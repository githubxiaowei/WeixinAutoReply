import itchat
import jieba
import pandas as pd
import configparser
import _thread
from utils.weather import *
from utils.schedule import *


class Robot:

    def __init__(self, ):
        """
        """
        self.key = self.load_key()
        self.on = True
        self.city_set = self.load_city()
        self.login_status = False
        self.instance = itchat

    def load_key(self):
        """
        load key from config file 'key.cfg'
        :return: string
        """
        config = configparser.RawConfigParser()
        config.read('key.cfg')
        return config.get('settings', 'key')

    def load_city(self):
        """
        load cities' names from csv file 'china-city-list.csv'
        :return: set
        """
        CSV_FILE_PATH = 'data/china-city-list.csv'
        df = pd.read_csv(CSV_FILE_PATH, skiprows=1)
        return set(df["City_CN"])

    def save_msg(self, filename, msg):
        """
        save messages to disk
        :param filename: log file location
        :param msg: messages to restore
        :return: None
        """
        if msg.fromUserName == 'newsapp':
            return

        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg.createTime))
        msg_str = "Time: {}\nFrom: {} \nTo  : {}\nCont: {}\n".format(time_str,
                                                                     msg.fromUserName,
                                                                     msg.toUserName,
                                                                     msg.content)
        with open(filename, 'a', encoding='utf8') as f:
            f.write(msg_str)
            f.write('\n')

    def send_to(self, msg, remarkName):
        """
        send message to a friend spercified by his remarkname
        :param msg: message to send
        :param remarkName: remarkname
        :return: None
        """
        result = self.instance.search_friends(remarkName)
        if len(result) == 1 and remarkName == result[0]["RemarkName"]:  #
            target = result[0]["UserName"]
            self.instance.send(msg, target)

    def text_reply(self, msg):
        """
        Auto-reply according to message recieved
        :param msg: message recieved
        :return: None
        """

        self.save_msg('log', msg)

        # 发给文件助手时，相当于发给自己
        if msg.toUserName == "filehelper":
            msg.fromUserName = msg.toUserName

        # 打开、关闭自动回复
        if msg.toUserName == msg.fromUserName:
            if msg.text == "on":
                self.on = True
            elif msg.text == "off":
                self.on = False

        if self.on:

            loc_list = []
            for w in jieba.cut(msg.content, cut_all=False):
                if w in self.city_set:
                    loc_list.append(w)

            for loc in loc_list:
                m = "[自动回复-实时天气]\n" + weather_now(loc, self.key)
                self.instance.send_msg(m, msg.fromUserName)

    def auto_reply(self, app):
        """
        Modify self.login_status when LOG OUT
        :param app: itchat
        :return:
        """
        assert (self.login_status == True)
        app.run()
        self.login_status = False

    def login(self, hotReload=False):
        """
        Login your Weixin account by QR pic
        :param hotReload: if restore the login status
        :return:
        """
        self.instance.auto_login(hotReload=hotReload)
        self.login_status = True

    def scheduled_task(self):
        """
        User-spercified task
        :return: None
        """
        isHour, hour = is_hour()

        if isHour and hour % 2 == 0:
            message_concent = "[整点天气]\n" + weather_now(loc='杭州', key=self.key)
            self.send_to(message_concent, 'csm')

        if is_day():
            message_concent = "[天气预报]\n" + weather_forecast(loc='杭州', key=self.key)
            self.send_to(message_concent, 'csm')

        time.sleep(60)

    def run(self):
        """
        Combine autoreply and scheduled-task together by multi-threading
        :return: None
        """
        _thread.start_new_thread(self.auto_reply, (self.instance,))
        while (self.login_status):
            self.scheduled_task()


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def text_reply(msg):
    robot.text_reply(msg)


robot = Robot()
robot.login(hotReload=True)
robot.run()
