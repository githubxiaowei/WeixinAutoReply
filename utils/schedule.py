import time

def is_hour():
    if (time.strftime("%M", time.localtime()) == '00'):
        return True, int(time.strftime("%H", time.localtime()))
    return False, None

def is_day():
    isHour, hour = is_hour()
    return isHour and hour==0
