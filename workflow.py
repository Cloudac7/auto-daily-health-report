# -*- coding: utf-8 -*-
import requests
import sys
import os
import json
import hmac
import hashlib
import base64
import time
import random
import urllib.parse

from config import settings
from datetime import datetime
from utils import load_config
from checkin import health_report
from recent import check_recent

username = ""
password = ""


# TODO: Use class ReportFactory to generate
def report_with(flag, reason="", success="", type="server_chan"):
    if type == "server_chan":
        return report_with_server_chan(flag, reason, success)
    elif type == "dingtalk":
        return report_with_dingtalk(flag, reason, success)
    else:
        return None


def report_with_server_chan(flag, reason="", success=""):
    try:
        # server_chan_secret = os.environ["server_chan_secret"]
        server_chan_secret = settings.server_chan_secret
        push_url = "https://sc.ftqq.com/" + server_chan_secret + ".send"
        if flag:
            result_title = "打卡成功提醒"
            result_text = "今日打卡操作已成功!" + success
        else:
            result_title = "打卡失败提醒"
            result_text = "今日打卡操作没有成功, 请手动完成打卡。错误细节: " + reason

        print(result_text)

        session = requests.Session()
        session.post(push_url, {
            "text": result_title,
            "desp": result_text
        })
    except KeyError:
        print("Cannot report with Server-Chan: secret_key not set")
        return
    except Exception:
        print("Cannot report with Server-Chan: unknown error")
        return


def report_with_dingtalk(flag, reason="", success=""):
    try:
        dingtalk_secret = settings.dingtalk_secret
        timestamp = str(round(time.time() * 1000))
        secret_enc = dingtalk_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, dingtalk_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        webhook_signed = settings.dingtalk_webhook + '&timestamp=' + timestamp + '&sign=' + sign
        if flag:
            result_title = "打卡成功提醒"
            result_text = "今日打卡操作已成功!" + success
        else:
            result_title = "打卡失败提醒"
            result_text = "今日打卡操作没有成功, 请手动完成打卡。错误细节: " + reason

        print(result_text)

        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": result_title,
                "text": result_text,
            },
        }
        session = requests.Session()
        session.post(webhook_signed, data=json.dumps(data), headers=headers)
    except KeyError:
        print("Cannot report with DingTalk: secret_key not set")
        return
    except Exception:
        print("Cannot report with DingTalk: unknown error")
        return


try:
    username = settings.xmu_username
    password = settings.xmu_password
#     webvpn_username = os.environ["webvpn_username"]
#     webvpn_password = os.environ["webvpn_password"]
except KeyError:
    reason = "You must provide a valid username & password and VPN account to log in xmuxg.xmu.edu.cn!"
    print(reason)
    report_with(False, reason)
    sys.exit(1)

try:
    today_log, status = check_recent(username, password)
    if status == 0 and today_log["today"]:
        print("Already reported today :)")
        sys.exit(0)

    random_zone = settings.get('random_zone', 0)
    if random_zone != 0:
        random_time = random.randint(0, random_zone)
        print("Will report after %s seconds" % random_time)
        time.sleep(random_time)
    response, status = health_report(username, password)
    if status != 0:
        print("Report error, reason: " + response["reason"])
        report_with(False, response["reason"])
        sys.exit(1)

    today_log, status = check_recent(username, password)
    if status == 0:
        if today_log["today"]:
            print("Automatically reported successfully!")
            success_info = "当前连续打卡" + str(today_log["days"]) + "天, 健康码为" + str(today_log["color"]) + "码!"
            report_with(True, success=success_info)
            sys.exit(0)
        else:
            print("Automatically reported failed.")
            reason = "System rejected the health-report request."
            report_with(False, reason)
            sys.exit(1)
    else:
        report_with(False, "Internal server error")
        sys.exit(1)

except Exception as e:
    reason = "Error occurred while sending the report request."
    print(reason, e)
    report_with(False, reason)
    sys.exit(1)
