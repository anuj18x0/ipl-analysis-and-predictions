# 🏏 IPL Analytics and Predictions

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

A comprehensive IPL data analytics and prediction platform built with Streamlit and machine learning.

## ⚡ Quick Start

**Try it instantly:**
```bash
docker-compose up --build
# Visit http://localhost:8501
```

**Or deploy to cloud** - see deployment options below! ☁️

## 📊 Dataset

The dataset used in this project consists of two CSV files: `matches_2008-2024.csv` and `deliveries_2008-2024.csv`. These files contain detailed information on match summaries and ball-by-ball data.

- **[IPL Complete Dataset (2008-2024)](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)**

## 📁 Project Structure

```
ipl-analytics-main/
├── 📂 src/                          # Source code
│   ├── 📂 pages/                    # Streamlit pages
│   │   ├── homePage.py              # Home page with IPL overview
│   │   ├── exploratoryDataAnalysis.py # EDA and data insights
│   │   ├── teamAnalysis.py          # Team performance analysis
│   │   ├── team_vs_teamAnalysis.py  # Head-to-head team comparisons
│   │   ├── playerAnalysis.py        # Individual player statistics
│   │   ├── batter_vs_bowlerAnalysis.py # Batter vs bowler matchups
│   │   └── matches.py               # Match scorecards
│   ├── 📂 predictions/              # ML prediction modules
│   │   ├── scorePrediction.py       # First innings score prediction
│   │   └── winnerPrediction.py      # Match winner probability prediction
│   ├── 📂 analysis/                 # Data analysis utilities
│   │   └── datasetPreprocessing.py  # Data cleaning and preprocessing
│   └── 📂 utils/                    # Utility functions
│       └── scrollToTop.py           # UI utility functions
├── 📂 notebooks/                    # Jupyter notebooks for experimentation
│   ├── scorePridiction.ipynb        # Score prediction model development
│   └── scorePridictionDataset.ipynb # Dataset exploration
├── 📂 scripts/                      # Training and utility scripts
│   ├── winner_model_train.py        # Train winner prediction model
│   ├── download_large_files.py      # Google Drive file downloader
│   └── setup_git_lfs.txt            # Git LFS setup instructions
├── 📂 Datasets/                     # Data files
│   ├── matches_2008-2024.csv        # Match-level data (1.5MB)
│   └── deliveries_2008-2024.csv     # Ball-by-ball data (68MB - Google Drive)
├── 📂 Model/                        # Saved ML models
│   ├── winner_prediction_model.pkl  # Winner prediction model (small)
│   └── predict_ipl_score_best_rf.pkl # Score model (2GB - Google Drive)
├── 📂 Images/                       # Static images and assets
│   ├── CricketFever.gif
│   ├── divider.png
│   ├── Welcome.gif
│   └── Wicket.gif
├── 📂 iplenv/                       # Python virtual environment
├── app.py                           # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── DEPLOYMENT.md                    # Deployment guide
├── Dockerfile                       # Docker container configuration
├── docker-compose.yml              # Docker Compose setup
├── .dockerignore                    # Docker ignore rules
├── docker-manage.bat               # Docker management script (Windows)
├── docker-manage.sh                # Docker management script (Linux/Mac)
└── README.md                        # This file
```

## 🚀 Getting Started

### Option 1: Docker (Recommended) 🐳

#### Prerequisites
- Docker Desktop installed

#### Quick Setup
```bash
# Clone the repository
git clone https://github.com/anuj18x0/ipl-analysis-and-predictions.git
cd ipl-analysis-and-predictions

# Download large files (required for full functionality)
python scripts/download_large_files.py

# Run with Docker
docker-compose up --build

# Visit http://localhost:8501
```

#### What Gets Downloaded
The app needs 2 large files that are stored on Google Drive:
- **deliveries_2008-2024.csv** (68MB) - Ball-by-ball data
- **predict_ipl_score_best_rf.pkl** (2GB) - Score prediction model

These download automatically when you run the script or deploy to cloud platforms.

### Option 2: Local Development

#### Prerequisites
- Python 3.9+

#### Installation
```bash
# Clone repository
git clone https://github.com/anuj18x0/ipl-analysis-and-predictions.git
cd ipl-analysis-and-predictions

# Install dependencies
pip install -r requirements.txt

# Download large files
python scripts/download_large_files.py

# Run application
streamlit run app.py
```

### Option 3: Cloud Deployment ☁️

#### Streamlit Cloud (Free)
1. Fork this repository
2. Deploy on [share.streamlit.io](https://share.streamlit.io)
3. Large files download automatically during deployment!

## 🎯 Features

### 📊 Analysis Pages
- **Home**: IPL overview and tournament information
- **Exploratory Data Analysis**: Data insights and visualizations
- **Team Analysis**: Individual team performance metrics
- **Team vs Team**: Head-to-head comparisons between teams
- **Player Analysis**: Individual player statistics and performance
- **Batter vs Bowler**: Specific matchup analysis
- **Match Scorecard**: Detailed match information

### 🤖 Prediction Models
- **Score Prediction**: Predict first innings total score (84%+ accuracy)
- **Winner Prediction**: Predict match winner with probability (84% accuracy)

### 📈 Model Features
The winner prediction model uses 14 key parameters:
- Team matchups and historical performance
- Venue and home advantage
- Toss winner and decision
- Head-to-head records
- Batting/bowling first statistics
- Recent season trends

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **ML**: Scikit-learn (Random Forest)
- **Data**: Pandas, NumPy  
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Deployment**: Docker + Google Drive integration
- **Dataset**: IPL 2008-2024 (260K+ deliveries, 1K+ matches)

## 🔧 Development

### Training New Models
```bash
# Train winner prediction model
python scripts/winner_model_train.py
```

### Download Large Files Manually
If automatic download doesn't work:
```bash
# Run the download script manually
python scripts/download_large_files.py

# Check if files downloaded correctly
ls -la Datasets/deliveries_2008-2024.csv
ls -la Model/predict_ipl_score_best_rf.pkl
```

### Troubleshooting
- **Missing large files?** Run `python scripts/download_large_files.py`
- **Import errors?** Check that you're in the project directory
- **Docker issues?** Make sure Docker Desktop is running

### Project Organization
The project follows a clean structure with source code organized by functionality.

## 📋 Data Sources
- **[IPL Complete Dataset (2008-2024)](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)** - Kaggle
- **Match data**: 1,000+ matches from 2008-2024
- **Ball-by-ball data**: 260,000+ deliveries with detailed statistics

## 🎉 Model Performance
- **Score Prediction**: Achieves high accuracy in predicting first innings totals
- **Winner Prediction**: 84% accuracy using comprehensive feature engineering

## 🌟 Key Features
- ⚡ **Instant Deployment** - Docker & cloud-ready
- 🤖 **84% ML Accuracy** - Advanced prediction models  
- 📊 **Interactive Dashboard** - Beautiful Streamlit interface
- 🏏 **16+ Years Data** - Comprehensive IPL analysis (2008-2024)
- 🐳 **Smart File Handling** - Google Drive integration for large files

## 📞 Contact & Contributing

Found this project helpful? ⭐ **Star this repository!**

**Connect with me:**
- GitHub: [@anuj18x0](https://github.com/anuj18x0)
- LinkedIn: [Arth Arvind](https://linkedin.com/in/arth-arvind)
- Email: artharvind18@gmail.com

**Contributions welcome!** Feel free to:
- 🐛 Report bugs
- 💡 Suggest features  
- 🔧 Submit pull requests
- 📖 Improve documentation

---
*Built with ❤️ for cricket analytics enthusiasts*
