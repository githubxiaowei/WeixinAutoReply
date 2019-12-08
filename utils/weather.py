import requests
import json

def weather_forecast(loc, key):
    url = 'https://free-api.heweather.net/s6/weather/forecast?location={}&key={}'.format(loc, key)
    res = requests.get(url)

    data = json.loads(res.text)
    # data_str = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':'))

    weather_data = data["HeWeather6"][0]
    location = weather_data["basic"]["location"]
    admin_area = weather_data["basic"]["admin_area"]
    cnty = weather_data["basic"]["cnty"]
    time = weather_data["update"]["loc"]
    forecast = weather_data["daily_forecast"]

    day_text = ["今天", "明天", "后天"]
    message = "地区：{}-{}-{}\n".format(cnty, admin_area, location)
    message += "时间：{}\n".format(time)
    message += '\n'.join(["{}({})，日间天气{}，夜间天气{}，相对湿度{}%，最高气温{}度，最低气温{}度，风向{}，风力{}级，能见度{}公里。" \
                         .format(day_text[i],
                                 forecast[i]["date"],
                                 forecast[i]["cond_txt_d"],
                                 forecast[i]["cond_txt_n"],
                                 forecast[i]["hum"],
                                 forecast[i]["tmp_max"],
                                 forecast[i]["tmp_min"],
                                 forecast[i]["wind_dir"], forecast[0]["wind_sc"], forecast[0]["vis"]) for i in
                          range(2)])
    return message


def weather_now(loc, key):
    url = 'https://free-api.heweather.net/s6/weather/now?location={}&key={}'.format(loc, key)
    res = requests.get(url)

    data = json.loads(res.text)
    # data_str = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':'))

    weather_data = data["HeWeather6"][0]
    location = weather_data["basic"]["location"]
    admin_area = weather_data["basic"]["admin_area"]
    cnty = weather_data["basic"]["cnty"]
    time = weather_data["update"]["loc"]
    now = weather_data["now"]

    message = "地区：{}-{}-{}\n".format(cnty, admin_area, location)
    message += "时间：{}\n".format(time)
    message += "天气{}，温度{}度，体感温度{}度，相对湿度{}%，风向{}，风力{}级，能见度{}公里。" \
        .format(now["cond_txt"],
                now["tmp"],
                now["fl"],
                now["hum"],
                now["wind_dir"],
                now["wind_sc"],
                now["vis"])
    return message
