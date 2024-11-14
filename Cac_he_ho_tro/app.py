from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)


# Cập nhật thông tin phòng với các dịch vụ đi kèm
class RoomManager:
    def __init__(self):
        self.rooms = {
            'Standard': {
                'total': 30,
                'available': [
                    {'room_number': 101, 'type': 'Phòng Đơn', 'view': 'Không có view đẹp', 'bed': '1 giường đơn'},
                    {'room_number': 102, 'type': 'Phòng Đôi', 'view': 'View thành phố', 'bed': '2 giường đơn'},
                    # Các phòng tiếp theo trong dãy Standard
                ],
                'price': 1800000,
                'services': ['Phòng tập hiện đại', 'Room Service', 'Nhà hàng Á', 'Giặt ủi quần áo'],
                'description': 'Phòng tiêu chuẩn với đầy đủ tiện nghi cơ bản',
                'amenities': ['Smart TV 42"', 'Minibar', 'Phòng tắm tiện nghi'],
                'size': '35m²'
            },
            'Deluxe': {
                'total': 30,
                'available': [
                    {'room_number': 201, 'type': 'Phòng Đôi', 'view': 'View vườn', 'bed': '1 giường đôi'},
                    {'room_number': 202, 'type': 'Phòng Gia đình', 'view': 'View hồ bơi', 'bed': '1 giường đôi, 1 giường đơn'},
                    # Các phòng tiếp theo trong dãy Deluxe
                ],
                'price': 2500000,
                'services': ['Massage & Spa', 'Room Service', 'Nhà hàng Á', 'Hồ bơi ngoài trời', 'Giặt ủi quần áo'],
                'description': 'Phòng cao cấp với view đẹp và dịch vụ spa',
                'amenities': ['Smart TV 55"', 'Minibar cao cấp', 'Ban công riêng', 'Phòng tắm sang trọng'],
                'size': '45m²'
            },
            'Suite': {
                'total': 25,
                'available': [
                    {'room_number': 301, 'type': 'Phòng Suite', 'view': 'View biển', 'bed': '1 giường king size'},
                    {'room_number': 302, 'type': 'Phòng Suite Gia đình', 'view': 'View vườn', 'bed': '2 giường đôi'},
                    # Các phòng tiếp theo trong dãy Suite
                ],
                'price': 3500000,
                'services': ['Massage & Spa', 'Room Service', 'Nhà hàng Âu', 'Hồ bơi ngoài trời', 'Dịch vụ Concierge', 'Giặt ủi quần áo'],
                'description': 'Phòng hạng sang với đầy đủ tiện nghi cao cấp',
                'amenities': ['Smart TV 65"', 'Phòng khách riêng', 'Bồn tắm Jacuzzi', 'Ban công panorama'],
                'size': '65m²'
            },
            'Executive': {
                'total': 15,
                'available': [
                    {'room_number': 401, 'type': 'Phòng Executive Đôi', 'view': 'View thành phố', 'bed': '1 giường king size'},
                    {'room_number': 402, 'type': 'Phòng Executive Suite', 'view': 'View toàn cảnh', 'bed': '2 giường đôi và 1 giường đơn'},
                    # Các phòng tiếp theo trong dãy Executive
                ],
                'price': 4000000,
                'services': ['Massage & Spa', 'Room Service', 'Nhà hàng Âu', 'Phòng họp/Hội nghị', 'Dịch vụ Concierge', 'Hồ bơi ngoài trời', 'Giặt ủi quần áo'],
                'description': 'Phòng hạng thương gia với phòng họp riêng',
                'amenities': ['Smart TV 75"', 'Phòng khách & Phòng ăn riêng', 'Bếp mini', 'Phòng tắm spa', 'Tầm nhìn 180 độ'],
                'size': '85m²'
            }
        }
        
        # Thêm thông tin về các dịch vụ cao cấp
        self.premium_services = {
            'Butler Service': 'Dịch vụ quản gia 24/7',
            'Private Chef': 'Đầu bếp riêng theo yêu cầu',
            'Luxury Transfer': 'Dịch vụ đưa đón bằng xe sang',
            'Personal Shopper': 'Dịch vụ mua sắm cá nhân',
            'Yacht Charter': 'Dịch vụ thuê du thuyền riêng'
        }

room_manager = RoomManager()

