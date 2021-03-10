#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

raw = wc.read_file('./export.json')
raw = json.loads(raw)
wc.jd(raw[sys.argv[1].lower()])
