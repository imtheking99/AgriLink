from django import template
import requests

register = template.Library()

@register.inclusion_tag('weather/weather_partial.html')
def show_weather():
    city = 'Colombo'
    api_key = '1e74f142f97c2bdc20efeb4a44461208'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    context = {'city': city}
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            context['weather'] = data
            desc = data['weather'][0]['description'].lower()
            
            if 'clear' in desc:
                context['condition_class'] = 'sunny'
                context['weather_icon'] = 'fa-sun'
            elif any(w in desc for w in ['rain', 'drizzle', 'storm']):
                context['condition_class'] = 'rainy'
                context['weather_icon'] = 'fa-cloud-showers-heavy'
            else:
                context['condition_class'] = 'cloudy'
                context['weather_icon'] = 'fa-cloud'
            
            if data['main']['temp'] > 30:
                context['alerts'] = ["High heat alert! Protect your crops."]
            elif 'rain' in desc:
                context['alerts'] = ["Rain expected! Ensure proper drainage."]
        else:
            context['error'] = 'City not found!'
    except:
        context['error'] = 'Service unavailable!'
        
    return context
