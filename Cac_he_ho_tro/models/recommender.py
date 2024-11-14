# models/recommender.py

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

class RoomRecommender:
    def __init__(self):
        self.model = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def fit(self, X, feature_names):
        """Huấn luyện model với dữ liệu đã cho"""
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        return self
    
    def recommend(self, customer_features, df):
        """Đưa ra gợi ý phòng dựa trên đặc điểm của khách hàng"""
        # Chuẩn hóa features của khách hàng mới
        customer_features_scaled = self.scaler.transform([customer_features])
        
        # Tìm k neighbors gần nhất
        distances, indices = self.model.kneighbors(customer_features_scaled)
        
        # Lấy thông tin của các khách hàng tương tự
        similar_customers = df.iloc[indices[0]]
        
        # Đếm số lượng mỗi loại phòng trong các khách hàng tương tự
        room_counts = similar_customers['loai_phong'].value_counts()
        
        # Tính điểm cho mỗi loại phòng
        room_scores = {}
        for idx, customer_idx in enumerate(indices[0]):
            room_type = df.iloc[customer_idx]['loai_phong']
            # Điểm càng cao khi distance càng nhỏ
            score = 1 / (distances[0][idx] + 1e-6)
            room_scores[room_type] = room_scores.get(room_type, 0) + score
            
        # Sắp xếp các loại phòng theo điểm
        recommended_rooms = sorted(room_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_recommendation': recommended_rooms[0][0],
            'all_recommendations': recommended_rooms,
            'similar_customers': similar_customers[['ho_ten', 'nghe_nghiep', 'quoc_tich', 'loai_phong']].to_dict('records'),
            'confidence_scores': {room: score/sum(room_scores.values()) for room, score in room_scores.items()}
        }
    
    def get_feature_importance(self):
        """Trả về tầm quan trọng của các features"""
        if self.feature_names is None:
            return None
            
        # Tính toán feature importance dựa trên variance của dữ liệu đã chuẩn hóa
        importance = np.abs(self.scaler.scale_)
        
        # Chuẩn hóa importance scores
        importance = importance / np.sum(importance)
        
        return dict(zip(self.feature_names, importance))