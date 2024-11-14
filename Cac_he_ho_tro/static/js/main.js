// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Form handling
    const bookingForm = document.getElementById('bookingForm');
    const recommendationResult = document.getElementById('recommendationResult');
    
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Form validation
    function validateForm(formData) {
        const requiredFields = ['name', 'age', 'gender', 'phone', 'occupation', 'nationality', 'hobbies'];
        const errors = [];
        
        requiredFields.forEach(field => {
            if (!formData.get(field)) {
                errors.push(`${field} is required`);
            }
        });
        
        // Validate age
        const age = parseInt(formData.get('age'));
        if (isNaN(age) || age < 18 || age > 120) {
            errors.push('Please enter a valid age between 18 and 120');
        }
        
        // Validate phone number
        const phoneRegex = /^\d{10,}$/;
        if (!phoneRegex.test(formData.get('phone'))) {
            errors.push('Please enter a valid phone number');
        }
        
        return errors;
    }
    
    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const errors = validateForm(formData);
        
        if (errors.length > 0) {
            showErrors(errors);
            return;
        }
        
        showLoading();
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            displayRecommendations(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred while processing your request');
        } finally {
            hideLoading();
        }
    }
    
    // Display recommendations
    function displayRecommendations(data) {
        const resultContent = document.getElementById('recommendationContent');
        
        const template = `
            <div class="room-card fade-in">
                <h4 class="text-xl font-bold mb-4">Recommended Room Type: ${data.room_type}</h4>
                <p class="text-lg mb-2">Price: ${formatCurrency(data.price)}</p>
                <div class="mb-4">
                    <h5 class="font-bold mb-2">Available Rooms:</h5>
                    <ul class="list-disc list-inside">
                        ${data.available_rooms.map(room => `
                            <li>Room ${room}</li>
                        `).join('')}
                    </ul>
                </div>
                <div>
                    <h5 class="font-bold mb-2">Similar Customer Preferences:</h5>
                    <ul class="list-// static/js/main.js (continued)

                    disc list-inside">
                        ${data.similar_customers.map(customer => `
                            <li>${customer.ho_ten} - ${customer.nghe_nghiep} from ${customer.quoc_tich}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="mt-8">
                <button onclick="bookRoom()" class="btn btn-primary w-full">
                    Đặt phòng ngay
                </button>
            </div>
        `;
        
        resultContent.innerHTML = template;
        recommendationResult.classList.remove('hidden');
        recommendationResult.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Helper functions
    function formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    }
    
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingSpinner';
        loadingDiv.innerHTML = `
            <div class="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white p-6 rounded-lg shadow-lg text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p class="mt-4">Đang xử lý...</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    }
    
    function hideLoading() {
        const loadingDiv = document.getElementById('loadingSpinner');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    function showErrors(errors) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mt-4';
        errorDiv.innerHTML = `
            <strong class="font-bold">Please fix the following errors:</strong>
            <ul class="list-disc list-inside mt-2">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
            <span class="absolute top-0 right-0 px-4 py-3">
                <svg onclick="this.parentElement.parentElement.remove()" 
                     class="fill-current h-6 w-6 text-red-500 cursor-pointer" 
                     role="button" 
                     xmlns="http://www.w3.org/2000/svg" 
                     viewBox="0 0 20 20">
                    <title>Close</title>
                    <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
                </svg>
            </span>
        `;
        bookingForm.insertAdjacentElement('beforebegin', errorDiv);
    }
    
    // Room booking function
    window.bookRoom = function() {
        const modal = document.createElement('div');
        modal.className = 'fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
                <h3 class="text-2xl font-bold mb-4">Xác nhận đặt phòng</h3>
                <p class="mb-4">Bạn có chắc chắn muốn đặt phòng này không?</p>
                <div class="flex justify-end space-x-4">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">
                        Hủy
                    </button>
                    <button onclick="confirmBooking()" 
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Xác nhận
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    window.confirmBooking = function() {
        // Implement booking confirmation logic here
        alert('Đặt phòng thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất.');
        location.reload();
    }
});

// Thêm vào file main.js
function validateForm(formData) {
    const errors = [];
    
    // Validate age
    const age = formData.get('age');
    if (!age) {
        errors.push('Vui lòng nhập tuổi');
    } else {
        const ageNum = parseInt(age);
        if (isNaN(ageNum) || ageNum < 18 || ageNum > 120) {
            errors.push('Vui lòng nhập tuổi hợp lệ (18-120)');
        }
    }
    
    // Validate phone
    const phone = formData.get('phone');
    if (!phone) {
        errors.push('Vui lòng nhập số điện thoại');
    } else if (!/^[0-9]{10}$/.test(phone)) {
        errors.push('Vui lòng nhập số điện thoại hợp lệ (10 số)');
    }
    
    // Validate other required fields
    const requiredFields = ['name', 'occupation', 'gender', 'nationality'];
    requiredFields.forEach(field => {
        if (!formData.get(field)) {
            errors.push(`Vui lòng nhập ${getFieldLabel(field)}`);
        }
    });
    
    return errors;
}

function getFieldLabel(field) {
    const labels = {
        'name': 'họ và tên',
        'occupation': 'nghề nghiệp',
        'gender': 'giới tính',
        'nationality': 'quốc tịch'
    };
    return labels[field] || field;
}

function showErrors(errors) {
    const errorDiv = document.getElementById('errorMessages');
    const errorList = document.getElementById('errorList');
    errorList.innerHTML = errors.map(error => `<li>${error}</li>`).join('');
    errorDiv.classList.remove('hidden');
}

function closeErrors() {
    document.getElementById('errorMessages').classList.add('hidden');
}

// Update form submit handler
document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Validate form
    const errors = validateForm(formData);
    if (errors.length > 0) {
        showErrors(errors);
        return;
    }
    
    // If validation passes, proceed with form submission
    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        displayRecommendations(data);
    } catch (error) {
        console.error('Error:', error);
        showErrors(['Đã xảy ra lỗi khi xử lý yêu cầu của bạn']);
    }
});

