#!/usr/bin/python

import sys
import json
import urllib, urllib2
import urlparse
import math

api_url = "http://rest.nexmo.com/sms/json"
api_user = "changeme"
api_pass = "changeme"
num_from = {'it': '0039**********', 'nl': '0031*********'}

sms_chars = 160

def url_fix(s, charset = 'utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def url_fetch(url):
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

def select_message(retry):
    in_msg = "Message: "
    if retry:
        in_msg = "Message (not empty this time): "
    msg = raw_input(in_msg)
    if len(msg) > 0:
        return msg
    return select_message(True)

def confirm(sender, recipient, message, smsd):
    sms_len, sms_num = smsd
    print("\nSummary:\n")
    print("From: %s") % sender
    print("To: %s") % recipient
    print("Message [%d char, %d sms]: %s") % (sms_len, sms_num, message)
    c = raw_input("\nConfirm sending [y/n]? ")
    if c == "y":
        return True
    return False

def main():
    sms_from = select_from(num_from)
    sms_to = select_to()
    sms_msg = select_message(False)
    sms_len = len(sms_msg)
    sms_num = math.ceil(float(sms_len) / sms_chars)
    sms_data = sms_len, sms_num

    if not sms_to:
        sys.exit("'To' field is not a valid number, ktnxbye.")

    final_url = "%s?username=%s&password=%s&from=%s&to=%s&text=%s" % (api_url,
            api_user, api_pass, sms_from, sms_to, sms_msg)

    if confirm(sms_from, sms_to, sms_msg, sms_data):
        success = False
        res = url_fetch(url_fix(final_url))
        print("")
        for s in range(int(res['message-count'])):
            out = "SMS %d/%d to '%s' " % (s + 1, sms_num, sms_to)
            if res['messages'][s]['status'] == "0":
                print(out + "ok.")
                api_bal = res['messages'][s]['remaining-balance']
                success = True
            else:
                print(out + "failed: '%s'") % res['messages'][s]['error-text']
        if success:
            print("\nAvailable balance: %s, ktnxbye") % api_bal

if __name__ == "__main__":
    sys.exit(main());

# EOF
