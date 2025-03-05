import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_ride_data(n_samples=1000, seed=42):
    """
    Tạo dữ liệu mẫu về chuyến xe cho mục đích huấn luyện mô hình
    
    Args:
        n_samples: Số lượng chuyến xe mẫu
        seed: Random seed để tái tạo
        
    Returns:
        DataFrame với dữ liệu chuyến xe
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Tạo ID cho chuyến xe
    ride_ids = [f"R{str(i).zfill(6)}" for i in range(n_samples)]
    
    # Tạo thời gian đặt xe ngẫu nhiên trong 30 ngày qua
    now = datetime.now()
    start_date = now - timedelta(days=30)
    booking_times = [start_date + timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    ) for _ in range(n_samples)]
    
    # Trích xuất các thuộc tính thời gian
    hours = [bt.hour for bt in booking_times]
    days_of_week = [bt.weekday() for bt in booking_times]
    is_weekend = [1 if dow >= 5 else 0 for dow in days_of_week]
    months = [bt.month for bt in booking_times]
    
    # Tạo dữ liệu không gian và chuyến đi
    distance_km = np.random.lognormal(mean=1.5, sigma=0.5, size=n_samples)
    distance_km = np.round(distance_km, 1)
    
    # Thời gian di chuyển (tỷ lệ với khoảng cách với chút biến thiên)
    avg_speed_kmh = 25  # Tốc độ trung bình 25km/h
    duration_min = np.round(distance_km / avg_speed_kmh * 60 * (1 + np.random.normal(0, 0.2, n_samples)))
    
    # Điều kiện thời tiết (0: tốt, 1: mưa, 2: mưa to)
    weather_condition = np.random.choice([0, 1, 2], size=n_samples, p=[0.7, 0.2, 0.1])
    
    # Mức độ tắc nghẽn giao thông (0-10)
    # Giờ cao điểm có mức tắc nghẽn cao hơn
    base_traffic = np.random.normal(3, 1, n_samples)
    peak_hour_effect = np.array([(3 if (h >= 7 and h <= 9) or (h >= 17 and h <= 19) else 0) 
                               for h in hours])
    traffic_level = np.clip(base_traffic + peak_hour_effect + np.random.normal(0, 1, n_samples), 0, 10)
    traffic_level = np.round(traffic_level).astype(int)
    
    # Số lượng tài xế có sẵn (thấp hơn vào giờ cao điểm)
    available_drivers = np.clip(
        np.random.normal(20, 5, n_samples) - peak_hour_effect/2, 1, 50).astype(int)
    
    # Nhu cầu khu vực (0-100)
    area_demand = np.clip(
        np.random.normal(50, 15, n_samples) + peak_hour_effect * 5, 0, 100).astype(int)
    
    # Loại xe (0: xe máy, 1: xe 4 chỗ, 2: xe 7 chỗ, 3: xe sang)
    vehicle_type = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.2, 0.6, 0.15, 0.05])
    
    # Thông tin người dùng
    user_rating = np.clip(np.random.normal(4.5, 0.5, n_samples), 1, 5)
    user_rating = np.round(user_rating, 1)
    user_previous_rides = np.clip(np.random.exponential(scale=20, size=n_samples), 0, 500).astype(int)
    
    # Tính giá cơ bản
    base_price_per_km = np.array([8000, 15000, 20000, 35000])[vehicle_type]  # Giá theo loại xe
    base_price = np.round(distance_km * base_price_per_km, -3)  # Làm tròn đến nghìn đồng
    
    # Tạo DataFrame
    rides_df = pd.DataFrame({
        'ride_id': ride_ids,
        'distance_km': distance_km,
        'duration_min': duration_min,
        'booking_time': booking_times,
        'hour': hours,
        'day_of_week': days_of_week,
        'is_weekend': is_weekend,
        'month': months,
        'weather_condition': weather_condition,
        'traffic_level': traffic_level,
        'available_drivers': available_drivers,
        'area_demand': area_demand,
        'vehicle_type': vehicle_type,
        'user_rating': user_rating,
        'user_previous_rides': user_previous_rides,
        'base_price': base_price
    })
    
    return rides_df

if __name__ == "__main__":
    # Test the function
    data = generate_sample_ride_data(n_samples=5)
    print(data.head())
