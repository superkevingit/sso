#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, url_for, request, make_response
import uuid
import redis
import time
import os
from functools import wraps
import ClientConfig
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)
host=ClientConfig.get('redis_host')
port=ClientConfig.get('redis_port')
db=ClientConfig.get('redis_db')
password=ClientConfig.get('redis_password')
domain=ClientConfig.get('cli_cookie_domain')
expires=int(time.time()) + ClientConfig.get('expires_time')

r = redis.StrictRedis(host=host, port=port, db=db, password=password)


def generateUuid(code_for):
    uuidcode = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return uuidcode


# ############# Helper Function ##############

def get_cli_sessionid(request):
    sessionid = False
    if request.cookies.get('sessionid'):
        sessionid = request.cookies.get('sessionid')
    return sessionid


def set_cli_sessionid(func):
    @wraps(func)
    def _set_cli_sessionid(**args):
        session_id = get_cli_sessionid(request)
        if session_id:
            return session_id
        sessionid = generateUuid('sessionid')
        res = make_response(url_for(str(func.__name__)))
        res.set_cookie('sessionid', value=sessionid, domain=domain, expires=expires)
        return func(res, **args)
    return _set_cli_sessionid


def get_info(sessionid):
    u_tag = r.hgetall(sessionid)
    if u_tag:
        return u_tag
    return False


def with_permission(func):
    @wraps(func)
    def _get_info(**args):
        info = get_info(get_cli_sessionid(request))
        if not info:
            fuc_name = func.__name__
            return redirect(url_for('login', _external=True) + '?view_before=' + str(fuc_name))
#        info = json.dumps(info)
        return func(info, **args)
    return _get_info

# ############# Session Manager ########

# ############# Web Router ###################


@app.route('/login', methods=['GET'])
def login():
    view_before = request.args.get('view_before')
    payload = {'view_before': url_for(view_before, _external=True), 'expires': expires, 'app_code': ClientConfig.get('app_code')}
    server_url = ClientConfig.get('server_url')
    r= requests.get(server_url, params=payload)
    return redirect(r.url)


@app.route('/token/<token>', methods=['GET'])
def token():
    r.hgetall(token)


@app.route('/')
def index():
    return 'I am sso-client'


# a page need permit
@app.route('/page')
@with_permission
def page(info):
    if request.cookies.get('sessionid'):
        sessionid = request.cookies.get('sessionid')
        return sessionid
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')
