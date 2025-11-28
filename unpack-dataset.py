#!/usr/bin/env python3
import argparse
import os
import lzma
import sys
import hashlib
import tarfile
from pathlib import Path

RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"

def sha256_file(path, bufsize=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def read_expected_sha256(sha256_path):
    """
    Supports common formats like:
      <hash>  filename
      <hash> *filename
      <hash>
    Returns the hex digest (str) or None if unreadable.
    """
    try:
        text = Path(sha256_path).read_text(errors="ignore").strip()
        if not text:
            return None
        first_line = text.splitlines()[0].strip()
        token = first_line.split()[0]
        token = token.strip()
        token = "".join(c for c in token if c.lower() in "0123456789abcdef")
        return token if len(token) == 64 else None
    except Exception:
        return None

def is_within_directory(directory, target):
    """Prevent path traversal on extraction."""
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

def safe_extract(tar: tarfile.TarFile, path: str):
    for member in tar.getmembers():
        target_path = os.path.join(path, member.name)
        if not is_within_directory(path, target_path):
            raise Exception(f"Blocked path traversal attempt: {member.name}")
    tar.extractall(path)

def extract_tar_xz(archive_path: Path, dest_dir: Path):
    """
    Extract a .tar.xz file, supporting nested tar archives or raw xz decompression.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(archive_path, mode="r:xz") as tf:
            for m in tf.getmembers():
                target = dest_dir / m.name
                if not str(target.resolve()).startswith(str(dest_dir.resolve()) + os.sep):
                    raise Exception(f"Blocked path traversal attempt: {m.name}")
            tf.extractall(dest_dir)
            return "tarxz"
    except tarfile.ReadError:
        pass

    out_name = archive_path.name
    if out_name.endswith(".xz"):
        out_name = out_name[:-3]
    if out_name.endswith(".tar"):
        out_name = out_name[:-4]

    raw_out = dest_dir / out_name
    with lzma.open(archive_path, "rb") as fin, open(raw_out, "wb") as fout:
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
    return "rawxz"

def process_top_level(archive_path: Path, dest_dir: Path, checksum_dir: Path = None):
    """
    Extract the top-level .tar.xz file with optional checksum verification.
    """
    arc_name = archive_path.name
    has_checksums = checksum_dir is not None and checksum_dir.is_dir()

    if has_checksums:
        sha_file = checksum_dir / f"{arc_name}.sha256"
        if not sha_file.exists():
            print(f"{YELLOW}[{arc_name}] checksum file missing: {sha_file.name}  â†’ extract unconditionally{RESET}")
            has_checksums = False
        else:
            expected = read_expected_sha256(sha_file)
            if not expected:
                print(f"[{arc_name}] invalid checksum file format: {sha_file.name}  â†’ extract unconditionally")
                has_checksums = False
            else:
                actual = sha256_file(archive_path)
                if actual.lower() != expected.lower():
                    print(f"{RED}[{arc_name}] checksum FAILED (expected {expected}, got {actual})  â†’ SKIP{RESET}")
                    return 0
                print(f"{GREEN}[{arc_name}] checksum passed{RESET}")

    try:
        kind = extract_tar_xz(archive_path, dest_dir)
        if kind == "tarxz":
            print(f"{GREEN}[{arc_name}]{RESET} extracted (tar.xz) to {dest_dir}")
        else:
            print(f"{GREEN}[{arc_name}]{RESET} decompressed raw .xz â†’ {dest_dir}")
        return 1
    except Exception as e:
        print(f"{RED}[{arc_name}] extract error: {e}  â†’ SKIP{RESET}")
        return 0

def process_subdir(src_dir: Path, dest_dir: Path, extracted_dest_dir: Path):
    """
    Process a subdirectory (e.g., attack_data or benign_data) with nested .tar.xz files,
    extracting contents to a separate folder.
    """
    checksum_dir = src_dir / "checksums"
    has_checksums = checksum_dir.is_dir()

    if not has_checksums:
        print(f"{YELLOW}No checksum dir found in {src_dir} â†’ extract unconditionally{RESET}")

    archives = sorted(src_dir.glob("*.tar.xz"))
    if not archives:
        print(f"{YELLOW}No .tar.xz files found in {src_dir}{RESET}")
        return 0

    total = 0
    ok = 0
    for arc in archives:
        total += 1
        arc_name = arc.name
        out_subdir = extracted_dest_dir  # Extract to a separate folder

        if has_checksums:
            sha_file = checksum_dir / f"{arc_name}.sha256"
            if not sha_file.exists():
                print(f"{YELLOW}[{arc_name}] checksum file missing: {sha_file.name}  â†’ SKIP{RESET}")
                continue
            expected = read_expected_sha256(sha_file)
            if not expected:
                print(f"[{arc_name}] invalid checksum file format: {sha_file.name}  â†’ SKIP")
                continue
            actual = sha256_file(arc)
            if actual.lower() != expected.lower():
                print(f"{RED}[{arc_name}] checksum FAILED (expected {expected}, got {actual})  â†’ SKIP{RESET}")
                continue
            print(f"{GREEN}[{arc_name}] checksum passed{RESET}")
            try:
                kind = extract_tar_xz(arc, out_subdir)
                if kind == "tarxz":
                    print(f"{GREEN}[{arc_name}]{RESET} extracted (tar.xz) to {out_subdir}")
                else:
                    print(f"{GREEN}[{arc_name}]{RESET} decompressed raw .xz â†’ {out_subdir}")
                ok += 1
            except Exception as e:
                print(f"{RED}[{arc_name}] extract error: {e}  â†’ SKIP{RESET}")
        else:
            try:
                extract_tar_xz(arc, out_subdir)
                print(f"{GREEN}[{arc_name}]{RESET} extracted to {out_subdir}")
                ok += 1
            except Exception as e:
                print(f"{RED}[{arc_name}] extract error: {e}  â†’ SKIP{RESET}")

    print(f"{GREEN}\nDone processing {src_dir.name}. Extracted {ok}/{total} archives.{RESET}")
    return ok

def process(src_dir: Path, dest_dir: Path, top_level_archive_name: str = "all_attack_benign_samples.tar.xz"):
    """
    Process the top-level archive and then its subdirectories (attack_data, benign_data),
    extracting nested files to separate folders.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Extract the top-level archive
    top_level_archive = src_dir / top_level_archive_name
    if top_level_archive.exists():
        checksum_dir = None  # If there's a top-level checksums folder, set it to src_dir / "checksums"
        if process_top_level(top_level_archive, dest_dir, checksum_dir) == 1:
            extracted_src = dest_dir
        else:
            return 1  # Error in top-level extraction
    else:
        print(f"{RED}Top-level archive {top_level_archive_name} not found in {src_dir}{RESET}")
        return 1

    # Process attack_data subdirectory, extract to extracted_attack_data
    attack_data_dir = extracted_src / "attack_data"
    if attack_data_dir.is_dir():
        extracted_attack_dir = dest_dir / "extracted_attack_data"
        process_subdir(attack_data_dir, attack_data_dir, extracted_attack_dir)

    # Process benign_data subdirectory, extract to extracted_benign_data
    benign_data_dir = extracted_src / "benign_data"
    if benign_data_dir.is_dir():
        extracted_benign_dir = dest_dir / "extracted_benign_data"
        process_subdir(benign_data_dir, benign_data_dir, extracted_benign_dir)

    return 0

def main():
    ap = argparse.ArgumentParser(description="Extract top-level .tar.xz and nested archives with checksums to separate folders.")
    ap.add_argument("src_dir", help="Directory containing the top-level all_attack_benign_samples.tar.xz")
    ap.add_argument("dest_dir", nargs="?", default=None,
                    help="Destination directory (defaults to src_dir)")
    args = ap.parse_args()

    src = Path(os.path.expanduser(args.src_dir)).resolve()
    if not src.is_dir():
        print(f"{RED}Error: src_dir is not a directory: {src}{RESET}", file=sys.stderr)
        sys.exit(2)

    dest = Path(os.path.expanduser(args.dest_dir)).resolve() if args.dest_dir else src
    dest.mkdir(parents=True, exist_ok=True)

    sys.exit(process(src, dest))

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        main()
    else:
        # === CONFIGS FOR IDE RUN ===
        src_dir = "C:\\Users\\kheir\\Downloads"  # Directory with top-level .tar.xz
        dest_dir = "C:\\Users\\kheir\\OneDrive\\Desktop\\Dataset"  # Destination for extraction

        from pathlib import Path

        src = Path(src_dir).expanduser().resolve()
        dest = Path(dest_dir).expanduser().resolve() if dest_dir else src

        process(src, dest)