import unittest
import numpy as np
import pandas as pd
from analytics import add_indicators, calculate_risk, predict_next_close

class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        idx = pd.date_range("2023-01-01", periods=260, freq="B")
        close = pd.Series(100 + np.cumsum(np.random.default_rng(7).normal(0.1, 1, len(idx))), index=idx)
        self.df = pd.DataFrame({
            "Open": close * 0.999,
            "High": close * 1.01,
            "Low": close * 0.99,
            "Close": close,
            "Volume": 100000
        }, index=idx)

    def test_indicators_exist(self):
        result = add_indicators(self.df)
        self.assertIn("RSI", result.columns)
        self.assertIn("MACD", result.columns)
        self.assertIn("BB_upper", result.columns)

    def test_risk_metrics(self):
        result = calculate_risk(self.df)
        self.assertIn("volatility", result)
        self.assertIn("max_drawdown", result)

    def test_prediction(self):
        result = predict_next_close(self.df)
        self.assertIn("prediction", result)
        self.assertGreater(result["prediction"], 0)

if __name__ == "__main__":
    unittest.main()
