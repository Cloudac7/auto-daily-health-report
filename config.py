# -*- coding: utf-8 -*-
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="REPORT",
    settings_files=['config.json'],
)
