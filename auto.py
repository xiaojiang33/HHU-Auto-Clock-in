import requests
from Crypto.Cipher import AES
import base64
from random import randrange
from bs4 import BeautifulSoup
import urllib3
import re
import time
import datetime
import json
import argparse
import sys


class DaKa:
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.key = None
        self.aes_crypt = None
        self.login_url = "http://authserver.hhu.edu.cn/authserver/login?service=http%3A%2F%2Fmy.hhu.edu.cn%2Fportal-web%2Fj_spring_cas_security_check"
        self.base_url = "http://dailyreport.hhu.edu.cn/pdc/form/list"
        self.save_url = "http://dailyreport.hhu.edu.cn/pdc/formDesignApi/S/gUTwwojq"
        self.submit_url = "http://dailyreport.hhu.edu.cn/pdc/formDesignApi/dataFormSave?wid=A335B048C8456F75E0538101600A6A04"
        self.info = None
        self.sess = requests.Session()

        print(self.username, self.password)
    def login(self):
        def __login_passwd_aes(mode=AES.MODE_CBC):
            def __random_str(num):
                chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
                return ''.join([chars[randrange(len(chars))] for i in range(num)])

            passwd_with_salt, iv = __random_str(64) + self.password, __random_str(16)
            self.aes_crypt = AESCrypt(self.key, mode, iv, passwd_with_salt)
            return self.aes_crypt.encrypt()

        try:
            login_res = self.sess.get(self.login_url)
            login_html = login_res.content.decode()
            login_soup = BeautifulSoup(login_html, "html.parser")
            self.key = login_soup.find("input", attrs={'id':'pwdDefaultEncryptSalt'})['value']
            login_data = {
                "username": self.username,
                "password": __login_passwd_aes(),
                "lt": login_soup.find("input", attrs={'name':'lt'})['value'],
                "dllt": login_soup.find("input",attrs={'name':'dllt'})['value'],
                "execution": login_soup.find("input", attrs={'name':'execution'})['value'],
                "_eventId": login_soup.find("input", attrs={'name':'_eventId'})['value'],
                "rmShown": login_soup.find("input", attrs={'name':'rmShown'})['value']
            }
            self.sess.post(self.login_url, data=login_data)  # session???cookies?????????????????????key??????
        except Exception as e:
            print("????????????????????????????????????????")
            exit(1)

    def get_info(self):
        def __get_date():
            today = datetime.date.today()
            return "%4d/%02d/%02d" % (today.year, today.month, today.day)
        urllib3.disable_warnings()

        res1 = self.sess.get(self.base_url, headers=self.headers, allow_redirects=True)
        res1 = self.sess.get(self.save_url, headers=self.headers, allow_redirects=True)
        content1 = res1.content.decode()
       # print(content1)
        username = re.search('"XGH_336526":"(.*?)"', content1).group(1)
        name = re.search('"XM_1474":"(.*?)"', content1).group(1)
        IDnumber = re.search('"SFZJH_859173":"(.*?)"', content1).group(1)
        yuanxi = re.search('"SELECT_941320":"(.*?)"', content1).group(1)
        nianji = re.search('"SELECT_459666":"(.*?)"', content1).group(1)
        zhuanye = re.search('"SELECT_814855":"(.*?)"', content1).group(1)
        banji = re.search('"SELECT_525884":"(.*?)"', content1).group(1)
        sushe = re.search('"SELECT_125597":"(.*?)"', content1).group(1)
        mengpai = re.search('"TEXT_950231":"(.*?)"', content1).group(1)
        dianhua = re.search('"TEXT_937296":"(.*?)"', content1).group(1)
        tiwen = re.search('"RADIO_6555":"(.*?)"', content1).group(1)
        zaixiao = re.search('"RADIO_535015":"(.*?)"', content1).group(1)
        benren = re.search('"RADIO_891359":"(.*?)"', content1).group(1)
        tongzhuren = re.search('"RADIO_372002":"(.*?)"', content1).group(1)
        zhonggao = re.search('"RADIO_618691":"(.*?)"', content1).group(1)

        save_data = {
            'DATETIME_CYCLE':__get_date(),
            'XGH_336526':username,     #??????
            'XM_1474':name,            #??????
            'SFZJH_859173': IDnumber,  #????????????
            'SELECT_941320':yuanxi,    #??????
            'SELECT_459666':nianji,    #??????
            'SELECT_814855':zhuanye,   #??????
            'SELECT_525884':banji,     #??????
            'SELECT_125597':sushe,     #??????
            'TEXT_950231':mengpai,     #?????????
            'TEXT_937296':dianhua,     #????????????
            'RADIO_6555':tiwen,        #??????
            'RADIO_535015':zaixiao,    #????????????
            'RADIO_891359':benren,     #??????????????????
            'RADIO_372002':tongzhuren, #?????????????????????
            'RADIO_618691':zhonggao    #14?????????????????????????????????
        }


        self.info = save_data
    def post(self):
        res = self.sess.post(self.submit_url+'&userId='+self.username, data=self.info)
        #print(self.info)
        return res


def main(username, password):
    print("1. ??????????????????????")
    dk = DaKa(username, password)
    print("2. ????????????????")
    dk.login()
    print("3. ??????????????????????")
    dk.get_info()
    print("4. ????????????%s????????????????" % dk.info['XM_1474'][0])
    res = dk.post()
    if '{"result":true}' in res.content.decode():
        print('??????%s??????????????????????' % dk.info['XM_1474'][0])
    else:
        print('??????????????????????')

class AESCrypt:
    """
    csu encrypt.js?????????????????????
    function getAesString(data, key0, iv0) {
        key0 = key0.replace(/(^\s+)|(\s+$)/g, "");
        var key = CryptoJS.enc.Utf8.parse(key0);
        var iv = CryptoJS.enc.Utf8.parse(iv0);
        var encrypted = CryptoJS.AES.encrypt(data, key, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });
        return encrypted.toString();
    }
    function encryptAES(data, aesKey) {
        if (!aesKey) {
            return data;
        }
        var encrypted = getAesString(randomString(64) + data, aesKey, randomString(16));
        return encrypted;
    }
    var $aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
    var aes_chars_len = $aes_chars.length;
    function randomString(len) {
        var retStr = '';
        for (i = 0; i < len; i++) {
            retStr += $aes_chars.charAt(Math.floor(Math.random() * aes_chars_len));
        }
        return retStr;
    }
    """

    def __init__(self, key, mode, iv, data):
        self.key = key.encode('utf-8')
        self.mode = mode
        self.iv = iv.encode('utf-8')
        self.data = self.pkcs7(data)
        self.cipher = AES.new(self.key, self.mode, self.iv)
        self.encryptedStr = None

    def encrypt(self):
        self.encryptedStr = base64.b64encode(self.cipher.encrypt(self.data))
        return self.encryptedStr

    def pkcs7(self, data, block_num=16):
        """
        ?????????????????????????????????block_num??????????????????????????????????????????
        :return:
        """
        pad = block_num - len(data.encode('utf-8')) % block_num
        data = data + pad * chr(pad)
        return data.encode('utf-8')


if __name__ == "__main__":
    print(sys.argv)
    username = sys.argv[1]
    password = sys.argv[2]
    try:
        main(username, password)
    except Exception:
        exit(1)
