import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class RideDataPreprocessor:
    """
    Preprocessor cho dữ liệu chuyến xe
    - Tiền xử lý các thuộc tính số
    - Mã hóa one-hot cho thuộc tính phân loại
    - Tạo các thuộc tính tương tác
    """
    def __init__(self):
        self.preprocessor = None
        self.feature_names = None
        
    def fit(self, X):
        """
        Khớp preprocessor với dữ liệu huấn luyện
        
        Args:
            X: DataFrame với dữ liệu chuyến xe
            
        Returns:
            self
        """
        # Định nghĩa các cột
        numeric_features = [
            'distance_km', 'duration_min', 'hour', 'day_of_week', 
            'traffic_level', 'available_drivers', 'area_demand', 
            'user_rating', 'user_previous_rides'
        ]
        
        categorical_features = ['weather_condition', 'vehicle_type', 'is_weekend']
        
        # Xây dựng transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
            ])
        
        # Khớp preprocessor
        self.preprocessor = preprocessor.fit(X)
        
        # Lấy tên các thuộc tính sau khi biến đổi
        cat_columns = []
        for i, col in enumerate(categorical_features):
            categories = self.preprocessor.transformers_[1][1].categories_[i][1:]
            cat_columns.extend([f'{col}_{cat}' for cat in categories])
        
        self.feature_names = numeric_features + cat_columns
        
        return self
    
    def transform(self, X):
        """
        Biến đổi dữ liệu chuyến xe sang dạng phù hợp cho mô hình học máy
        
        Args:
            X: DataFrame với dữ liệu chuyến xe
            
        Returns:
            Array đã được biến đổi
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor chưa được khớp. Hãy gọi fit() trước.")
        
        # Biến đổi dữ liệu
        X_transformed = self.preprocessor.transform(X)
        
        # Thêm các thuộc tính tương tác (nếu cần)
        # Ví dụ: tỷ lệ cung-cầu là một thuộc tính quan trọng
        X_df = pd.DataFrame(X_transformed, columns=self.feature_names)
        
        return X_df
