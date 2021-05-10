#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import js2py

for ip in ['1.1.1.1/32', '1.1.1.1/32', 'adrian/32']:
	wc.pairprint(ip, wc.IP_get(ip))

