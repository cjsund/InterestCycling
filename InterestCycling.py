#!/usr/bin/python
#coding=utf-8

import urllib2
import smtplib
import os


from sgmllib import SGMLParser
from email.mime.text import MIMEText
from config import *


path = os.getcwd()
url_html = urllib2.urlopen('http://www.dongfanghong.com.cn/bbs/forum.php?mod=forumdisplay&fid=11&filter=author&orderby=dateline').read()
html = unicode(url_html, 'GBK').encode('UTF-8')
mail_list = Mail_List
print Mail_User

class Send_Mail(object):

    def __init__(self, to, whois=Mail_From):
        self.whois = whois
        self.to = to

    def mail_body(self, subject=u"东方红二手更新", content="This is test mail.", charset="utf-8", subtype='html'):
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
        self.getdata = True
        for k,v in attrs:
        	if k == 'class' and v == 'xst':
        		self.flag = True
        		href = [ v for k, v in attrs if k == 'href']
        		if href:
        			self.IDlist.append(href)
        		return
        
    def end_a(self):
        if self.getdata:
            self.getdata = False

    def handle_data(self, text):
        if self.getdata:
            self.IDlist.append(text)
            
    def printID(self):
        for i in self.IDlist:
            print i

class WriteMail(object):

	def __init__(self):
		self.setp = 4
		self.setp_url = 1
		self.setp_title1 = 0
		self.setp_title2 = 2

		self.analyze = GetIdList()
		self.analyze.feed(html)

		self.old_url = open(os.path.join(path, "old_url.log"), 'r').read().strip()
		self.new_url = self.point_url = str(self.analyze.IDlist[self.setp_url])[2:-2]
		if self.new_url == self.old_url:
			print "No change."
			import sys
			sys.exit(0)
		

	def write(self):
		with open(os.path.join(path, "mail_body.txt"), 'w') as self.mail_body:
			#try:
			while True:
				self.new_url = str(self.analyze.IDlist[self.setp_url])[2:-2]
				self.new_title1 = str(self.analyze.IDlist[self.setp_title1])
				self.new_title2 = str(self.analyze.IDlist[self.setp_title2])
				if self.new_url == self.old_url:
					break
				self.mail_body.write("<a href=""http://www.dongfanghong.com.cn/bbs/%s"">[%s]%s</a><br /></br>\n" % (self.new_url, self.new_title1, self.new_title2))
				self.setp_url += self.setp
				self.setp_title1 += self.setp
				self.setp_title2 += self.setp

		with open(os.path.join(path, "old_url.log"), 'w') as old_url:
			old_url.write(self.point_url)
		send_mail = Send_Mail(to=mail_list)
		send_mail.mail_body(content=open(os.path.join(path, "mail_body.txt"), 'r').read())
		send_mail.send()
			#except IndexError:
			#	#print e
			#	print "len(use.IDlist) %s " % len(self.analyze.IDlist)
       		#	print self.setp_url
       		#	print self.new_url
       		#	print self.new_title1
       		#	print self.new_title2
       		#	import sys
       		#	sys.exit(1)

use = WriteMail()
use.write()

