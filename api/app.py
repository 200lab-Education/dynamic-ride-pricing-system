from flask import Flask, request, jsonify
import pandas as pd
import joblib
from datetime import datetime
import numpy as np

app = Flask(__name__)

# Tải mô hình và preprocessor
try:
    pricing_system = joblib.load("ride_pricing_system.pkl")
    print("Đã tải hệ thống định giá chuyến xe")
except:
    pricing_system = None
    print("Chưa tạo hệ thống định giá chuyến xe. Hãy chạy main.py trước.")

@app.route('/api/get-price', methods=['POST'])
def get_ride_price():
    """API endpoint để lấy giá chuyến xe"""
    if pricing_system is None:
        return jsonify({"error": "Hệ thống định giá chưa được khởi tạo"}), 500
    
    # Lấy dữ liệu từ request
    data = request.json
    
    # Chuẩn bị dữ liệu chuyến
    ride_data = pd.DataFrame({
        'ride_id': [data.get('ride_id', 'R000001')],
        'distance_km': [data.get('distance_km', 5.0)],
        'duration_min': [data.get('duration_min', 15)],
        'booking_time': [datetime.now()],
        'hour': [data.get('hour', datetime.now().hour)],
        'day_of_week': [datetime.now().weekday()],
        'is_weekend': [1 if datetime.now().weekday() >= 5 else 0],
        'month': [datetime.now().month],
        'weather_condition': [data.get('weather_condition', 0)],
        'traffic_level': [data.get('traffic_level', 3)],
        'available_drivers': [data.get('available_drivers', 10)],
        'area_demand': [data.get('area_demand', 50)],
        'vehicle_type': [data.get('vehicle_type', 1)],  # Mặc định xe 4 chỗ
        'user_rating': [data.get('user_rating', 4.5)],
        'user_previous_rides': [data.get('user_previous_rides', 5)],
        'base_price': [data.get('distance_km', 5.0) * 15000]  # Giá cơ bản ước tính
    })
    
    # Tính toán giá
    try:
        price_result = pricing_system.get_ride_price(ride_data)
        return jsonify({
            'ride_id': data.get('ride_id', 'R000001'),
            'optimal_price': price_result['optimal_price'],
            'base_price': price_result['base_price'],
            'price_percent_change': price_result['price_percent_change'],
            'insights': price_result['insights']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate-rides', methods=['GET'])
def simulate_rides():
    """API endpoint để giả lập nhiều chuyến xe"""
    if pricing_system is None:
        return jsonify({"error": "Hệ thống định giá chưa được khởi tạo"}), 500
    
    # Tạo dữ liệu mẫu
    from data.data_generator import generate_sample_ride_data
    
    n_rides = int(request.args.get('n_rides', 5))
    rides_df = generate_sample_ride_data(n_samples=n_rides)
    
    # Tính giá cho tất cả chuyến
    results = pricing_system.batch_price_rides(rides_df)
    
    # Trả về kết quả
    response = []
    for i, row in results.iterrows():
        ride_data = rides_df.iloc[i]
        vehicle_types = ["Xe máy", "Xe 4 chỗ", "Xe 7 chỗ", "Xe sang"]
        
        response.append({
            'ride_id': row['ride_id'],
            'distance_km': ride_data['distance_km'],
            'duration_min': ride_data['duration_min'],
            'vehicle_type': vehicle_types[ride_data['vehicle_type']],
            'base_price': row['base_price'],
            'optimal_price': row['optimal_price'],
            'price_percent_change': row['price_percent_change'],
            'insights': row['insights'][:2]  # Chỉ trả về 2 insights đầu tiên để gọn
        })
    
    return jsonify(response)

@app.route('/')
def index():
    return """
    <h1>API Hệ thống Đặt Xe Dynamic Pricing</h1>
    <p>Sử dụng các endpoint sau:</p>
    <ul>
        <li><code>/api/get-price</code> - POST - Lấy giá cho một chuyến xe</li>
        <li><code>/api/simulate-rides?n_rides=5</code> - GET - Giả lập nhiều chuyến xe</li>
    </ul>
    """

@app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint kiểm tra trạng thái hệ thống"""
    status = {
        'status': 'healthy',
        'pricing_system': 'loaded' if pricing_system is not None else 'not_loaded',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(status)

@app.route('/api/pricing-factors', methods=['GET'])
def pricing_factors():
    """API endpoint hiển thị các yếu tố ảnh hưởng đến giá"""
    factors = {
        'base_factors': [
            'Khoảng cách (km)',
            'Thời gian di chuyển ước tính (phút)',
            'Loại phương tiện (xe máy, xe 4 chỗ, xe 7 chỗ, xe sang)'
        ],
        'dynamic_factors': [
            'Tỷ lệ cung-cầu (số lượng tài xế có sẵn so với nhu cầu)',
            'Thời điểm trong ngày (giờ cao điểm)',
            'Ngày trong tuần (ngày thường/cuối tuần)',
            'Điều kiện thời tiết (tốt, mưa, mưa to)',
            'Tình trạng giao thông (mức độ tắc nghẽn 0-10)',
            'Lịch sử người dùng (số chuyến đi trước đây)',
            'Đánh giá người dùng (1-5 sao)'
        ],
        'special_conditions': [
            'Giảm giá 5% cho người dùng trung thành (>50 chuyến, đánh giá ≥4.5)',
            'Giảm giá 2% cho người dùng thường xuyên (>20 chuyến)',
            'Tăng giá tối đa 50% trong điều kiện cực kỳ cao điểm',
            'Tăng giá 10-20% trong điều kiện thời tiết xấu'
        ]
    }
    return jsonify(factors)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
