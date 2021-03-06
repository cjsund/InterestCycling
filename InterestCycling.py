#!/usr/bin/python
#coding=utf-8

import urllib2
import smtplib
import sys
import os

import chardet

from datetime import datetime
from sgmllib import SGMLParser
from email.mime.text import MIMEText
from collections import OrderedDict

from config import *

path = sys.path[0]
mail_status = False
Keyword_List = ["坐垫", "把组", "弯把", "3t", "Specialized", "selle", "deda"]
now_time = datetime.now().strftime("%Y%m%d%H%M")

class Send_Mail(object):

    def __init__(self, to, whois=Mail_From):
        self.whois = whois
        self.to = to

    def mail_body(self, subject="Second-hand bicycle parts %s" % now_time, content="This is test mail.", charset="utf-8", subtype='html'):
        self.msg = MIMEText(content, subtype, charset)
        self.msg['Subject'] = subject
        self.msg['from'] = self.whois
        self.msg['To'] = self.to

    def send(self, user=Mail_User, password=Mail_Passwd, smtp_server=Mail_Smtp, port="25"):
        smtp = smtplib.SMTP(smtp_server, port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, password)
        for mail in self.to.split(","):
            if smtp.sendmail(self.whois, mail, self.msg.as_string()):
                print "Send Mail to %s" % mail


class GetIdList(SGMLParser):

    def reset(self):
        self.IDlist = []
        self.flag = False
        self.getdata = False
        self.verbatim = 0
        SGMLParser.reset(self)
        
    def start_th(self, attrs):
        if self.flag == True:
            self.verbatim +=1
            return
        for k,v in attrs:
            if k == 'class' and v == 'new':
                self.flag = True
                return

    def end_th(self):
        if self.verbatim == 0:
            self.flag = False
        if self.flag == True:
            self.verbatim -=1

    def start_a(self, attrs):
        if self.flag == False:
            return
        for k,v in attrs:
            if k == 'class' and v == 'xst' or k == 'class' and v == 's xst':
                self.getdata = True
                href = [ v for k, v in attrs if k == 'href']
                if href:
                    self.IDlist.append(href[0])

        
    def end_a(self):
        if self.getdata:
            self.getdata = False

    def handle_data(self, text):
        if self.getdata:
            self.IDlist.append(text)
            

class WriteMail(object):

    def __init__(self, bbs_name):
        self.setp = 2
        self.setp_url = 0
        self.setp_title1 = 1

        self.bbs_name = bbs_name

        self.analyze = GetIdList()
        self.analyze.feed(gethtml(Html_List.get(self.bbs_name), self.bbs_name))

    def readlog(self):
        self.old_url_list = OrderedDict()
        with open(os.path.join(path, "OrderedDict.log"), 'r') as order:
            for i in order:
                name, url = i.split(":", 1)
                self.old_url_list[name] = url
        self.old_url = self.old_url_list.get(self.bbs_name).strip()
        self.new_url = self.point_url = str(self.analyze.IDlist[self.setp_url])
        self.len_num = len(self.analyze.IDlist) - 1
        if self.new_url == self.old_url:
            print "%s No change." % self.bbs_name
            return
        
    def writelog(self):
        self.old_url_list[self.bbs_name] = self.point_url + "\n"
        with open(os.path.join(path, "OrderedDict.log"), 'w') as order:
            for i in Web_List:
                order.write("%s:%s" % (i, self.old_url_list.get(i)))


    def write(self):
        global mail_status
        with open(os.path.join(path, "mail_body.txt"), 'a') as self.mail_body:
            while True:
                if self.setp_url >= self.len_num or self.setp_title1 >= self.len_num:
                    return
                self.new_url = self.analyze.IDlist[self.setp_url]
                self.new_title1 = self.analyze.IDlist[self.setp_title1]
                if self.new_url == self.old_url:
                    return
                for keyword in Keyword_List:
                    if keyword in self.new_title1:
                        mail_status = True
                        if self.bbs_name == "www.dongfanghong.com.cn":
                            self.mail_body.write("<a href=""http://%s/bbs/%s"">%s</a><br /></br>\n" % (self.bbs_name, self.new_url, self.new_title1))
                        else:
                            self.mail_body.write("<a href=""http://%s/%s"">%s</a><br /></br>\n" % (self.bbs_name, self.new_url, self.new_title1))

                self.setp_url += self.setp
                self.setp_title1 += self.setp





def gethtml(url, url_name):
    url_html = urllib2.urlopen(url, timeout=60).read()
    html_encode = chardet.detect(url_html).get('encoding', 'utf-8')
    location_encode = sys.getfilesystemencoding()
    html_file_path = os.path.join(path, "html")
    html_file = os.path.join(html_file_path, "html_%s_%s" % (now_time, url_name))

    if not os.path.isdir(html_file_path):
        os.mkdir(html_file_path)

    html = url_html.decode(html_encode, 'ignore').encode(location_encode)
    with open(html_file , 'w') as html_file:
        html_file.write(html)
    return html


if __name__ == '__main__':

    with open(os.path.join(path, "mail_body.txt"), 'w') as mail_body:
        mail_body.truncate()
        mail_body.write("退订请回复邮件。\n<br /></br>")
    
    for name in Web_List:
        use = WriteMail(bbs_name=name)
        use.readlog()
        use.writelog()
        use.write()

    if mail_status:
        send = Send_Mail(to=Mail_List)
        send.mail_body(content=open(os.path.join(path, "mail_body.txt"), 'r').read())
        send.send()

