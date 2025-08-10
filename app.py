import streamlit as st
from typing import Dict, List
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
load_dotenv()

# Danh sách khách sạn được đề xuất theo địa điểm
HOTEL_RECOMMENDATIONS = {
    "Da Nang": [
        {
            "name": "Vinpearl Resort & Spa Da Nang",
            "stars": 5,
            "address": "23 Truong Sa Street, Hoa Hai Ward, Ngu Hanh Son District",
            "price_range": {"VND": (2500000, 5000000), "USD": (100, 200)},
            "amenities": ["Bãi biển riêng", "Hồ bơi", "Spa", "Phòng gym", "Nhà hàng"],
            "booking_link": "https://www.vinpearl.com/danang-resort/",
            "highlights": ["View biển tuyệt đẹp", "Dịch vụ 5 sao", "Gần các điểm tham quan"]
        },
        {
            "name": "Muong Thanh Luxury Da Nang Hotel",
            "stars": 4,
            "address": "270 Vo Nguyen Giap Street, My An Ward, Ngu Hanh Son District",
            "price_range": {"VND": (1500000, 3000000), "USD": (60, 120)},
            "amenities": ["Hồ bơi", "Nhà hàng", "Phòng gym", "Bar"],
            "booking_link": "https://luxurydanang.muongthanh.com/",
            "highlights": ["Vị trí trung tâm", "Gần biển Mỹ Khê", "Giá cả hợp lý"]
        },
        {
            "name": "Novotel Danang Premier Han River",
            "stars": 4,
            "address": "36 Bach Dang Street, Hai Chau District",
            "price_range": {"VND": (2000000, 4000000), "USD": (80, 160)},
            "amenities": ["View sông Hàn", "Hồ bơi", "Nhà hàng", "Bar trên tầng thượng"],
            "booking_link": "https://novotel-danang.com/",
            "highlights": ["View sông Hàn đẹp", "Gần cầu Rồng", "Trung tâm thành phố"]
        }
    ],
    "Hoi An": [
        {
            "name": "Four Seasons Resort The Nam Hai",
            "stars": 5,
            "address": "Block Ha My Dong B, Dien Duong Ward, Dien Ban Town",
            "price_range": {"VND": (8000000, 15000000), "USD": (320, 600)},
            "amenities": ["Bãi biển riêng", "Spa", "Hồ bơi", "Villa riêng biệt"],
            "booking_link": "https://www.fourseasons.com/hoian/",
            "highlights": ["Resort sang trọng bậc nhất", "Kiến trúc độc đáo", "Dịch vụ hoàn hảo"]
        },
        {
            "name": "Allegro Hoi An Hotel & Spa",
            "stars": 4,
            "address": "326 Ly Thuong Kiet Street, Hoi An Ancient Town",
            "price_range": {"VND": (1200000, 2500000), "USD": (50, 100)},
            "amenities": ["Hồ bơi", "Spa", "Nhà hàng", "Xe đạp miễn phí"],
            "booking_link": "https://allegrohoian.com/",
            "highlights": ["Gần phố cổ", "Giá tốt", "Dịch vụ thân thiện"]
        }
    ],
    "Ha Long": [
        {
            "name": "Vinpearl Resort & Spa Ha Long",
            "stars": 5,
            "address": "Reu Island, Bai Chay Ward, Ha Long City",
            "price_range": {"VND": (3000000, 6000000), "USD": (120, 240)},
            "amenities": ["View vịnh Hạ Long", "Hồ bơi", "Spa", "Casino"],
            "booking_link": "https://www.vinpearl.com/halong-resort/",
            "highlights": ["View vịnh tuyệt đẹp", "Đảo riêng", "Tiện nghi cao cấp"]
        }
    ],
    "Nha Trang": [
        {
            "name": "Vinpearl Resort Nha Trang",
            "stars": 5,
            "address": "Hon Tre Island, Vinh Nguyen Ward",
            "price_range": {"VND": (2800000, 5500000), "USD": (110, 220)},
            "amenities": ["Công viên giải trí", "Bãi biển riêng", "Hồ bơi", "Spa"],
            "booking_link": "https://www.vinpearl.com/nhatrang-resort/",
            "highlights": ["Đảo riêng", "Vinpearl Land", "Cáp treo biển"]
        }
    ],
    "Phu Quoc": [
        {
            "name": "JW Marriott Phu Quoc Emerald Bay Resort & Spa",
            "stars": 5,
            "address": "Khem Beach, An Thoi Town",
            "price_range": {"VND": (7000000, 15000000), "USD": (280, 600)},
            "amenities": ["Bãi biển riêng", "Spa", "Hồ bơi", "Phòng gym"],
            "booking_link": "https://www.marriott.com/phuquoc-jw/",
            "highlights": ["Thiết kế độc đáo", "Bãi biển đẹp", "Dịch vụ xuất sắc"]
        }
    ]
}

