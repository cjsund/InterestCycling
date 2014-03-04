#!/usr/bin/python
#coding=utf-8

import urllib2
import smtplib
import sys
import os

import chardet

from sgmllib import SGMLParser
from email.mime.text import MIMEText
from collections import OrderedDict

from config import *

#Html_List = {"www.dongfanghong.com.cn": "http://www.dongfanghong.com.cn/bbs/forum.php?mod=forumdisplay&fid=11&filter=author&orderby=dateline",
#            "www.fengyunbike.com": "http://www.fengyunbike.com/forum.php?mod=forumdisplay&fid=9&filter=author&orderby=dateline",
#            "bbs.cyclist.cn": "http://bbs.cyclist.cn/forum.php?mod=forumdisplay&fid=25&filter=author&orderby=dateline",
#            "bbs.chinabike.net": "http://bbs.chinabike.net/forum.php?mod=forumdisplay&fid=35&filter=author&orderby=dateline",
#            "bbs.biketo.com": "http://bbs.biketo.com/forum.php?mod=forumdisplay&fid=39&filter=author&orderby=dateline"}
#Web_List = ["www.dongfanghong.com.cn", "www.fengyunbike.com", "bbs.cyclist.cn", "bbs.chinabike.net", "bbs.biketo.com"]

path = os.getcwd()


class Send_Mail(object):

    def __init__(self, to, whois=Mail_From):
        self.whois = whois
        self.to = to

    def mail_body(self, subject=u"二手更新", content="This is test mail.", charset="utf-8", subtype='html'):
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
        self.analyze.feed(gethtml(Html_List.get(self.bbs_name)))

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
        with open(os.path.join(path, "mail_body.txt"), 'a') as self.mail_body:
            #try:
            self.mail_body.write("<h3>%s</h3><br /></br>\n" % self.bbs_name)
            while True:
                if self.setp_url >= self.len_num or self.setp_title1 >= self.len_num:
                    return
                self.new_url = self.analyze.IDlist[self.setp_url]
                self.new_title1 = self.analyze.IDlist[self.setp_title1]
                if self.new_url == self.old_url:
                    return
                if self.bbs_name == "www.dongfanghong.com.cn":
                    self.mail_body.write("<a href=""http://%s/bbs/%s"">%s</a><br /></br>\n" % (self.bbs_name, self.new_url, self.new_title1))
                else:
                    self.mail_body.write("<a href=""http://%s/%s"">%s</a><br /></br>\n" % (self.bbs_name, self.new_url, self.new_title1))
                self.setp_url += self.setp
                self.setp_title1 += self.setp





def gethtml(bbs_name):
    url_html = urllib2.urlopen(bbs_name, timeout=60).read()
    html_encode = chardet.detect(url_html).get('encoding', 'utf-8')
    location_encode = sys.getfilesystemencoding()
    return url_html.decode(html_encode, 'ignore').encode(location_encode)


if __name__ == '__main__':

    with open(os.path.join(path, "mail_body.txt"), 'w') as mail_body:
        mail_body.truncate()
        mail_body.write("退订请回复邮件。\n")
    
    for name in Web_List:
        use = WriteMail(bbs_name=name)
        use.readlog()
        use.writelog()
        use.write()
    
    send = Send_Mail(to=Mail_List)
    send.mail_body(content=open(os.path.join(path, "mail_body.txt"), 'r').read())
    send.send()

