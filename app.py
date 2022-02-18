# -*- coding: utf-8 -*-
import argparse
import json
import os
import time
import random

from config import settings
from utils import load_config
from checkin import health_report
from recent import check_recent


parser = argparse.ArgumentParser()

# parser.add_argument('config',
#                     metavar='config',
#                     help="配置文件路径")
parser.add_argument('action',
                    metavar='action',
                    choices=["check", "query"],
                    help="动作 (check: 打卡, query: 查询今日打卡情况)")

args = parser.parse_args()

username = settings.xmu_username
password = settings.xmu_password
use_webvpn = settings.get('use_webvpn', False)
use_random = settings.get('use_random', False)


if args.action == "check":
    if use_random:
        print()
        random_time_zone = settings.get('random_zone', 1)
        time.sleep(random.randint(0, random_time_zone))
    res, sta = health_report(username,
                            password,
                            use_webvpn=use_webvpn,
                            vpn_username=settings.get('vpn_username', None),
                            vpn_password=settings.get('vpn_password', None))
    print(json.dumps(res, indent=4, ensure_ascii=False))

if args.action == "query":
    res, sta = check_recent(username,
                           password,
                           use_webvpn=use_webvpn,
                           vpn_username=settings.get('vpn_username', None),
                           vpn_password=settings.get('vpn_password', None))
    print(json.dumps(res, indent=4, ensure_ascii=False))