# Initialize API settings
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather_forecast(location: str, start_date: str, end_date: str) -> List[Dict]:
    """Get weather forecast for the travel dates"""
    try:
        # Chuyển đổi địa điểm thành tọa độ
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={WEATHER_API_KEY}"
        location_data = requests.get(geocoding_url).json()
        
        if not location_data:
            return []
        
        lat, lon = location_data[0]['lat'], location_data[0]['lon']
        
        # Lấy dự báo thời tiết
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        forecast_data = requests.get(forecast_url).json()
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1
        
        forecasts = []
        for i in range(duration):
            date = start + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Tìm dự báo cho ngày này
            day_forecasts = [f for f in forecast_data['list'] if f['dt_txt'].startswith(date_str)]
            
            if day_forecasts:
                avg_temp = sum(f['main']['temp'] for f in day_forecasts) / len(day_forecasts)
                weather_desc = day_forecasts[0]['weather'][0]['description']
                
                forecasts.append({
                    'date': date_str,
                    'temperature': round(avg_temp, 1),
                    'description': weather_desc,
                    'min_temp': min(f['main']['temp_min'] for f in day_forecasts),
                    'max_temp': max(f['main']['temp_max'] for f in day_forecasts)
                })
        
        return forecasts
    except Exception as e:
        print(f"Error getting weather forecast: {e}")
        return []

def make_openai_request(endpoint: str, payload: dict) -> dict:
    """Make a request to the OpenAI API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{API_BASE}/{endpoint}",
        headers=headers,
        json=payload
    )
    return response.json()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def load_conversation_history() -> List[Dict]:
    """Load conversation history from session state"""
    return st.session_state.messages

def save_conversation_history(messages: List[Dict]):
    """Save conversation history to session state"""
    st.session_state.messages = messages

def get_travel_requirements(user_input: str) -> Dict:
    """Extract travel requirements using function calling"""
    # Store original input for language detection
    original_input = user_input
    functions = [
        {
            "name": "extract_travel_info",
            "description": "Extract detailed travel information from user input",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date of the trip (YYYY-MM-DD format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date of the trip (YYYY-MM-DD format)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Destination location"
                    },
                    "budget_details": {
                        "type": "object",
                        "properties": {
                            "total": {
                                "type": "number",
                                "description": "Total budget for the trip"
                            },
                            "currency": {
                                "type": "string",
                                "description": "Currency of the budget (USD, VND, etc.)"
                            },
                            "accommodation_budget": {
                                "type": "number",
                                "description": "Budget allocated for accommodation"
                            },
                            "food_budget": {
                                "type": "number",
                                "description": "Budget allocated for food and dining"
                            },
                            "activities_budget": {
                                "type": "number",
                                "description": "Budget allocated for activities and attractions"
                            },
                            "transportation_budget": {
                                "type": "number",
                                "description": "Budget allocated for transportation"
                            }
                        },
                        "required": ["total", "currency"]
                    },
                    "preferences": {
                        "type": "object",
                        "properties": {
                            "accommodation_type": {
                                "type": "string",
                                "description": "Preferred type of accommodation (hotel, hostel, resort, etc.)"
                            },
                            "activities": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of preferred activities or interests"
                            },
                            "cuisine_preferences": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Food preferences or dietary restrictions"
                            },
                            "transportation_mode": {
                                "type": "string",
                                "description": "Preferred mode of transportation"
                            }
                        }
                    },
                    "weather_check": {
                        "type": "boolean",
                        "description": "Whether to include weather information in the plan"
                    }
                },
                "required": ["start_date", "location", "budget_details"]
            }
        }
    ]

    # Get conversation history for context
    history = load_conversation_history()
    
    # Batch the function calling request with context
    messages = []
    # Add last 5 messages for context if they exist
    if history:
        messages.extend(history[-5:])
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    payload = {
        "model": "GPT-4o-mini",
        "messages": messages,
        "functions": functions,
        "function_call": {"name": "extract_travel_info"}
    }
    
    response = make_openai_request("chat/completions", payload)
    
    # Extract the function call result
    if response.get("choices") and response["choices"][0].get("message", {}).get("function_call"):
        function_call = response["choices"][0]["message"]["function_call"]
        result = json.loads(function_call["arguments"])
        # Add original input for language detection
        result['original_input'] = original_input
        return result
    return {'original_input': original_input}

def detect_language(text: str) -> str:
    """Detect if the input is Vietnamese or English"""
    # Simple detection based on Vietnamese-specific characters
    vietnamese_chars = set('àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ')
    text_chars = set(text.lower())
    return 'vi' if vietnamese_chars & text_chars else 'en'

def get_hotel_recommendations(location: str, budget: Dict, lang: str = 'en') -> str:
    """Get hotel recommendations based on location and budget"""
    hotels = HOTEL_RECOMMENDATIONS.get(location, [])
    if not hotels:
        return "No specific hotel recommendations available for this location." if lang == 'en' else "Không có đề xuất khách sạn cụ thể cho địa điểm này."
    
    currency = budget.get('currency', 'USD')
    total_budget = budget.get('total', 0)
    accommodation_budget = budget.get('accommodation_budget', total_budget * 0.4)  # Assume 40% of total budget for accommodation
    
    suitable_hotels = []
    for hotel in hotels:
        price_range = hotel['price_range'].get(currency, hotel['price_range']['USD'])
        if price_range[0] <= accommodation_budget:
            suitable_hotels.append(hotel)
    
    if not suitable_hotels:
        return "No hotels found within your budget." if lang == 'en' else "Không tìm thấy khách sạn phù hợp với ngân sách của bạn."
    
    if lang == 'en':
        recommendations = "🏨 Hotel Recommendations:\n\n"
        for hotel in suitable_hotels:
            price_range = hotel['price_range'].get(currency, hotel['price_range']['USD'])
            recommendations += f"""• {hotel['name']} ({hotel['stars']}⭐)
