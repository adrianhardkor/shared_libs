#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)

# hostname = 'ARC UAT1 HUH CMR 01'
# print(hostname)

hexx = '46 75 63 6b 20 74 65 63 68 6e 69 63 6f 6c 6f 72 20 6d 6f 64 65 6d 73 2c 20 74 68 65 79 20 77 6f 6e 27 74 20 73 63 61 6e 20 73 6f 20 6e 6f 77 20 49 20 68 61 76 65 20 74 6f 20 74 79 70 65 20 74 68 65 20 6d 6f 74 68 65 72 20 66 75 63 6b 65 72 27 73 20 69 6e 20 62 79 20 68 61 6e 64 2e 20'

print(bytes.fromhex(hexx).decode('utf-8'))

import wcommon as wc
# wc.sendmail('adrian.krygowski@wowinc.com', 'test1', '12')
