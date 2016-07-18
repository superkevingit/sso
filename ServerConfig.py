#!/usr/bin/env python
# encoding: utf-8

config = {
    'server_url': 'http://0.0.0.0:5000/login',
}


def get(str):
    return config[str]
