import requests

def get_weather(city: str) -> str:
    """
    获取城市天气，使用免费的 wttr.in API
    city: 城市名（中文或英文都可以）
    """
    try:
        # 详细天气格式
        url = f"https://wttr.in/{city}"
        params = {"format": "j1", "lang": "zh"}  # j1 是 JSON 格式
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        
        # 提取关键信息
        temp_c = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]
        weather_desc = current["weatherDesc"][0]["value"]
        wind_speed = current["windspeedKmph"]
        
        # 获取城市名
        area_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        
        # 获取未来3天天气
        forecasts = []
        for day in data["weather"][:3]:
            date = day["date"]
            max_temp = day["maxtempC"]
            min_temp = day["mintempC"]
            desc = day["hourly"][4]["weatherDesc"][0]["value"]
            forecasts.append(f"{date}: {desc}，最高{max_temp}°C，最低{min_temp}°C")
        
        result = f"""📍 {area_name}, {country}
🌡️ 当前温度: {temp_c}°C（体感 {feels_like}°C）
🌤️ 天气状况: {weather_desc}
💧 湿度: {humidity}%
💨 风速: {wind_speed} km/h

📅 未来3天预报:
""" + "\n".join(forecasts)
        
        return result
    
    except Exception as e:
        # 降级用简单格式
        try:
            url = f"https://wttr.in/{city}?format=4"
            response = requests.get(url, timeout=10)
            return response.text.strip()
        except:
            return f"获取天气失败: {str(e)}"


if __name__ == "__main__":
    print(get_weather("北京"))
    print("\n---\n")
    print(get_weather("Shanghai"))
