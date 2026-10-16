# 📈 Stock Analyzer Pro

An AI-powered stock market analysis dashboard built using Python and Streamlit. The application helps users explore stock market data, analyze technical indicators, compare stocks, assess investment risk, and track their portfolio.

## 🚀 Features

- **Market Dashboard:** View stock prices and historical market trends.
- **Technical Analysis:** Analyze stocks using RSI, MACD, SMA, EMA, and Bollinger Bands.
- **Stock Comparison:** Compare historical performance of multiple stocks.
- **AI-Based Prediction:** Explore experimental stock-price forecasts using a Random Forest regression model.
- **Risk Analysis:** Review historical volatility, drawdown, and other risk metrics.
- **Portfolio Tracking:** Record trades and monitor portfolio holdings.
- **Watchlist:** Save and track selected stocks.
- **News Sentiment:** Analyze financial headlines using a basic sentiment-scoring approach.
- **User Authentication:** Register and log in using securely hashed passwords.
- **SQLite Database:** Store application users and relevant portfolio/watchlist data locally.

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend / Dashboard:** Streamlit
- **Data Analysis:** Pandas, NumPy
- **Financial Data:** yfinance
- **Machine Learning:** Scikit-learn
- **Visualization:** Plotly
- **Database:** SQLite
- **Testing:** Pytest

## 📂 Project Structure

```text
Stock-Analyzer-Pro/
├── app.py
├── analytics.py
├── db.py
├── market_data.py
├── sentiment.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── tests/
    └── test_analytics.py
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/Stock-Analyzer-Pro.git
cd Stock-Analyzer-Pro
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🧪 Run Tests

```bash
python -m pytest
```

## 📊 Learning Outcomes

This project demonstrates practical experience with:

- Python application development
- Financial data analysis and visualization
- Technical indicator calculations
- Introductory machine learning
- Database integration and user authentication
- Building interactive dashboards with Streamlit
- Software testing and project organization

## ⚠️ Disclaimer

This project is intended for educational and research purposes only. Stock-price predictions and sentiment scores are experimental and may be inaccurate. Historical performance does not guarantee future returns. This application does not provide financial advice.

## 👩‍💻 Author

**Anjali**
If you find this project useful, consider giving the repository a ⭐.
