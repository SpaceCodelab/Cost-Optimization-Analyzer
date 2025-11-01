<h1 align="center">☁️ AWS Cost Optimization Analyzer 🚀</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-App-red?logo=streamlit" alt="Streamlit App"/>
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/ML-Anomaly%20Detection-green?logo=scikitlearn" alt="Machine Learning"/>
  <img src="https://img.shields.io/badge/Status-Stable-success" alt="Stable"/>
</p>

<p align="center">
  <strong>AI-Powered Cloud Cost Intelligence for AWS 💸</strong><br>
  <em>Predictive, Insightful, and Beautifully Visualized.</em>
</p>

---

## 🌍 Live Demo

👉 **Try it now:** [https://cost-optimization-analyzer.streamlit.app/](https://cost-optimization-analyzer.streamlit.app/)

---

## 💡 Overview

**CloudPulse AI** is an advanced **Streamlit-based analytics dashboard** that helps cloud teams understand, forecast, and optimize AWS spending using AI and data visualization.

It leverages:
- 🧠 **Machine Learning (Isolation Forest)** for anomaly detection  
- 💹 **Linear Regression** for forecasting and trend analysis  
- 💰 **AI-driven Recommendations** to identify potential savings  
- 📊 **Interactive Visualizations** powered by Plotly and Matplotlib  
- 📄 **One-click PDF Report Generation** for decision-makers  

---

## 🧠 Key Features

| Feature | Description |
|----------|-------------|
| 💵 **AWS Cost Analysis** | Automatically parses your AWS billing CSV and visualizes daily, regional, and service-level spend |
| 🔍 **Anomaly Detection** | Detects unusual cost spikes using ML (Isolation Forest) |
| 📈 **Forecasting Engine** | Predicts next 30-day spend trends per service |
| 🤖 **AI Recommendations** | Identifies high-ROI cost-saving opportunities |
| 🎨 **Interactive Dashboards** | Built with Plotly, Streamlit, and responsive layouts |
| 🧾 **PDF Export** | Generates professional PDF cost reports automatically |

---

## 🧰 Tech Stack

- **Frontend / UI:** [Streamlit](https://streamlit.io)  
- **Data Processing:** Pandas, NumPy  
- **Visualization:** Plotly, Matplotlib  
- **Machine Learning:** scikit-learn  
- **Reporting:** fpdf2, ReportLab  
- **Language:** Python 3.12  

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/SpaceCodelab/Cost-Optimization-Analyzer.git
cd Cost-Optimization-Analyzer

# Create and activate virtual environment (recommended)
python -m venv env
env\Scripts\activate        # Windows
# or
source env/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/main.py

## 📂 Project Structure

Cost-Optimization-Analyzer/
│
├── app/
│   ├── main.py                # Streamlit dashboard
│   └── logo.svg               # Optional app logo
│
├── data/
│   └── sample_aws.csv         # Sample AWS billing data
│
├── tests/
│   └── test_func.py            # Unit tests
    └── conftest.py           
│
├── requirements.txt           # Dependencies
├── runtime.txt                # Python version
├── README.md                  # This file
└── .streamlit/
    └── config.toml (optional) # Theme or secrets config