- Address: {hotel['address']}
- Price Range: {price_range[0]}-{price_range[1]} {currency}
- Amenities: {', '.join(hotel['amenities'])}
- Highlights: {', '.join(hotel['highlights'])}
- Booking: {hotel['booking_link']}

"""
    else:
        recommendations = "🏨 Đề xuất khách sạn:\n\n"
        for hotel in suitable_hotels:
            price_range = hotel['price_range'].get(currency, hotel['price_range']['USD'])
            recommendations += f"""• {hotel['name']} ({hotel['stars']}⭐)
- Địa chỉ: {hotel['address']}
- Khoảng giá: {price_range[0]}-{price_range[1]} {currency}
- Tiện nghi: {', '.join(hotel['amenities'])}
- Điểm nổi bật: {', '.join(hotel['highlights'])}
- Đặt phòng: {hotel['booking_link']}

"""
    
    return recommendations

def generate_travel_plan(requirements: Dict) -> str:
    """Generate a detailed travel plan based on requirements"""
    # Detect language from the original input
    user_input = requirements.get('original_input', '')
    lang = detect_language(user_input)
    
    # Get weather information if requested
    weather_info = []
    if requirements.get('weather_check'):
        weather_info = get_weather_forecast(
            requirements['location'],
            requirements['start_date'],
            requirements.get('end_date', requirements['start_date'])
        )
    
    # Get hotel recommendations
    location = requirements.get('location', '')
    budget_details = requirements.get('budget_details', {})
    hotel_recommendations = get_hotel_recommendations(location, budget_details, lang)
    
    # Create a context-aware prompt in the detected language
    preferences = requirements.get('preferences', {})
    
    if lang == 'vi':
        weather_text = ""
        if weather_info:
            weather_text = "\nThông tin thời tiết:\n" + "\n".join([
                f"- Ngày {w['date']}: {w['temperature']}°C, {w['description']}, "
                f"Thấp nhất: {w['min_temp']}°C, Cao nhất: {w['max_temp']}°C"
                for w in weather_info
            ])
        
        prompt = f"""Là một trợ lý lập kế hoạch du lịch, tạo một kế hoạch chi tiết dựa trên các yêu cầu sau:
        Ngày bắt đầu: {requirements.get('start_date', 'Chưa xác định')}
        Ngày kết thúc: {requirements.get('end_date', 'Chưa xác định')}
        Địa điểm: {requirements.get('location', 'Chưa xác định')}

