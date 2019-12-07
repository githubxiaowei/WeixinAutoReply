import itchat
import requests
import json
import time
import jieba
import pandas as pd
import configparser


config = configparser.RawConfigParser()
config.read('key.cfg')

key = config.get('settings', 'key')

# 全局变量，控制开关
global on
on = True

CSV_FILE_PATH = './china-city-list.csv'
df = pd.read_csv(CSV_FILE_PATH, skiprows=1)
city_set = set(df["City_CN"])


def weather_forecast(loc):
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


def weather_now(loc):
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

    message = "[自动回复-实时天气]\n"
    message += "地区：{}-{}-{}\n".format(cnty, admin_area, location)
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


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def text_reply(msg):
    global on

    # json_str = json.dumps(msg, ensure_ascii=False, indent=4, separators=(',', ':'))
    # print(json_str)

    # 发给文件助手时，相当于发给自己
    if msg.toUserName == "filehelper":
        msg.fromUserName = msg.toUserName

    # 打开、关闭自动回复
    if msg.toUserName == msg.fromUserName:
        if msg.text == "on":
            on = True
        elif msg.text == "off":
            on = False
    print("Auto-Reply: ", on)

    if on:
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg.createTime))
        msg_str = "Time: {}\nFrom: {} \nTo  : {}\nCont: {}".format(time_str, msg.fromUserName, msg.toUserName,
                                                                   msg.content)
        print(msg_str)

        loc_list = []
        for w in jieba.cut(msg.content, cut_all=False):
            if w in city_set:
                loc_list.append(w)

        for loc in loc_list:
            m = weather_now(loc)
            itchat.send_msg(m, msg.fromUserName)


# 二维码登陆
itchat.auto_login(hotReload=True)
itchat.run()
