#-*-coding:utf8-*-
# author: dong wang  Melbourne Uni
from __future__ import print_function
from googleapiclient.discovery import build
import re
import string
import sys
import os
import urllib
import urllib2
import time
from bs4 import BeautifulSoup
import requests
import couchdb
from lxml import etree
import cookies
from textblob import TextBlob

#to store userid and cookies
maxpage=101
usernum=44
topicnum=0
api_num=19
api_count=0
translateapi_count=0
couch = couchdb.Server('http://127.0.0.1:5984/')
db = couch['weibo']
pagenum=1
result = ""
urllist_set = set()
word_count = 0
#to control the speed of crawling
crawling_count=0
SearchWord=cookies.gettopic(topicnum)
#to store the number of forward,comment
num_zan=[]
num_forward=[]
num_comment=[]
num_date=[]
pattern = r"\d+\.?\d*"

print ('prepare to crawl...')

while crawling_count<usernum:
    try:
      user_id,user_cookie=cookies.getcookies(crawling_count)
      cookie = {"Cookie":user_cookie }
      url = 'http://weibo.cn/u/%d?filter=1&page=2'%(int)(user_id)
      html = requests.get(url, cookies = cookie).content
      selector = etree.HTML(html)
      urllist_set = set()
      
      for page in range(pagenum,maxpage):
             #to get xml page
             url = 'http://weibo.cn/u/%d?filter=1&page=%d'%((int)(user_id),page)
             url = 'http://weibo.cn/search/mblog?hideSearchFrame=&keyword=%s&page=%d'%(SearchWord,pagenum)
             lxml = requests.get(url, cookies = cookie).content
             contentnum=0
             #to crawl only text
             selector = etree.HTML(lxml)
             content = selector.xpath('//span[@class="ctt"]')
             for each in content:
                text = each.xpath('string(.)')
                if word_count>=4:
                   text = "%d :"%(word_count-3) +text+"\n\n"
                else :
                   text = text+"\n\n"
                result = result + text
                word_count += 1
             word_str=result.splitlines()
             info = selector.xpath("//div[@class='c']")
             #to get how people support this oppinion,forward,comment
             if len(info) > 3:
                for i in range(0,len(info)-2):
                    str_zan = info[i].xpath("div/a/text()")
                    for each in str_zan:
                        if u'赞' in each:
                           guid = re.findall(pattern, each, re.M)
                           num_zan.append(guid[0])
                        if u'转发' in each:
                           relay = re.findall(pattern, each, re.M)
                           num_forward.append(relay[0])
                        if u'评论' in each:
                           comment = re.findall(pattern, each, re.M)
                           num_comment.append(comment[0])
             str_date=selector.xpath('//span[@class="ct"]')
             for each in str_date:
                 date_text = each.xpath('string(.)')
                 num_date.append(date_text)
             api_count=api_count+1
                 # to split each users' senetences
             for newresult in word_str:
                if len(newresult)>1:
                    if api_count<=80 and translateapi_count<api_num:
                       api=cookies.getapi(translateapi_count)
                       service = build('translate', 'v2',
                       developerKey=(api))
                       #translate content from chinese to english
                       content=service.translations().list(source='zh-CN',target='en',q=newresult).execute()
                       str_content=(str)(content)
                       testimonial=TextBlob(str_content)
                       #transltate date from chinese to english
                       date_content=service.translations().list(source='zh-CN',target='en',q=num_date[contentnum].encode('utf-8')).execute()
                       date=(str)(date_content)
                       #save documents to couchdb
                       doc = {'content': content,'polarity':testimonial.sentiment.polarity,'subjectivity':testimonial.sentiment.subjectivity,'zan':num_zan[contentnum],'forward':num_forward[contentnum],'comment':num_comment[contentnum],'date':date}
                       db.save(doc)
                       contentnum=contentnum+1
                    else:
                       api_count=0
                       translateapi_count=translateapi_count+1
             print (pagenum,': is crawled')
             pagenum=pagenum+1
             crawling_count=crawling_count+1
             time.sleep(5)
             if crawling_count==usernum:
                crawling_count=0
             break
      #change related topic
      if pagenum==maxpage and topicnum<2:
         topicnum=topicnum+1
         SearchWord=cookies.gettopic(topicnum)
         pagenum=1
      if pagenum==maxpage and topicnum==2:
         crawling_count=100
    except:
        crawling_count=crawling_count+1
        print('to find a valid userid and cookies')
        if crawling_count==usernum:
                crawling_count=0
print ('weibo spider is finished')
