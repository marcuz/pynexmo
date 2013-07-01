#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 Marco Londero <marco.londero@linux.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import json
import urllib
import urllib2
import urlparse
import math

api_url = "https://rest.nexmo.com/sms/json"
api_user = "changeme"
api_pass = "changeme"
num_from = {'it': '39**********', 'uk': '44*********'}

sms_chars = 160


def __url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor)).replace("#","%23")


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

    final_url = "%s?username=%s&password=%s&from=%s&to=%s&text=%s" % (api_url,
                api_user, api_pass, sms_from, sms_to, sms_msg)

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