def calculate_service_match_score(customer_services, room_services):
    """Tính điểm phù hợp dịch vụ giữa khách hàng và phòng"""
    if not customer_services:
        return 0
    
    customer_services = set(customer_services.split(';'))
    room_services = set(room_services)
    
    # Tính tỷ lệ dịch vụ khách hàng muốn có trong phòng
    matched_services = customer_services.intersection(room_services)
    score = len(matched_services) / len(customer_services)
    
    return score

def preprocess_customer_data(df):
    """Tiền xử lý dữ liệu khách hàng"""
    df['customer_profile'] = df.apply(lambda row: f"{row['nghe_nghiep']} {row['quoc_tich']} {row['gioi_tinh']} {row['so_thich']} {row['dich_vu_da_su_dung']}".lower(), axis=1)
    return df

def find_similar_customers(new_customer_profile, df, n_recommendations=3):
    """Tìm khách hàng tương tự"""
    vectorizer = TfidfVectorizer(stop_words='english')
    all_profiles = list(df['customer_profile']) + [new_customer_profile]
    tfidf_matrix = vectorizer.fit_transform(all_profiles)
    
    cosine_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
    similar_indices = cosine_sim.argsort()[-n_recommendations:][::-1]
    
    return df.iloc[similar_indices]

def recommend_room_type(similar_customers, customer_services):
    """Đề xuất loại phòng dựa trên khách hàng tương tự và dịch vụ mong muốn"""
    room_scores = {}
    
    # Tính điểm cho mỗi loại phòng
    for room_type, room_info in room_manager.rooms.items():
        score = 0
        # Điểm dựa trên lựa chọn của khách hàng tương tự
        similar_room_count = similar_customers[similar_customers['loai_phong'] == room_type].shape[0]
        score += similar_room_count * 0.5  # Trọng số 0.5 cho lịch sử

        # Điểm dựa trên dịch vụ phù hợp
        service_score = calculate_service_match_score(customer_services, room_info['services'])
        score += service_score * 0.5  # Trọng số 0.5 cho dịch vụ phù hợp
        
        score = min(score, 1.0)

        room_scores[room_type] = {
            'score': score,
            'price': room_info['price'],
            'services': room_info['services'],
            'description': room_info['description'],
            'amenities': room_info['amenities'],
            'size': room_info['size']
        }
    
    # Sắp xếp phòng theo điểm và trả về 3 phòng tốt nhất
    sorted_rooms = sorted(room_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:3]
    
    return sorted_rooms

@app.route('/')
def home():
    services = [
        'Nhà hàng Á', 'Nhà hàng Âu', 'Lobby Bar', 'Room Service',
        'Hồ bơi ngoài trời', 'Phòng tập hiện đại', 'Massage & Spa',
        'Xe đưa đón sân bay', 'Giặt ủi quần áo', 'Phòng họp/Hội nghị',
        'Tour tham quan thành phố', 'Tổ chức tiệc',
        'Dịch vụ quản gia 24/7', 'Đầu bếp riêng theo yêu cầu', 'Dịch vụ đưa đón bằng xe sang'
    ]
    return render_template('index.html', services=services)

@app.route('/recommend', methods=['POST'])
def recommend():
    customer_data = request.form.to_dict()
    
    # Tạo profile cho khách hàng mới
    new_customer_profile = f"{customer_data['occupation']} {customer_data['nationality']} {customer_data['gender']} {customer_data['hobbies']} {customer_data.get('services', '')}"
    
    # Đọc và xử lý dữ liệu
    df = pd.read_csv('DuLieu_KhachHang.csv')
    df = preprocess_customer_data(df)
    
    # Tìm khách hàng tương tự
    similar_customers = find_similar_customers(new_customer_profile, df)
    
    # Đề xuất phòng
    recommended_rooms = recommend_room_type(similar_customers, customer_data.get('services', ''))
    
    # Chuẩn bị kết quả
    recommendations = []
    for room_type, info in recommended_rooms:
        recommendations.append({
            'room_type': room_type,
            'score': int(info['score'] * 100),
            'price': "{:,}".format(info['price']),
            'services': info['services'],
            'description': info['description'],
            'amenities': info['amenities'],
            'size': info['size'],
            'available_rooms': room_manager.rooms[room_type]['available'][:3]
        })

    return jsonify({
        'recommendations': recommendations,
        'similar_customers': similar_customers[['ho_ten', 'nghe_nghiep', 'quoc_tich']].to_dict('records')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)