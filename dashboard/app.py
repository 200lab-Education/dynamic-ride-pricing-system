import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
from datetime import datetime
import time

# Cấu hình trang
st.set_page_config(
    page_title="Dynamic Ride Pricing Dashboard",
    page_icon="🚕",
    layout="wide"
)

# Tiêu đề
st.title("🚕 Dashboard Dynamic Pricing cho Ứng dụng Đặt Xe")

# Kết nối tới API
API_URL = "http://localhost:5001/api"

def get_health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.json()
    except:
        return {"status": "error", "pricing_system": "not_connected"}

def get_pricing_factors():
    try:
        response = requests.get(f"{API_URL}/pricing-factors")
        return response.json()
    except:
        return {}

def simulate_rides(n_rides=5):
    try:
        response = requests.get(f"{API_URL}/simulate-rides", params={"n_rides": n_rides})
        return response.json()
    except:
        return []

def get_price(ride_params):
    try:
        response = requests.post(f"{API_URL}/get-price", json=ride_params)
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi gọi API: {str(e)}")
        return {"error": str(e)}

# Kiểm tra kết nối
health = get_health()
if health["status"] == "healthy":
    st.sidebar.success("✅ Kết nối đến API thành công")
else:
    st.sidebar.error("❌ Không thể kết nối đến API. Hãy chắc chắn server đang chạy.")
    st.stop()

# Sidebar
st.sidebar.header("Điều chỉnh tham số")

tab1, tab2 = st.tabs(["Giả lập", "Mô phỏng theo tham số"])

with tab1:
    st.header("Giả lập nhiều chuyến xe")
    
    # Số lượng chuyến để giả lập
    n_rides = st.slider("Số lượng chuyến để giả lập", 1, 20, 5)
    
    if st.button("Chạy giả lập"):
        with st.spinner("Đang tính toán giá cho các chuyến xe..."):
            rides_data = simulate_rides(n_rides)
            
        if rides_data:
            # Hiển thị dữ liệu
            st.subheader(f"Kết quả giả lập {len(rides_data)} chuyến xe")
            
            # Chuyển đổi về DataFrame để dễ làm việc
            df = pd.DataFrame(rides_data)
            
            # Hiển thị thống kê
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Giá trung bình", f"{df['optimal_price'].mean():,.0f}đ")
            with col2:
                st.metric("% thay đổi trung bình", f"{df['price_percent_change'].mean():.1f}%")
            with col3:
                vehicle_counts = df['vehicle_type'].value_counts()
                st.metric("Loại xe phổ biến nhất", df['vehicle_type'].mode()[0])
            
            # Biểu đồ
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Biểu đồ % thay đổi giá
            sns.histplot(df['price_percent_change'], bins=10, kde=True, ax=ax1)
            ax1.axvline(0, color='red', linestyle='--')
            ax1.set_title("Phân bố % thay đổi giá")
            ax1.set_xlabel("% thay đổi giá")
            
            # Biểu đồ giá theo loại xe
            sns.boxplot(x='vehicle_type', y='optimal_price', data=df, ax=ax2)
            ax2.set_title("Giá theo loại xe")
            ax2.set_xlabel("Loại xe")
            ax2.set_ylabel("Giá (đồng)")
            
            st.pyplot(fig)
            
            # Hiển thị bảng dữ liệu
            st.subheader("Chi tiết các chuyến xe")
            st.dataframe(df)

with tab2:
    st.header("Mô phỏng theo tham số")
    
    col1, col2 = st.columns(2)
    
    with col1:
        distance = st.slider("Khoảng cách (km)", 1.0, 30.0, 5.0, 0.5)
        vehicle_type = st.selectbox(
            "Loại phương tiện",
            options=[
                {"value": 0, "label": "Xe máy"},
                {"value": 1, "label": "Xe 4 chỗ"},
                {"value": 2, "label": "Xe 7 chỗ"},
                {"value": 3, "label": "Xe sang"}
            ],
            format_func=lambda x: x["label"]
        )
        
        weather = st.selectbox(
            "Điều kiện thời tiết",
            options=[
                {"value": 0, "label": "Tốt"},
                {"value": 1, "label": "Mưa"},
                {"value": 2, "label": "Mưa to"}
            ],
            format_func=lambda x: x["label"]
        )
    
    with col2:
        traffic = st.slider("Mức độ tắc nghẽn (0-10)", 0, 10, 3)
        drivers = st.slider("Số tài xế có sẵn", 1, 50, 10)
        demand = st.slider("Nhu cầu khu vực (0-100)", 0, 100, 50)
        
        user_info = st.toggle("Hiển thị thông tin người dùng")
        
        if user_info:
            user_rating = st.slider("Đánh giá người dùng", 1.0, 5.0, 4.5, 0.1)
            user_rides = st.slider("Số chuyến đi trước đây", 0, 100, 5)
        else:
            user_rating = 4.5
            user_rides = 5
    
    if st.button("Tính giá"):
        ride_params = {
            "distance_km": distance,
            "duration_min": distance * 3,  # Ước tính thời gian
            "weather_condition": weather["value"],
            "traffic_level": traffic,
            "available_drivers": drivers,
            "area_demand": demand,
            "vehicle_type": vehicle_type["value"],
            "user_rating": user_rating,
            "user_previous_rides": user_rides
        }
        
        with st.spinner("Đang tính toán giá..."):
            result = get_price(ride_params)
            
        if "error" in result:
            st.error(f"Lỗi: {result['error']}")
        else:
            # Hiển thị kết quả
            st.subheader("Kết quả tính giá")
            
            # Các thông số chính
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Giá cơ bản", f"{result['base_price']:,.0f}đ")
            with col2:
                st.metric("Giá tối ưu", f"{result['optimal_price']:,.0f}đ")
            with col3:
                color = "normal"
                if result['price_percent_change'] > 0:
                    color = "off"
                else:
                    color = "inverse"
                st.metric("% thay đổi giá", f"{result['price_percent_change']:.1f}%", delta_color=color)
            
            # Hiển thị insights
            st.subheader("Phân tích giá")
            for insight in result['insights']:
                st.info(insight)

# Hiển thị các yếu tố ảnh hưởng đến giá
st.sidebar.header("Yếu tố ảnh hưởng đến giá")
pricing_factors = get_pricing_factors()

if pricing_factors:
    with st.sidebar.expander("Yếu tố cơ bản"):
        for factor in pricing_factors.get('base_factors', []):
            st.write(f"- {factor}")
            
    with st.sidebar.expander("Yếu tố động"):
        for factor in pricing_factors.get('dynamic_factors', []):
            st.write(f"- {factor}")
            
    with st.sidebar.expander("Điều kiện đặc biệt"):
        for factor in pricing_factors.get('special_conditions', []):
            st.write(f"- {factor}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Demo Dynamic Pricing - Phiên bản 1.0")
st.sidebar.caption(f"Cập nhật lần cuối: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
