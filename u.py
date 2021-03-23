#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import skinny
S = skinny.SKINNY('skinnyapi.arc.ninjaneers.net')

PATH = '/var/lib/jenkins/Modems'
for ip in wc.exec2('ls ' + PATH).split('\n'):
	if ip.startswith('10') is False: continue
	ip = '.'.join(ip.split('.')[0:4])
	print(ip)
	wc.pairprint(ip, S.GetSQC(ip))
	exit(0)
 
