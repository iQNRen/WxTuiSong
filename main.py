import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os
 
 
def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)
 
 
# https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="wx03128739273e2cd4"&secret="9ad2c696b07784badadc270044a2fa67"

def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)

    return access_token

def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    # print(response)
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
        print(location_id)
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()

    # print(response)
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    return weather, temp, wind_dir
 
def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_ch = r.json()["note"]
    return note_ch
 
 
def send_message(to_user, access_token, region_name, weather, temp, wind_dir, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取创建时间的日期格式
    create_year = int(config["date"].split("-")[0])
    create_month = int(config["date"].split("-")[1])
    create_day = int(config["date"].split("-")[2])
    create_date = date(create_year, create_month, create_day)
    # 获取现在持续时间的日期差
    days = str(today.__sub__(create_date)).split(" ")[0]

    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "day":{
                "value": days,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            }
        }
    }


    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)
 
 
if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)
 
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, wind_dir = get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "":
        # 获取词霸每日金句
        note_ch = get_ciba()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch, note_en)
    os.system("pause")