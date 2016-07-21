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
uc_expires = ServerConfig.get('uc_expires')

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
        view_token = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            token = generateUuid('token')
            TokenUtil.setToken(token, {'sessionid':'', 'username': username, 'app_tag': ''})
            req = requests.get(view_token, params=token)
            return req
            if not req:
                return {'msg':'token failed or expired!'}

        return render_template('login.html', view_before=view_before, view_token=view_token)
    return render_template('login.html', view_before=view_before, view_token=view_token)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
