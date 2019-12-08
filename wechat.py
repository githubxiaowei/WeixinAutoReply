import itchat
import jieba
import pandas as pd
import configparser
import _thread
from utils.weather import *
from utils.schedule import *

# 读取配置文件中的 key
config = configparser.RawConfigParser()
config.read('key.cfg')
key = config.get('settings', 'key')

# 全局变量，控制开关
global on
on = True

# 读取城市列表
CSV_FILE_PATH = './china-city-list.csv'
df = pd.read_csv(CSV_FILE_PATH, skiprows=1)
city_set = set(df["City_CN"])


def save_msg(filename, msg):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg.createTime))
    msg_str = "Time: {}\nFrom: {} \nTo  : {}\nCont: {}".format(time_str,
                                                               msg.fromUserName,
                                                               msg.toUserName,
                                                               msg.content)
    with open(filename, 'a', encoding='utf8') as f:
        f.write(msg_str)
        f.write('\n')


def send_to(msg, remarkName):
    result = itchat.search_friends(remarkName)
    if len(result) == 1 and remarkName == result[0]["RemarkName"]:  #
        target = result[0]["UserName"]
        itchat.send(msg, target)


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def text_reply(msg):
    global on

    save_msg('log', msg)

    # 发给文件助手时，相当于发给自己
    if msg.toUserName == "filehelper":
        msg.fromUserName = msg.toUserName

    # 打开、关闭自动回复
    if msg.toUserName == msg.fromUserName:
        if msg.text == "on":
            on = True
        elif msg.text == "off":
            on = False

    if on:

        loc_list = []
        for w in jieba.cut(msg.content, cut_all=False):
            if w in city_set:
                loc_list.append(w)

        for loc in loc_list:
            m = "[自动回复-实时天气]\n" + weather_now(loc, key)
            itchat.send_msg(m, msg.fromUserName)


global login


def keep_run(app):
    global login
    assert (login == True)
    app.run()
    login = False


itchat.auto_login(hotReload=True)
login = True
_thread.start_new_thread(keep_run, (itchat,))

while (login):
    isHour, hour = is_hour()

    if isHour and hour%2==0:
        message_concent = "[整点天气]\n" + weather_now(loc='杭州', key=key)
        send_to(message_concent, 'csm')

    if is_day():
        message_concent = "[天气预报]\n" + weather_forecast(loc='杭州', key=key)
        send_to(message_concent, 'csm')

    time.sleep(60)
