# IIoT Attack Classification with LightGBM

This project implements a machine learning pipeline for classifying Industrial Internet of Things (IIoT) attacks using the LightGBM gradient boosting framework. The system processes network traffic data to distinguish between benign traffic and various types of cyber attacks in industrial environments.

## 📋 Table of Contents

- [Features](#features)
- [Dataset](#dataset)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Model Architecture](#model-architecture)
- [Results](#results)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Multi-class Classification**: Distinguishes between benign traffic and multiple attack types
- **Time Window Analysis**: Supports classification across different time aggregations (1-10 seconds)
- **Robust Preprocessing**: Handles missing values, feature scaling, and skewness correction
- **Feature Engineering**: Automatic feature transformation and selection
- **Model Evaluation**: Comprehensive metrics including accuracy, precision, recall, and F1-score
- **Visualization**: Confusion matrices and feature importance plots
- **Dataset Integrity**: Built-in checksum verification for data integrity

## 📊 Dataset

The project uses the CIC IIoT Dataset 2025 (https://www.unb.ca/cic/datasets/iiot-dataset-2025.html), containing:

- **Benign Samples**: Normal industrial network traffic
- **Attack Samples**: Various cyber attack scenarios including:
  - DDoS attacks
  - Injection attacks
  - Man-in-the-middle attacks
  - And other industrial-specific threats

**Data Structure:**
- Time windows: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 seconds
- Features: Network packet statistics, protocol information, timing metrics
- Format: CSV files with labeled samples

## 🔧 Prerequisites

- Python 3.8+
- Required libraries:
  - pandas
  - numpy
  - scikit-learn
  - lightgbm
  - matplotlib
  - seaborn
  - pathlib

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd iiot-attack-classification
   ```

2. **Install dependencies:**
   ```bash
   pip install pandas numpy scikit-learn lightgbm matplotlib seaborn
   ```

3. **Extract the dataset:**
   ```bash
   python unpack-dataset.py
   ```
   This will extract the compressed data files and verify integrity using checksums.

## 📖 Usage

### Data Preparation

1. **Unpack Dataset:**
   ```bash
   python unpack-dataset.py
   ```

2. **Run the Jupyter Notebook:**
   Open `classification-iiot-attacks-lgbm.ipynb` in Jupyter Lab/Notebook and execute the cells sequentially.

### Key Steps in the Pipeline:

1. **Environment Setup**: Verify Python environment and library versions
2. **Data Loading**: Load and merge CSV files from different time windows
3. **Data Inspection**: Analyze dataset structure, missing values, and distributions
4. **Feature Engineering**: Apply transformations and handle skewness
5. **Preprocessing**: Scale features and prepare for training
6. **Model Training**: Train LightGBM classifier with optimized hyperparameters
7. **Evaluation**: Assess model performance with detailed metrics
8. **Visualization**: Generate confusion matrices and feature importance plots

### Running Individual Components:

```python
# Load and preprocess data
from pathlib import Path
import pandas as pd

# Load specific time window
data_path = Path("iiot-dataset-2025")
df = pd.read_csv(data_path / "attack_samples_1sec.csv")
```

## 🏗️ Model Architecture

### LightGBM Configuration:
- **Objective**: Multi-class classification
- **Boosting**: Gradient Boosting Decision Trees (GBDT)
- **Hyperparameters**:
  - Learning rate: 0.05
  - Number of leaves: 31
  - Feature fraction: 0.9
  - Bagging fraction: 0.8
  - Early stopping: 100 rounds

### Preprocessing Pipeline:
1. **Feature Selection**: Remove non-numeric columns except target
2. **Missing Value Handling**: Median imputation
3. **Feature Scaling**: Robust scaling (with centering disabled)
4. **Skewness Correction**: Log transformation for skewed features

## 📈 Results

### Performance Metrics:
- **Overall Accuracy**: ~95%+ (varies by time window)
- **Macro F1-Score**: High performance across all attack classes
- **Class-wise Performance**: Excellent detection of both benign and attack traffic

### Key Findings:
- Model performs well across different time windows
- Top features include network packet statistics and timing metrics
- Robust handling of class imbalance through internal LightGBM mechanisms

## 📁 Project Structure

```
├── classification-iiot-attacks-lgbm.ipynb  # Main analysis notebook
├── unpack-dataset.py                      # Dataset extraction script
├── README.md                             # Project documentation
├── attack_data/                          # Compressed attack samples
│   ├── *.tar.xz                         # Compressed CSV files
│   └── checksums/                       # SHA256 checksums
├── benign_data/                         # Compressed benign samples
│   ├── *.tar.xz                         # Compressed CSV files
│   └── checksums/                       # SHA256 checksums
└── iiot-dataset-2025/                   # Extracted dataset
    ├── attack_samples_*.csv             # Attack data by time window
    └── benign_samples_*.csv             # Benign data by time window
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- IIoT Dataset 2025 providers
- LightGBM development team
- Open source community for machine learning libraries

## 📞 Contact

For questions or issues, please open an issue in the repository or contact the maintainers.

---

**Note**: This project is for research and educational purposes. Ensure compliance with data usage policies and ethical guidelines when applying to real-world industrial systems.

