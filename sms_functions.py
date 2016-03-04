import urllib  # URL functions
import urllib2  # URL functions


def send_sms(number, content, data_config):
    encoding = 'utf-8'
    username = data_config['uname']
    sender = data_config['sender']
    hash_code = data_config['hash']
    test_flag = data_config['test_flag']  # real messages have test_flag = 0
    url = data_config['url_send']

    values = {'test': test_flag,
              'uname': username,
              'hash': hash_code,
              'message': content,
              'from': sender,
              'selectednums': number}

    post_data = urllib.urlencode(values)
    request = urllib2.Request(url, post_data)

    # print 'Attempt to send SMS ...'
    try:
        response = urllib2.urlopen(request)
        response_url = response.geturl()
        if response_url == url:
            print 'SMS sent!'
    except urllib2.URLError, error:
        # print 'Send failed!'
        print error.reason
