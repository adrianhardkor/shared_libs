#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap

out = {}
out2 = {}
raw = json.loads(wc.read_file('/home/adrian/Modems/RDU.10.88.48.100.json'))
for r in raw.keys():
	out[r] = soap.FormatRDU_Modem(r, raw[r])
	for k in out[r].keys():
		if out[r][k] == '': continue; # with values only
		if k not in out2.keys(): out2[k] = 1
		else: out2[k] = out2[k] + 1
wc.jd(out)
wc.jd(out2)


