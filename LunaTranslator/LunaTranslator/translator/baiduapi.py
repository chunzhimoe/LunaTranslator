 
import requests 

from utils.config import globalconfig  
from translator.basetranslator import basetrans   
import hashlib
import urllib
import random 
class TS(basetrans):  
    def langmap(self):
        return  {"es":"spa","ko":"kor","fr":"fra","ja":"jp","cht":"cht"}
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query):  
        if self.config['APP ID'].strip()=="" or self.config['密钥'].strip()=="":
            return 
        else:
            appid = self.config['APP ID'].strip()
            secretKey = self.config['密钥'].strip()
  
        myurl = '/api/trans/vip/translate'

        fromLang = self.srclang   #原文语种
        toLang = self.tgtlang   #译文语种
        salt = random.randint(32768, 65536)
        q= query
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
        
        res=self.session.get('https://api.fanyi.baidu.com'+myurl,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).json()  
        self.countnum(query)
        return '\n'.join([_['dst'] for _ in res['trans_result']])  
          