import numpy as np
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa hai điểm trên trái đất bằng công thức haversine
    
    Args:
        lat1, lon1: Vĩ độ, kinh độ của điểm 1 (đơn vị: độ)
        lat2, lon2: Vĩ độ, kinh độ của điểm 2 (đơn vị: độ)
        
    Returns:
        Khoảng cách theo km
    """
    # Chuyển độ sang radian
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Công thức haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Bán kính trái đất (km)
    
    return c * r

def estimate_travel_time(distance_km, traffic_level=3, weather_condition=0):
    """
    Ước tính thời gian di chuyển dựa trên khoảng cách, tắc nghẽn và thời tiết
    
    Args:
        distance_km: Khoảng cách (km)
        traffic_level: Mức độ tắc nghẽn (0-10)
        weather_condition: Điều kiện thời tiết (0: tốt, 1: mưa, 2: mưa to)
        
    Returns:
        Thời gian di chuyển ước tính (phút)
    """
    # Tốc độ cơ bản (km/h)
    base_speed = 30
    
    # Điều chỉnh tốc độ theo tắc nghẽn
    speed_multiplier = 1 - (traffic_level / 15)  # Giảm tối đa 2/3 tốc độ
    
    # Điều chỉnh tốc độ theo thời tiết
    if weather_condition == 1:  # Mưa
        speed_multiplier *= 0.9
    elif weather_condition == 2:  # Mưa to
        speed_multiplier *= 0.8
    
    # Tốc độ cuối cùng
    speed = base_speed * max(0.3, speed_multiplier)  # Tốc độ tối thiểu 9 km/h
    
    # Thời gian di chuyển (phút)
    travel_time = (distance_km / speed) * 60
    
    # Thêm chút biến thiên ngẫu nhiên
    travel_time *= 1 + np.random.normal(0, 0.1)
    
    return max(5, round(travel_time))  # Tối thiểu 5 phút
