# Dynamic Ride Pricing System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-2.0+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/) [![Machine Learning](https://img.shields.io/badge/ML-Gradient_Boosting-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

> Dynamic Pricing System for ride-hailing applications, using Machine Learning and multiple real-world factors to optimize ride prices in real-time.

## 📋 Overview

The system uses machine learning models to predict base prices based on ride characteristics and then applies dynamic (real-time) adjustments based on supply-demand, weather, time of day, user history, and many other factors.

**Key Features:**

- ✨ **Smart Pricing**: Base price prediction based on distance, time, vehicle type
- 🌦️ **Real-time Factors**: Price adjustments based on weather, traffic congestion, supply-demand
- 🚀 **API Integration**: RESTful API for real-world applications
- 📊 **Analytics**: Visual dashboard for analysis and simulation

## 🛠️ Installation

<details>
<summary>Click to expand installation steps</summary>

1. Clone repository:

```bash
git clone https://github.com/yourusername/dynamic-ride-pricing.git
cd dynamic-ride-pricing
```

2. Install libraries:

```bash
pip install -r requirements.txt
```

3. Train the model:

```bash
python main.py
```

4. Run API server:

```bash
python -m api.app
```

5. Run dashboard:

```bash
streamlit run dashboard/app.py
```

</details>

## 🖥️ Usage

### 🔌 API

API runs at `http://localhost:5001/api` with the following endpoints:

| Endpoint           | Method | Description                                    |
| ------------------ | ------ | ---------------------------------------------- |
| `/health`          | GET    | Check operational status                       |
| `/get-price`       | POST   | Calculate ride price based on parameters       |
| `/simulate-rides`  | GET    | Simulate multiple rides with random parameters |
| `/pricing-factors` | GET    | View factors affecting price                   |

### 📈 Dashboard

The Streamlit dashboard provides:

1. **Multiple Ride Simulation**:

   - 🚕 Create multiple random rides
   - 📊 Analyze and visualize results

2. **Parameter-based Simulation**:
   - 🎛️ Manually adjust ride parameters
   - 🔍 View detailed pricing analysis

## 📂 Project Structure

<details>
<summary>Click to expand project structure</summary>

```
dynamic-pricing/
│
├── api/                        # API server module
│   ├── __init__.py
│   └── app.py                  # Flask API server
│
├── dashboard/                  # Streamlit Dashboard
│   └── app.py                  # Dashboard application
│
├── data/                       # Data processing module
│   ├── __init__.py
│   ├── data_generator.py       # Sample data generator
│   └── preprocessor.py         # Data preprocessing
│
├── models/                     # ML model module
│   ├── __init__.py
│   └── pricing_model.py        # Price prediction model
│
├── pricing/                    # Dynamic Pricing module
│   ├── __init__.py
│   └── dynamic_pricer.py       # Dynamic pricing algorithm
│
├── utils/                      # Utilities
│   ├── __init__.py
│   └── geo_utils.py            # Geographic/distance utilities
│
├── main.py                     # Main execution file
├── requirements.txt            # Required libraries
└── README.md                   # This file
```

</details>

## 💼 Dynamic Pricing Mechanism

The system uses a 2-step process to determine prices:

### 1️⃣ Base Price Prediction

> Uses Gradient Boosting model to predict price from distance, time, vehicle type. Result is the base price for the ride.

### 2️⃣ Dynamic Price Adjustments

| Factor                  | Description                                                | Impact |
| ----------------------- | ---------------------------------------------------------- | ------ |
| 🚗 **Supply-Demand**    | Adjusts price based on driver availability and area demand | ±15%   |
| 🌧️ **Weather**          | Increases price during adverse weather conditions          | +5-10% |
| 🚦 **Congestion**       | Adjusts price according to traffic congestion levels       | +3-12% |
| 🏆 **Customer Loyalty** | Discounts for loyal users                                  | -5-15% |

## 📊 Example Results

<details open>
<summary>Example results from the pricing system for a 5km ride:</summary>

```
- Base price: 75,000 VND
- Optimized price: 82,500 VND
- Price change %: +10.0%

Insights:
- Price increased by 10.0% compared to base price due to high demand during peak hours
- Area has low supply-demand ratio (8 drivers/45 requests)
- Weather conditions (rain) increased price by 5%
```

</details>

## 🔧 System Requirements

- 🐍 Python 3.9+
- 💾 4GB RAM (recommended)
- 💽 50MB disk space

## 📄 License

[MIT License](LICENSE)

---

<details>
<summary>Repository Setup Instructions</summary>

Place this README.md file in the root directory of the project (same level as main.py).

To add this file to the repository, do the following:

1. Create a file named `README.md` in the root directory of the project
2. Copy the above content into the file
3. Save the file and add it to the git repository:

```bash
git add README.md
git commit -m "Add project README"
git push
```

</details>

```

```
