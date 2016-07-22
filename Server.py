#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request, render_template, url_for, make_response, redirect
import redis
import uuid
import requests
import ServerConfig
import json

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0, password=123)
token_expires = ServerConfig.get('token_expires')
uc_expires = ServerConfig.get('uc_expires')
uc_domain = ServerConfig.get('uc_domain')
app_code = ServerConfig.get('app_code')


# ############# Helper Function ####################
def generateUuid(code_for):
    token = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return token


# ############# Token/GlobalSession Manager ###############
class TokenUtil:
    def setToken(self, uc_token, TokenInfo):
        uc_token = 'token:' + uc_token
        r.hmset(uc_token, TokenInfo)
        return r.expire(uc_token, token_expires)

    def getToken(self, uc_token):
        uc_token = 'token:' + uc_token
        return r.hgetall(uc_token)

    def delToken(self, uc_token):
        uc_token = 'token:' + uc_token
        return r.delete(uc_token)

TokenUtil = TokenUtil()


class GlobalSessionUtil:
    def setGlobalSession(self, ucsession, sessionid, app_code):
        ucsession = 'sso:' + ucsession
        sessionid = 'sessionid:' + app_code + ':' + sessionid
        return r.lpush(ucsession, sessionid)

    def getGlobalSessionNumber(self, ucsession):
        ucsession = 'sso:' + ucsession
        return r.llen(ucsession)

    def delGlobalSession(self, ucsession):
        ucsession = 'sso:' + ucsession
        back_value = True
        while back_value:
            back_value = r.lpop(ucsession)
            r.delete(str(back_value))
        return True

GlobalSessionUtil = GlobalSessionUtil()


class LocalSessionUtil:
    def setLocalSession(self, sessionid, info, app_code):
        sessionid = 'sessionid:' + app_code + ':' + sessionid
        r.hmset(sessionid, info)
        return r

    def getLocalSession(self, sessionid):
        sessionid = 'sessionid:' + app_code + ':' + sessionid
        pass


LocalSessionUtil = LocalSessionUtil()


# ############# Web Router #########################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.args.get('view_before'):
        view_before = request.args.get('view_before')
    elif request.form.get('view_before'):
        view_before = request.form.get('view_before')
    else:
        view_before = url_for('show_user', _external=True)

    if request.args.get('view_token'):
        view_token = request.args.get('view_token')
    elif request.form.get('view_token'):
        view_token = request.form.get('view_token')
    else:
        view_token = url_for('token', _external=True)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # mysql select!
        if username and password:
            token = generateUuid('token')
            sessionid = generateUuid('sessionid')
            TokenUtil.setToken(token, {'sessionid': sessionid, 'username': username, 'app_code': ''})
            # here is a request,need more time
            req = requests.get(view_token, params={'token': token})
            token_check = json.loads(req.text)['result']
            if token_check:
                # time delay(need something!)
                ucsession = generateUuid('ucsession')
                res = make_response()
                res.set_cookie('ucsession', value=ucsession, domain=uc_domain, expires=uc_expires)
                app_code = TokenUtil.getToken(token)['app_code']
                GlobalSessionUtil.setGlobalSession(ucsession, sessionid, str(app_code))
                info = {'username': username, 'name': 'select from mysql!'}
                LocalSessionUtil.setLocalSession(sessionid, info, str(app_code))
                TokenUtil.delToken(token)
                return redirect(view_before)
        return render_template('login.html', view_before=view_before, view_token=view_token)
    return render_template('login.html', view_before=view_before, view_token=view_token)


# need fix!
@app.route('/token', methods=['GET'])
def token():
    if request.args.get('token'):
        token = request.args.get('token')
        tkn = r.hgetall(token)
        if tkn is not None:
            sessionid = generateUuid('sessionid')
            print sessionid
            r.hmset(token, {'sessionid': sessionid, 'app_code': ServerConfig.get('app_code')})
            res = make_response()
            res.set_cookie('sessionid', value=sessionid, domain=uc_domain, expires=uc_expires)
            return (res, json.dumps({'result': True, 'msg': 'token permit'}))
        return json.dumps({'result': False, 'msg': 'token expires or illegal'})
    return json.dumps({'result': False, 'msg': 'no token'})


# need a decorator
@app.route('/show_user')
def show_user():
    return 'I am show user'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
