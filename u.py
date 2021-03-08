#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

raw = wc.read_file('/Users/adrian/Desktop/provServer.modems.xml.txt').replace('cptype:','cptype_')
raw = wc.xml_loads2(raw)
wc.jd(raw)
