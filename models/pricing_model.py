import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

class RidePricingModel:
    """
    Mô hình dự đoán giá chuyến xe dựa trên các đặc trưng
    """
    def __init__(self, params=None):
        """
        Khởi tạo mô hình với các tham số cấu hình
        
        Args:
            params: Dict các tham số cho RandomForestRegressor
        """
        default_params = {
            'n_estimators': 100,
            'max_depth': 15,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
            
        self.model = RandomForestRegressor(**default_params)
        self.feature_importance = None
        
    def fit(self, X, y):
        """
        Huấn luyện mô hình dự đoán giá
        
        Args:
            X: DataFrame với các đặc trưng đã được tiền xử lý
            y: Series giá chuyến xe
            
        Returns:
            self
        """
        self.model.fit(X, y)
        
        # Lưu tầm quan trọng của đặc trưng
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return self
    
    def predict(self, X):
        """
        Dự đoán giá chuyến xe
        
        Args:
            X: DataFrame với các đặc trưng đã được tiền xử lý
            
        Returns:
            Array giá dự đoán
        """
        return self.model.predict(X)
    
    def evaluate(self, X, y):
        """
        Đánh giá mô hình trên tập dữ liệu
        
        Args:
            X: DataFrame với các đặc trưng đã được tiền xử lý
            y: Series giá chuyến xe thực tế
            
        Returns:
            Dict với các độ đo đánh giá
        """
        predictions = self.predict(X)
        
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)
        mape = np.mean(np.abs((y - predictions) / y)) * 100
        
        return {
            'mae': mae,
            'r2': r2,
            'mape': mape
        }
    
    def get_feature_importance(self):
        """
        Trả về tầm quan trọng của các đặc trưng
        
        Returns:
            DataFrame với tầm quan trọng của các đặc trưng
        """
        return self.feature_importance
    
    def save(self, path):
        """
        Lưu mô hình vào file
        
        Args:
            path: Đường dẫn file để lưu mô hình
        """
        joblib.dump(self, path)
    
    @classmethod
    def load(cls, path):
        """
        Tải mô hình từ file
        
        Args:
            path: Đường dẫn file mô hình
            
        Returns:
            Instance của RidePricingModel
        """
        return joblib.load(path)
