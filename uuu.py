#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

one = {'1':1,'2':2,'list':[1,2,3,4]}
two = {'1':2,'2':1,'list':[4,3,2,1]}
def compareDict(old,new):
	out = deepdiff.DeepDiff(old,new)
	out = json.dumps(out)
	out = json.loads(out)
	return(out)
print(compareDict(one,two))
print(compareDict(one,one))
exit(0)

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


