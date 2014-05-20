#encoding=utf-8
'''
AliExpress SDK for Python3
written by kk, fkfkbill#gmail.com
'''
__author__ = "kK"


from hashlib import sha1
import hmac
from urllib import request
from urllib import parse
from datetime import datetime

try:import simplejson as json
except:import json


def _aop_signature(appsecret,sig_url=None,**kwargs):
    '''
字典序排序并生成aop签名
'''
    #先将字典转换成序列，用序列自带的sort作排序。
    a=[(s,kwargs[s]) for s in kwargs]
    a.sort()
    result="".join(["%s%s"%(s[0],s[1]) for s in a])
    #hmac_sha1
    if sig_url!=None:
        #api signature
        #part of url is needed
        result=sig_url+result
    print(result)
    signature=hmac.new(
        appsecret.encode("utf-8"),
        result.encode("utf-8"),
        sha1
    ).hexdigest() #十六进制
    return str(signature).upper()


def _aop_timestamp():
    '''
时间戳
'''
    return int(datetime.now().timestamp()*1000)


def genAuthUri(appkey,appsecret,redirect_uri,state=""):
    '''
生成用户认证的url
NOTE:
appkey:same as client_id
'''
    auth_uri="http://gw.api.alibaba.com/auth/authorize.htm?" \
             "site=aliexpress&" \
             "client_id=%s&" \
             "state=%s&" \
             "redirect_uri=%s&"%(appkey,state,redirect_uri)
    auth_uri+="_aop_signature=%s"%(_aop_signature(appsecret,
                                                 client_id=appkey,
                                                 redirect_uri=redirect_uri,
                                                 site="aliexpress",
                                                 state=state))
    return auth_uri


def getToken(appkey,appsecret,redirect_uri,code):
    '''
用户认证之后，根据获得的临时令牌“code”，获取refreshtoken和accesstoken。
'''
    get_token_uri="https://gw.api.alibaba.com/openapi/http/1/system.oauth2/getToken/" \
                  "%s?" \
                  "grant_type=authorization_code&" \
                  "need_refresh_token=true&" \
                  "client_id=%s&" \
                  "client_secret=%s&" \
                  "redirect_uri=%s&" \
                  "code=%s" % (appkey,appkey,appsecret,redirect_uri,code)
    #以post模式请求数据。
    #别忘记decode，然后让json转回python的dict
    result=json.loads(request.urlopen(get_token_uri,b"").read().decode("utf-8"))
    return result


def refreshAccesstoken(appkey,appsecret,refresh_token):
    '''
用refreshtoken去更新accesstoken。
'''
    get_token_uri="https://gw.api.alibaba.com/openapi/http/1/system.oauth2/getToken/" \
                  "%s?" \
                  "grant_type=refresh_token&" \
                  "client_id=%s&" \
                  "client_secret=%s&" \
                  "refresh_token=%s" % (appkey,appkey,appsecret,refresh_token)
    #以post模式请求数据。
    #别忘记decode，然后让json转回python的dict
    result=json.loads(request.urlopen(get_token_uri,b"").read().decode("utf-8"))
    return result


def postponeToken(appkey,appsecret,refresh_token,access_token):
    '''
换取新的refreshtoken。
注意：
如果当前时间离refreshToken过期时间在30天以内，
那么可以调用postponeToken接口换取新的refreshToken；
否则会报错（400，bad request）。详情参见开放平台文档
'''
    get_token_uri="https://gw.api.alibaba.com/openapi/param2/1/system.oauth2/postponeToken/" \
                  "%s?" \
                  "client_id=%s&" \
                  "client_secret=%s&" \
                  "refresh_token=%s&" \
                  "access_token=%s" % (appkey,appkey,appsecret,refresh_token,access_token)
    #别忘记decode，然后让json转回python的dict
    result=json.loads(request.urlopen(get_token_uri).read().decode("utf-8"))
    return result


class aliexp_api_frame:
    def _api_uri_gen(self,base_uri,appkey,dic):
        '''
    产生标准的api uri.
    '''
        if base_uri[-1]!="/":
            base_uri+="/"
        return base_uri+appkey+"?"+parse.urlencode(dic)


    def __init__(self,
                 appkey,
                 appsecret=None,
                 with_time=False,
                 **kwargs):
        '''
    使用方式：
    appkey必填，如果给出appsecret，则将自动计算_aop_signature。
    with_time若为True，则将附上_aop_timestamp
    应用级参数都放入kwargs中，注意大多数api需要access_token，故不应忘记。
    '''
        if with_time:
            #必须先判断是否要加入时间戳。
            #因为签名因子制作的时候需要加入时间戳
            kwargs.update({"_aop_timestamp":_aop_timestamp()})
        if appsecret:
            #to make the signature for an api,some part of the url is needed.
            kwargs.update({"_aop_signature":_aop_signature(
                appsecret,
                "param2/1/aliexpress.open/api.%s/%s"%(self.__class__.__name__,appkey),
                **kwargs
            )})
        self.api_uri=self._api_uri_gen(
            "http://gw.api.alibaba.com:80/openapi/param2/1/aliexpress.open/api.%s/"% \
                self.__class__.__name__,
            appkey,
            kwargs
        )
        print(self.api_uri) # for debugging usage.


    def query(self):
        '''
    执行查询
    '''
        return json.loads(request.urlopen(self.api_uri).read().decode("utf-8"))


#交易
class findOrderTradeInfo(aliexp_api_frame):pass
#class findOrderBuyerInfo(aliexp_api_frame):pass
#class findOrderReceiptInfo(aliexp_api_frame):pass
class findOrderBaseInfo(aliexp_api_frame):pass
class findOrderListSimpleQuery(aliexp_api_frame):pass
#class requestPaymentRelease(aliexp_api_frame):pass
#class updateDeliveriedConfirmationFile(aliexp_api_frame):pass
#class findLoanListQuery(aliexp_api_frame):pass
class findOrderById(aliexp_api_frame):pass
class findOrderListQuery(aliexp_api_frame):pass
