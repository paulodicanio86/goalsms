
import urllib
import urllib2
import json
from pprint import pprint

with open('sms_config.json') as data_file:
    data_config = json.load(data_file)
pprint(data_config)

encoding = 'utf-8'


def getMessages(uname, hashCode, inboxID):
    data = urllib.urlencode({'username': uname, 'hash': hashCode, 'inbox_id' : inboxID})
    data = data.encode(encoding)
    request = urllib2.Request(data_config['url_receive'] + '/get_messages/?')
    f = urllib2.urlopen(request, data)
    fr = f.read()
    return(fr)

def getInboxes(uname, hashCode):
    data = urllib.urlencode({'username': uname, 'hash': hashCode})
    data = data.encode(encoding)
    request = urllib2.Request(data_config['url_receive'] + '/get_inboxes/?')
    f = urllib2.urlopen(request, data)
    fr = f.read()
    return(fr)



resp =  getInboxes(data_config['uname'], data_config['hash'])

resp2 =  getMessages(data_config['uname'], data_config['hash'], '9')
resp3 =  getMessages(data_config['uname'], data_config['hash'], '10')


print (resp)
print (resp2)
print (resp3)