{hotel_recommendations}
        
        Ngân sách:
        - Tổng: {budget_details.get('total', 'Chưa xác định')} {budget_details.get('currency', '')}
        - Chỗ ở: {budget_details.get('accommodation_budget', 'Chưa xác định')} {budget_details.get('currency', '')}
        - Ăn uống: {budget_details.get('food_budget', 'Chưa xác định')} {budget_details.get('currency', '')}
        - Hoạt động: {budget_details.get('activities_budget', 'Chưa xác định')} {budget_details.get('currency', '')}
        - Di chuyển: {budget_details.get('transportation_budget', 'Chưa xác định')} {budget_details.get('currency', '')}
        
        Sở thích:
        - Loại chỗ ở: {preferences.get('accommodation_type', 'Chưa xác định')}
        - Hoạt động yêu thích: {', '.join(preferences.get('activities', ['Chưa xác định']))}
        - Ẩm thực: {', '.join(preferences.get('cuisine_preferences', ['Chưa xác định']))}
        - Phương tiện di chuyển: {preferences.get('transportation_mode', 'Chưa xác định')}
        {weather_text}"""
    else:
        weather_text = ""
        if weather_info:
            weather_text = "\nWeather Information:\n" + "\n".join([
                f"- Date {w['date']}: {w['temperature']}°C, {w['description']}, "
                f"Low: {w['min_temp']}°C, High: {w['max_temp']}°C"
                for w in weather_info
            ])
            
        prompt = f"""As a travel planning assistant, create a detailed plan based on these requirements:
        Start Date: {requirements.get('start_date', 'Not specified')}
        End Date: {requirements.get('end_date', 'Not specified')}
        Location: {requirements.get('location', 'Not specified')}
        
        Budget:
        - Total: {budget_details.get('total', 'Not specified')} {budget_details.get('currency', '')}
        - Accommodation: {budget_details.get('accommodation_budget', 'Not specified')} {budget_details.get('currency', '')}
        - Food: {budget_details.get('food_budget', 'Not specified')} {budget_details.get('currency', '')}
        - Activities: {budget_details.get('activities_budget', 'Not specified')} {budget_details.get('currency', '')}
        - Transportation: {budget_details.get('transportation_budget', 'Not specified')} {budget_details.get('currency', '')}
        
        Preferences:
        - Accommodation Type: {preferences.get('accommodation_type', 'Not specified')}
        - Preferred Activities: {', '.join(preferences.get('activities', ['Not specified']))}
        - Cuisine Preferences: {', '.join(preferences.get('cuisine_preferences', ['Not specified']))}
        - Transportation Mode: {preferences.get('transportation_mode', 'Not specified')}
        {weather_text}

    """ + ("""
    Vui lòng cung cấp lịch trình chi tiết theo từng ngày bao gồm:
    
    Cho mỗi ngày:
    1. Thời gian biểu chi tiết (giờ cụ thể cho mỗi hoạt động)
    2. Chỗ ở đề xuất và giá cả
    3. Các hoạt động và địa điểm tham quan:
       - Thời gian cho mỗi hoạt động
       - Chi phí vào cửa/vé (nếu có)
       - Thời gian di chuyển giữa các địa điểm
    4. Bữa ăn đề xuất:
       - Nhà hàng hoặc địa điểm
       - Món ăn đặc trưng
       - Chi phí ước tính
    5. Phương tiện di chuyển:
       - Loại phương tiện
       - Chi phí
       - Thời gian di chuyển
    6. Tổng chi phí trong ngày
    7. Mẹo và khuyến nghị địa phương
    
    Lưu ý:
    - Đảm bảo tổng chi phí nằm trong ngân sách
    - Cân nhắc thời tiết khi lên kế hoạch hoạt động
    - Có phương án dự phòng cho hoạt động ngoài trời
    """ if lang == 'vi' else """
    Please provide a detailed day-by-day itinerary including:
    
    For each day:
    1. Detailed timeline (specific hours for each activity)
    2. Accommodation recommendations and costs
    3. Activities and attractions:
       - Duration for each activity
       - Entrance/ticket costs (if any)
       - Travel time between locations
    4. Meal recommendations:
       - Restaurants or venues
       - Signature dishes
       - Estimated costs
    5. Transportation:
       - Mode of transport
       - Costs
       - Travel duration
    6. Total daily expenses
    7. Local tips and recommendations
    
    Note:
    - Ensure total costs stay within budget
    - Consider weather conditions when planning activities
    - Include backup plans for outdoor activities
    """)

    # Get conversation history for context
    history = load_conversation_history()
    
    # Prepare messages with context
    messages = []
    # Add last 5 messages for context if they exist
    if history:
        messages.extend(history[-5:])
    # Add current request
    messages.append({"role": "user", "content": prompt})
    
    # Generate response with context
    payload = {
        "model": "GPT-4o-mini",
        "messages": messages
    }
    
    response = make_openai_request("chat/completions", payload)
    
    if response.get("choices"):
        return response["choices"][0]["message"]["content"]
    return "Sorry, I couldn't generate a travel plan at this moment."

# Streamlit UI
st.title("🌍 AI Travel Planner")

# Chat interface
st.write("Welcome! Let me help you plan your perfect trip. Please provide your travel details, and I'll create a customized plan for you.")

# Display chat history
for message in load_conversation_history():
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input with dynamic placeholder based on previous language
last_message = st.session_state.messages[-1] if st.session_state.messages else None
last_lang = detect_language(last_message["content"]) if last_message else "en"
placeholder = "Hãy chia sẻ kế hoạch du lịch của bạn..." if last_lang == "vi" else "Tell me about your travel plans..."
user_input = st.chat_input(placeholder)

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Extract travel requirements
    requirements = get_travel_requirements(user_input)
    
    # Generate travel plan
    travel_plan = generate_travel_plan(requirements)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(travel_plan)
    
    # Save to conversation history
    save_conversation_history([
        *load_conversation_history(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": travel_plan}
    ])
