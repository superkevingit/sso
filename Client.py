#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, url_for, request, make_response
import uuid
import redis
import time
import json
import os
from functools import wraps
import ClientConfig

# new object
app = Flask(__name__)
app.secret_key = os.urandom(24)

r = redis.StrictRedis(host=ClientConfig.get('redis_host'), +\
                      port=ClientConfig.get('redis_port'), +\
                      db=ClientConfig.get('redis_db'), +\
                      password=ClientConfig.get('redis_password'))

def generateUuid(code_for):
    uuidcode = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return uuidcode


############## Helper Function ##############

def get_cli_sessionid(request):
    sessionid = False
    if request.cookies.get('sessionid'):
        sessionid = request.cookies.get('sessionid')
    return sessionid

def get_info(sessionid):
    u_tag = r.hgetall(sessionid)
    if u_tag:
        return u_tag
    return 'Permission denied'

def with_permission(func):
    @wraps(func)
    def _get_info(**args):
        info = get_info(get_cli_sessionid(request))
        if not info:
            func_name = func.__name__
            return redirect(url_for('login', _external=True)[:-1] +\
                            '?func_name=' + str(func_name))
        info = json.dumps(info)
        return func(info, **args)
    return _get_info

############## Web Router ###################

@app.route('/login')
def login():
    redirect = request.args.get('func_name')
    return redirect(ClientConfig.get('server_url') +\
                    '?redirect=' +\
                    url_for(redirect, _external=True)[:-1] +\
                    '?app_code=' +\
                    ClientConfig.get('app_code'))


@app.route('/')
def index():
#    sid = request.args.get('student_id')
#    token = request.args.get('uc_token')
#    return sid + '+' + token
    user_id = str(uuid.uuid3(uuid.uuid1(), 'user_id').hex)
    res = make_response(redirect(url_for('cookie')))
    res.set_cookie('sessionid', value=user_id, +\
                   domain=ClientConfig.get('cli_cookie_domain'), +\
                   expires=int(time.time()) + ClientConfig.get('expires_time'))
    return res


@app.route('/cookie')
def cookie():
    sessionid = request.cookies.get('sessionid')
    print sessionid
    return sessionid


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')
