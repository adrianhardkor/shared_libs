#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

data = wc.read_file('./test')
wc.jd(json.loads(data))

