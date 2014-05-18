#encoding=utf-8
'''
AliExpress SDK for Python3
written by kk
'''
__author__ = "kK"


from urllib import request
from hashlib import sha1
import hmac
from urllib import request

try:import simplejson as json
except:import json


def gen_auth_url(appkey,appsecret,redirect_url,state=""):
    '''
generate oauth2 login url
NOTE:
appkey:same as client_id
'''
    aop_signature_data="client_id%s" \
                       "redirect_uri%s" \
                       "sitealiexpress" %(appkey,redirect_url)
    if state:
        aop_signature_data+="state"+state
    aop_signature=hmac.new(appsecret.encode("utf-8"),aop_signature_data.encode("utf-8"),sha1).hexdigest()
    aop_signature=str(aop_signature).upper()
    auth_url="http://gw.api.alibaba.com/auth/authorize.htm?" \
             "client_id=%s&" \
             "site=aliexpress&" \
             "redirect_uri=%s&"%(appkey,redirect_url)
    if state:
        auth_url+="state=%s&"%state
    auth_url+="_aop_signature=%s"%(aop_signature)
    return auth_url


def get_token(appkey,appsecret,redirect_url,code):
    '''
when temporary code send to your site in querystring named "code",
get the token.
'''
    get_token_url="https://gw.api.alibaba.com/openapi/http/1/system.oauth2/getToken/" \
                  "%s?" \
                  "grant_type=authorization_code&" \
                  "need_refresh_token=true&" \
                  "client_id=%s&" \
                  "client_secret=%s&" \
                  "redirect_uri=%s&" \
                  "code=%s" % (appkey,appkey,appsecret,redirect_url,code)
    result=json.loads(request.urlopen(get_token_url,b"").read().decode("utf-8"))
    return result


def refresh_accesstoken(appkey,appsecret,refresh_token):
    '''
get access_token with refresh_token
'''

