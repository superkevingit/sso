#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, url_for, request, make_response, render_template
import uuid
import redis
import time
import os
from functools import wraps
import ClientConfig
import requests
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
host=ClientConfig.get('redis_host')
port=ClientConfig.get('redis_port')
db=ClientConfig.get('redis_db')
password=ClientConfig.get('redis_password')
domain=ClientConfig.get('cli_cookie_domain')
expires=int(time.time()) + ClientConfig.get('expires_time')
app_code=ClientConfig.get('app_code')

r = redis.StrictRedis(host=host, port=port, db=db, password=password)


def generateUuid(code_for):
    uuidcode = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return uuidcode


# ############# Helper Function ##############
def get_sessionid(request):
    sessionid = False
    if request.cookies.get('sessionid'):
        sessionid = request.cookies.get('sessionid')
    return sessionid


def get_info(sessionid):
    u = r.hgetall(sessionid)
    if u:
        return u
    return False


def with_permission(func):
    @wraps(func)
    def _get_info():
        info = get_info(get_sessionid(request))
        if info is False:
            view_before = url_for(str(func.__name__), _external=True)
            return redirect(url_for('login', view_before=view_before))
        result = {'msg': True, 'info': info}
        result = json.dumps(result)
        return func(result)
    return _get_info


# ############# Token/Local Session Manager ########
class TokenUtil:
    def setToken(self, uc_token, TokenInfo):
        uc_token = 'token:' + uc_token
        return r.hmset(uc_token, TokenInfo)

    def getToken(self, uc_token):
        uc_token = 'token:' + uc_token
        return r.hgetall(uc_token)

TokenUtil = TokenUtil()


class LocalSessionUtil:
    def delLocalSession():
        pass


# ############# Web Router ###################
# a page need permit
@app.route('/page', methods=['GET'])
@with_permission
def page(result):
    result = json.loads(result)
    return render_template('page.html', info=result['info'])


@app.route('/login', methods=['GET'])
def login():
    view_before = request.args.get('view_before') if request.args.get('view_before') else url_for('login', _external=True)
    payload = {'view_before': view_before, 'view_token': url_for('token', _external=True)}
    server_url = ClientConfig.get('server_url')
    r= requests.get(server_url, params=payload)
    return redirect(r.url)


@app.route('/token', methods=['GET'])
@app.before_request
def token():
    if request.args.get('token'):
        token = request.args.get('token')
        tkn = TokenUtil.getToken(token)
        if tkn is not None:
            TokenUtil.setToken(token, {'app_code': app_code})
            sessionid = tkn['sessionid']
            @after_this_request
            def set_sessionid(response):
                response.set_cookie('sessionid', value=sessionid, domain=domain, expires=expires)
#            return json.dumps({'result': True, 'msg': 'token permit'})
        return json.dumps({'result': False, 'msg': 'token expires or illegal'})
    return json.dumps({'result': False, 'msg': 'no token'})


@app.route('/cook')
def cook():
    resp = make_response(redirect('http://0.0.0.0:5000/show_user'))
    value = generateUuid('cookietest')
    resp.set_cookie('cookietest', value=value, domain=domain, expires=expires)
    return 'hello'


@app.route('/')
def index():
    return 'I am sso-client'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')
