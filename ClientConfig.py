#!/usr/bin/env python
# encoding: utf-8

config = {
    'server_url': 'http://0.0.0.0:5000/login',
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 0,
    'redis_password': 123,
    'cli_cookie_domain': '0.0.0.0:5001',
    'expires_time': 60 * 60 * 24 * 7,
    'app_code': '111',
}


def get(str):
    return config[str]
