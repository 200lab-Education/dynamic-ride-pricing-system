import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

from data.data_generator import generate_sample_ride_data
from data.preprocessor import RideDataPreprocessor
from models.pricing_model import RidePricingModel
from pricing.dynamic_pricer import DynamicRidePricingSystem

def train_model():
    """
    Tạo dữ liệu, huấn luyện mô hình và lưu hệ thống định giá
    """
    print("===== Xây dựng hệ thống Dynamic Pricing cho ứng dụng đặt xe =====")
    
    # Bước 1: Tạo dữ liệu mẫu
    print("1. Tạo dữ liệu mẫu...")
    n_samples = 10000
    data = generate_sample_ride_data(n_samples=n_samples)
    print(f"Đã tạo {n_samples} chuyến xe mẫu")
    
    # Chia tập huấn luyện và kiểm thử
    X = data.drop(['ride_id', 'booking_time', 'base_price'], axis=1)
    y = data['base_price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Kích thước tập huấn luyện: {X_train.shape[0]} chuyến")
    print(f"Kích thước tập kiểm thử: {X_test.shape[0]} chuyến")
    
    # Bước 2: Tiền xử lý dữ liệu
    print("2. Tiền xử lý dữ liệu...")
    preprocessor = RideDataPreprocessor()
    preprocessor.fit(X_train)
    
    X_train_processed = preprocessor.transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    print(f"Số lượng đặc trưng sau khi tiền xử lý: {X_train_processed.shape[1]}")
    
    # Bước 3: Huấn luyện mô hình
    print("3. Huấn luyện mô hình dự đoán giá...")
    model = RidePricingModel()
    model.fit(X_train_processed, y_train)
    
    # Đánh giá mô hình
    train_metrics = model.evaluate(X_train_processed, y_train)
    test_metrics = model.evaluate(X_test_processed, y_test)
    
    print(f"Kết quả trên tập huấn luyện:")
    print(f"  - MAE: {train_metrics['mae']:,.0f} đồng")
    print(f"  - MAPE: {train_metrics['mape']:.2f}%")
    print(f"  - R²: {train_metrics['r2']:.4f}")
    
    print(f"Kết quả trên tập kiểm thử:")
    print(f"  - MAE: {test_metrics['mae']:,.0f} đồng")
    print(f"  - MAPE: {test_metrics['mape']:.2f}%")
    print(f"  - R²: {test_metrics['r2']:.4f}")
    
    # Hiển thị tầm quan trọng của đặc trưng
    feature_imp = model.get_feature_importance()
    print("Tầm quan trọng của các đặc trưng hàng đầu:")
    for i, (feature, importance) in enumerate(zip(feature_imp['feature'][:5], feature_imp['importance'][:5])):
        print(f"{i+1}. {feature}: {importance:.4f}")
    
    # Bước 4: Khởi tạo hệ thống Dynamic Pricing
    print("4. Khởi tạo hệ thống Dynamic Pricing...")
    pricing_system = DynamicRidePricingSystem(model, preprocessor)
    
    # Lưu hệ thống định giá
    joblib.dump(pricing_system, "ride_pricing_system.pkl")
    print("Đã lưu hệ thống định giá vào 'ride_pricing_system.pkl'")
    
    # Bước 5: Demo thử nghiệm
    print("5. Thử nghiệm hệ thống với một số chuyến xe mẫu...")
    test_rides = generate_sample_ride_data(n_samples=5)
    print("Chuyến 1:")
    
    # In thông tin chi tiết cho chuyến đầu tiên
    first_ride = test_rides.iloc[[0]]
    print(f"- Loại xe: {['Xe máy', 'Xe 4 chỗ', 'Xe 7 chỗ', 'Xe sang'][first_ride['vehicle_type'].values[0]]}")
    print(f"- Khoảng cách: {first_ride['distance_km'].values[0]:.1f} km")
    print(f"- Thời gian: {first_ride['duration_min'].values[0]:.0f} phút")
    print(f"- Điều kiện thời tiết: {['Tốt', 'Mưa', 'Mưa to'][first_ride['weather_condition'].values[0]]}")
    print(f"- Tắc nghẽn giao thông: {first_ride['traffic_level'].values[0]}/10")
    print(f"- Tỷ lệ cung-cầu: {first_ride['available_drivers'].values[0]} tài xế / {first_ride['area_demand'].values[0]} nhu cầu")
    
    # Tính giá
    price_result = pricing_system.get_ride_price(first_ride)
    
    print(f"Kết quả tính giá:")
    print(f"- Giá cơ bản: {price_result['base_price']:,.0f} đồng")
    print(f"- Giá tối ưu: {price_result['optimal_price']:,.0f} đồng")
    print(f"- % thay đổi giá: {price_result['price_percent_change']:.1f}%")
    
    print("Insights:")
    for insight in price_result['insights']:
        print(f"- {insight}")
    
    # Kết thúc
    print("===== Xây dựng hệ thống thành công =====")
    print("Để chạy API server, thực thi: python -m api.app")
    print("Để chạy dashboard, thực thi: streamlit run dashboard/app.py")

def test_api():
    """
    Kiểm thử API endpoints
    """
    import requests
    from requests.exceptions import ConnectionError
    
    print("===== Kiểm thử API =====")
    
    base_url = "http://localhost:5000/api"
    
    try:
        # Kiểm tra health
        print("Kiểm tra API health...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("Health check OK:", response.json())
        else:
            print(f"Lỗi: {response.status_code}")
        
        # Thử tính giá
        print("Thử tính giá 1 chuyến...")
        test_ride = {
            "distance_km": 5.0,
            "duration_min": 15,
            "weather_condition": 0,
            "traffic_level": 3,
            "available_drivers": 10,
            "area_demand": 50,
            "vehicle_type": 1,
            "user_rating": 4.5,
            "user_previous_rides": 5
        }
        
        response = requests.post(f"{base_url}/get-price", json=test_ride)
        if response.status_code == 200:
            result = response.json()
            print(f"Giá cơ bản: {result['base_price']:,.0f} đồng")
            print(f"Giá tối ưu: {result['optimal_price']:,.0f} đồng")
            print(f"% thay đổi giá: {result['price_percent_change']:.1f}%")
        else:
            print(f"Lỗi: {response.status_code}")
        
        # Thử giả lập chuyến
        print("Thử giả lập 3 chuyến...")
        response = requests.get(f"{base_url}/simulate-rides?n_rides=3")
        if response.status_code == 200:
            results = response.json()
            print(f"Nhận được {len(results)} kết quả")
            for i, ride in enumerate(results):
                print(f"Chuyến {i+1}: {ride['ride_id']} - {ride['optimal_price']:,.0f} đồng")
        else:
            print(f"Lỗi: {response.status_code}")
        
    except ConnectionError:
        print("Không thể kết nối đến API server. Hãy chắc chắn server đang chạy.")
    
    print("===== Kết thúc kiểm thử API =====")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dynamic Ride Pricing System')
    parser.add_argument('--action', type=str, default='train', 
                        choices=['train', 'test_api'],
                        help='Hành động để thực hiện (train|test_api)')
    
    args = parser.parse_args()
    
    if args.action == 'train':
        train_model()
    elif args.action == 'test_api':
        test_api()
