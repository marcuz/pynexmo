#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Marco Londero <marco.londero@linux.it>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import sys
import json
import urllib
import urllib2
import urlparse
import math
import ConfigParser

api_url = "https://rest.nexmo.com/sms/json"
config = ConfigParser.ConfigParser()
config.read('config.ini')
api_key = config.get('default','api_key')
api_secret = config.get('default','api_secret')
num_from = config._sections['num_from']
sms_chars = 160


def __url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    unsplit = urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
    return unsplit.replace("#", "%23")


def __url_fetch(url):
    try:
        return json.load(urllib2.urlopen(url))
    except Exception, e:
        sys.exit("\nFailed to fetch API endpoint, exiting: %s" % e.reason)


def __select_from(numbers):
    for num in numbers:
        print("[%s] %s") % (num, numbers[num])
    try:
        fromnum = raw_input("From: ")
        return numbers[fromnum]
    except KeyError:
        sys.exit("No such number. You suuuck! ktnxbye")


def __select_to():
    c = raw_input("To: ")
    if c.isdigit():
        return c
    return False


def __select_message(retry):
    in_msg = "Message: "
    if retry:
        in_msg = "Message (not empty this time): "
    msg = raw_input(in_msg)
    if len(msg) > 0:
        return msg
    return __select_message(True)


def __confirm(sender, recipient, message, smsd):
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
    try:
        sms_from = __select_from(num_from)
        sms_to = __select_to()
        sms_msg = __select_message(False)
        sms_len = len(sms_msg)
        sms_num = math.ceil(float(sms_len) / sms_chars)
        sms_data = sms_len, sms_num
    except KeyboardInterrupt:
        sys.exit("\n\nRequest to quit, exiting.")

    if not sms_to:
        sys.exit("'To' field is not a valid number, ktnxbye.")

    final_url = "%s?api_key=%s&api_secret=%s&from=%s&to=%s&text=%s" % (api_url,
                api_key, api_secret, sms_from, sms_to, sms_msg)

    if __confirm(sms_from, sms_to, sms_msg, sms_data):
        success = False
        res = __url_fetch(__url_fix(final_url))
        print("")
        for s in range(int(res['message-count'])):
            out = "SMS %d/%d to '%s' " % (s + 1, sms_num, sms_to)
            if res['messages'][s]['status'] == "0":
                print(out + "ok (cost: %s, msgid: %s)" %
                      (res['messages'][s]['message-price'],
                       res['messages'][s]['message-id']))
                api_bal = res['messages'][s]['remaining-balance']
                success = True
            else:
                print(out + "failed: '%s'") % res['messages'][s]['error-text']
        if success:
            print("\nAvailable balance: %s, ktnxbye") % api_bal

if __name__ == "__main__":
    sys.exit(main())

# EOF
