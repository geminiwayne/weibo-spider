#-*-coding:utf8-*-
# author: dong wang  Melbourne Uni
#store cookies and userid,topic
userid=[];

cookies=[""];

topic=[u"2016美国选举",u"2016美国总统选举",u"美国大选",u"2016美国总统",u"2016希拉里",u"2016川普",u"希拉里vs川普",u"2016美国总统大选",u"总统竞选",u"美国总统竞选",u"特朗普"];
#store google translate api key
translate_api=[''
]

#get cookies and userid
def getcookies(index):
 x=-1
 user=0
 cok=''
 for elem in range(0,44):
    if index==x:
        user=userid[x]
        cok=cookies[x]
    else:
        x=x+1
 return user,cok
#get topic
def gettopic(index):
    x=-1
    weibo_topic=''
    for elem in range(0,2):
       if index==x:
          weibo_topic=topic[x]
       else:
          x=x+1
    return weibo_topic

#get translate api
def getapi(index):
    x=-1
    trans_api=''
    for elem in range(0,19):
        if index==x:
            trans_api=translate_api[x]
        else:
            x=x+1
    return trans_api
