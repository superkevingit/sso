#!/usr/bin/env python
# encoding: utf-8

config = {
    'server_url': 'http://0.0.0.0:5000/login',
    'uc_expires': 60 * 60 * 24 * 7,
    'token_expires': 60,
    'uc_domain': '0.0.0.0:5000',
    'app_code': 'uc',
}


def get(str):
    return config[str]
