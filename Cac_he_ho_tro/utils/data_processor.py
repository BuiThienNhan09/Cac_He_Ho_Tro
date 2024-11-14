# utils/data_processor.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class DataProcessor:
    def __init__(self):
        self.label_encoders = {}
        
    def preprocess_customer_data(self, df):
        """Tiền xử lý dữ liệu khách hàng"""
        # Tạo bản sao để không ảnh hưởng đến dữ liệu gốc
        processed_df = df.copy()
        
        # Xử lý các giá trị null
        processed_df['so_thich'] = processed_df['so_thich'].fillna('')
        processed_df['dich_vu_da_su_dung'] = processed_df['dich_vu_da_su_dung'].fillna('')
        
        # Chuẩn hóa text
        text_columns = ['nghe_nghiep', 'quoc_tich', 'so_thich', 'dich_vu_da_su_dung']
        for col in text_columns:
            processed_df[col] = processed_df[col].str.lower()
            
        # Mã hóa các biến categorical
        categorical_columns = ['gioi_tinh', 'loai_phong']
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            processed_df[col] = self.label_encoders[col].fit_transform(processed_df[col])
            
        return processed_df
    
    def create_customer_profile(self, customer_data):
        """Tạo profile cho khách hàng mới"""
        profile = {
            'nghe_nghiep': customer_data.get('occupation', '').lower(),
            'quoc_tich': customer_data.get('nationality', '').lower(),
            'gioi_tinh': customer_data.get('gender', ''),
            'so_thich': customer_data.get('hobbies', '').lower(),
            'dich_vu_quan_tam': ','.join(customer_data.getlist('services')).lower()
        }
        return profile
    
    def calculate_age(self, birth_date):
        """Tính tuổi từ ngày sinh"""
        today = pd.Timestamp.now()
        birth = pd.to_datetime(birth_date)
        age = today.year - birth.year
        if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
            age -= 1
        return age
    
    def extract_features(self, df):
        """Trích xuất features cho model học máy"""
        # Tạo features từ sở thích
        df['so_thich_count'] = df['so_thich'].str.count(';') + 1
        
        # Tạo features từ dịch vụ đã sử dụng
        df['dich_vu_count'] = df['dich_vu_da_su_dung'].str.count(';') + 1
        
        # Tính tuổi
        df['tuoi'] = df['ngay_sinh'].apply(self.calculate_age)
        
        # Tạo feature matrix
        feature_cols = ['tuoi', 'so_thich_count', 'dich_vu_count', 'gioi_tinh']
        X = df[feature_cols].values
        
        return X