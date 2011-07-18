#!/usr/bin/python

import sys
import json
import urllib, urllib2
import urlparse

api_url = "http://rest.nexmo.com"
api_path = "sms/json?"
api_user = "changeme"
api_pass = "changeme"
num_from = {'it': '0039**********', 'nl': '0031*********'}

def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def fetch(url):
    return json.load(urllib2.urlopen(url))

def select_from(numbers):
    for num in numbers:
        print("[%s] %s") % (num, numbers[num])
    try:
        fromnum = raw_input("From: ")
        return numbers[fromnum]
    except KeyError:
        sys.exit("No such number. You suuuck! ktnxbye")

def select_to():
    c = raw_input("To: ")
    if c.isdigit():
        return c
    return False

def select_message():
    return raw_input("Message: ")

def confirm(sender, recipient, message):
    print("\nSummary:\n")
    print("From: %s") % sender
    print("To: %s") % recipient
    print("Message [%s]: %s") % (str(len(message)), message)
    c = raw_input("\nConfirm sending [y/n]? ")
    if c == "y":
        return True
    return False

sms_from = select_from(num_from)
sms_to = select_to()
sms_msg = select_message()

if not sms_to:
    sys.exit("'To' field is not a valid number, ktnxbye.")

final_url = "%s/%susername=%s&password=%s&from=%s&to=%s&text=%s" % (api_url, api_path, api_user, api_pass, sms_from, sms_to, sms_msg)

if confirm(sms_from, sms_to, sms_msg):
    res = fetch(url_fix(final_url))
    if res['messages'][0]['status'] == "0":
        print("SMS succesfully sent to '%s'. Available balance: %s") % (sms_to, res['messages'][0]['remaining-balance'])
    else:
        print("Something went wrong, you suuuck (or maybe API do)! Error message: '%s'") % res['messages'][0]['error-text']

# EOF
