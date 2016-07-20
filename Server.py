#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, request, render_template, url_for, make_response, redirect
import redis
import uuid
import requests
import ServerConfig

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0, password=123)
token_expires_time = ServerConfig.get('token_expires_time')
expires_time = ServerConfig.get('expires_time')

# ############# Helper Function ####################
def generateUuid(code_for):
    token = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return token

# ############# Token/Session Manager ###############
class TokenUtil:
    def setToken(self, uc_token, TokenInfo):
        r.hmset(uc_token, TokenInfo)
        return r.expire(uc_token, token_expires_time)

    def getToken(self, uc_token):
        return r.hgetall(uc_token)

    def delToken(self, uc_token):
        return r.delete(uc_token)

TokenUtil = TokenUtil()

class GlobalSessions:
    def sessions():
        pass


# ############# Web Router #########################


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        view_before = request.form.get('view_before')
        app_code = request.form.get('app_code')
        app_domain = request.url_root
        if username and password:
            token = generateUuid('token')
            sessionid = generateUuid('sessionid')
            TokenInfo = {'username': username,
                         'sessionid': sessionid}
            TokenUtil.setToken(token, TokenInfo)
            res = make_response(redirect(app_domain))
            req = requests.get(app_domain+'/token/'+token)
            tokenInfo = {''}
        return render_template('login.html')
    view_before = request.args.get('view_before') if request.args.get('view_before') else url_for('show_user', _external=True)
    app_code = request.args.get('app_code') if request.args.get('app_code') else 'uc'
    expires = request.args.get('expires') if request.args.get('expires') else expires_time
    return render_template('login.html', view_before=view_before, app_code=app_code, expires=expires)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
