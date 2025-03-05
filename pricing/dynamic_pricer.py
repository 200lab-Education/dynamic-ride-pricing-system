import pandas as pd
import numpy as np
from datetime import datetime

class DynamicRidePricingSystem:
    """
    Hệ thống Dynamic Pricing cho ứng dụng đặt xe
    - Sử dụng mô hình ML để dự đoán giá cơ bản
    - Áp dụng các quy tắc kinh doanh để điều chỉnh giá
    - Tạo insights về lý do tại sao giá được điều chỉnh
    """
    def __init__(self, model, preprocessor):
        """
        Khởi tạo hệ thống Dynamic Pricing
        
        Args:
            model: Mô hình đã huấn luyện (RidePricingModel)
            preprocessor: Preprocessor đã fit (RideDataPreprocessor)
        """
        self.model = model
        self.preprocessor = preprocessor
        self.price_constraints = {
            'min_multiplier': 0.8,  # Giảm giá tối đa 20%
            'max_multiplier': 2.0,  # Tăng giá tối đa 100%
            'min_price': {
                0: 10000,  # Giá tối thiểu cho xe máy
                1: 20000,  # Giá tối thiểu cho xe 4 chỗ
                2: 30000,  # Giá tối thiểu cho xe 7 chỗ
                3: 50000   # Giá tối thiểu cho xe sang
            }
        }
        
    def get_ride_price(self, ride_data):
        """
        Tính giá cho một chuyến xe
        
        Args:
            ride_data: DataFrame với thông tin chuyến xe (1 dòng)
            
        Returns:
            Dict với giá tối ưu và thông tin chi tiết
        """
        # Biến đổi dữ liệu
        X = self.preprocessor.transform(ride_data)
        
        # Dự đoán giá cơ bản bằng mô hình ML
        base_price = ride_data['base_price'].values[0]
        model_price = self.model.predict(X)[0]
        
        # Điều chỉnh giá theo các quy tắc kinh doanh
        constrained_price, insights = self._apply_business_rules(ride_data)
        
        # Tính phần trăm thay đổi giá
        price_change = ((constrained_price - base_price) / base_price) * 100
        
        # Làm tròn giá đến hàng nghìn
        optimal_price = round(constrained_price, -3)
        
        return {
            'optimal_price': optimal_price,
            'base_price': base_price,
            'model_price': model_price,
            'price_percent_change': price_change,
            'insights': insights
        }
    
    def batch_price_rides(self, rides_df):
        """
        Tính giá cho nhiều chuyến xe cùng lúc
        
        Args:
            rides_df: DataFrame với thông tin nhiều chuyến xe
            
        Returns:
            DataFrame với giá và insights cho mỗi chuyến
        """
        results = []
        
        for i, row in rides_df.iterrows():
            ride_data = pd.DataFrame([row])
            price_result = self.get_ride_price(ride_data)
            
            results.append({
                'ride_id': row['ride_id'],
                'base_price': price_result['base_price'],
                'optimal_price': price_result['optimal_price'],
                'price_percent_change': price_result['price_percent_change'],
                'insights': price_result['insights']
            })
        
        return pd.DataFrame(results)
    
    def _apply_business_rules(self, ride_data):
        """
        Áp dụng các quy tắc kinh doanh để điều chỉnh giá
        
        Args:
            ride_data: DataFrame với thông tin chuyến xe (1 dòng)
            
        Returns:
            Tuple (giá sau điều chỉnh, danh sách insights)
        """
        data = ride_data.iloc[0]
        base_price = data['base_price']
        constrained_price = base_price
        insights = []
        reasons = []
        
        # 1. Yếu tố cung-cầu
        demand = data['area_demand']
        drivers = data['available_drivers']
        demand_supply_ratio = demand / max(drivers, 1)
        
        if demand_supply_ratio > 2:  # Nhu cầu gấp đôi số tài xế
            surge_multiplier = min(1.5, 1 + (demand_supply_ratio - 2) * 0.1)
            constrained_price *= surge_multiplier
            reasons.append(f"Nhu cầu cao ({demand}) và ít tài xế ({drivers}), dẫn đến tăng giá.")
        
        # 2. Điều kiện thời tiết
        weather = data['weather_condition']
        if weather == 1:  # Mưa
            constrained_price *= 1.1
            reasons.append("Thời tiết mưa làm tăng giá do điều kiện đi lại khó khăn.")
        elif weather == 2:  # Mưa to
            constrained_price *= 1.2
            reasons.append("Thời tiết mưa to làm tăng giá đáng kể do rủi ro và khó khăn trong di chuyển.")
        
        # 3. Tắc nghẽn giao thông
        traffic = data['traffic_level']
        if traffic > 7:  # Tắc nghẽn cao
            constrained_price *= 1 + (traffic - 7) * 0.03
            reasons.append(f"Tắc nghẽn giao thông cao (mức {traffic}/10) làm tăng giá.")
        
        # 4. Giờ cao điểm
        hour = data.get('hour', datetime.now().hour)
        if (hour >= 7 and hour <= 9) or (hour >= 17 and hour <= 19):
            constrained_price *= 1.15
            reasons.append(f"Đặt xe trong giờ cao điểm ({hour}h) làm tăng giá.")
        
        # 5. Chiết khấu cho người dùng thường xuyên
        previous_rides = data['user_previous_rides']
        user_rating = data['user_rating']
        
        if previous_rides > 50 and user_rating >= 4.5:
            constrained_price *= 0.95  # Giảm 5% cho người dùng trung thành
            reasons.append(f"Giảm giá 5% cho người dùng trung thành (>50 chuyến, đánh giá ≥4.5).")
        elif previous_rides > 20:
            constrained_price *= 0.98  # Giảm 2% cho người dùng thường xuyên
            reasons.append(f"Giảm giá 2% cho người dùng thường xuyên ({previous_rides} chuyến).")
        
        # 6. Đảm bảo giá nằm trong giới hạn
        min_price = self.price_constraints['min_price'][data['vehicle_type']]
        min_allowed = base_price * self.price_constraints['min_multiplier']
        max_allowed = base_price * self.price_constraints['max_multiplier']
        
        constrained_price = max(constrained_price, min_price)
        constrained_price = max(constrained_price, min_allowed)
        constrained_price = min(constrained_price, max_allowed)
        
        # Tạo insights tổng quát
        price_change = ((constrained_price - base_price) / base_price) * 100
        
        if price_change > 0:
            insights.append(f"Giá tăng {abs(price_change):.1f}% so với giá cơ bản do nhu cầu cao hoặc điều kiện bất lợi.")
        elif price_change < 0:
            insights.append(f"Giá giảm {abs(price_change):.1f}% so với giá cơ bản do ưu đãi khách hàng hoặc nhu cầu thấp.")
        else:
            insights.append("Giá bằng với giá cơ bản do điều kiện bình thường.")
        
        # Thêm các lý do cụ thể
        insights.extend(reasons)
        
        return constrained_price, insights
