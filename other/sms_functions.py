import urllib
import urllib2


def send_sms(number, content, data_config):
    encoding = 'utf-8'
    username = data_config['username']
    sender = data_config['sender']
    hash_code = data_config['hash']
    test_flag = data_config['test_flag']  # real messages have test_flag = 0
    url = data_config['url_send']

    values = {'test': test_flag,
              'username': username,
              'hash': hash_code,
              'message': content,
              'sender': sender,
              'numbers': number}

    post_data = urllib.urlencode(values)
    post_data = post_data.encode(encoding)
    request = urllib2.Request(url)

    # print 'Attempt to send SMS ...'
    try:
        f = urllib2.urlopen(request, post_data)
        fr = f.read()
        print(fr)
        print 'SMS sent!'
    except urllib2.URLError, error:
        # print 'Send failed!'
        print error.reason
