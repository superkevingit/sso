#!/usr/bin/env python
# encoding: utf-8
import redis
import uuid


def generateUuid(code_for):
    token = str(uuid.uuid3(uuid.uuid1(), str(code_for)).hex)
    return token

r = redis.StrictRedis(host='localhost', port=6379, db=0, password=123)
uc_token = generateUuid('uc_token')
user_id = generateUuid('user_id')
global_session_id = generateUuid('global_session_id')
TokenInfo = {
    'user_id': user_id,
    'ssoClient': 'App',
    'globalId': global_session_id
}
token_expire_time = int('60')


############## Token/Session Manager ###############
class TokenUtil:
    def setToken(self, uc_token, TokenInfo):
        r.hmset(uc_token, TokenInfo)
        return r.expire(uc_token, token_expire_time)

    def getToken(self, uc_token):
        return r.hgetall(uc_token)

    def delToken(self, uc_token):
        return r.delete(uc_token)


token = TokenUtil()
print token.setToken(uc_token, TokenInfo)
print token.getToken(uc_token)


#class GlobalSessions:
#    def sessions():

############## Web Router #########################
