#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

PATH = '/var/lib/jenkins/Modems/'
for fname in wc.exec2('ls ' + PATH).split('\n'):
	wc.jd(json.loads(wc.read_file(PATH + fname)))
