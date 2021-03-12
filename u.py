#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

pairedlist = ['{REQUEST', '{v-i-vendor-opts', '00:00:11:8b:9b:01:01:02:05:96:01:01:01:02:01:03:03:01:01:04:01:01:05:01:01:06:01:01:07:01:19:08:01:08:09:01:00:0a:01:01:0b:01:18:0c:01:01:0d:02:00:40:0e:02:00:10:0f:01:01:10:04:00:00:00:06:11:01:01:13:01:01:14:01:00:15:01:38:16:01:01:17:01:01:18:01:04:19:01:04:1a:01:04:1b:01:28:1c:01:02:1d:01:08:1e:01:20:1f:01:10:20:01:18:21:01:02:22:01:01:23:01:01:24:01:18:25:01:01:26:02:00:40:27:01:01:28:01:d4:2c:04:00:00:00:01:2e:01:01:12:07:10:0c:f8:93:b5:96:b3:12:07:01:0c:f8:93:b5:96:b4', ' chaddr', '0c:f8:93:b5:96:b2', ' relay-agent-info', '01:04:20:00:00:02:02:06:0c:f8:93:b5:96:b2:09:0b:00:00:11:8b:06:01:04:01:02:03:01', ' relay-agent-circuit-id', '01:04:20:00:00:02', ' client-id-created-from-mac-address', '00:00:00:00', ' dhcp-class-identifier', 'docsis3.0:', ' hlen', '06', ' giaddr', '0a:58:10:01', ' vendor-encapsulated-options', '02:03:45:43:4d:03:10:45:43:4d:3a:45:4d:54:41:3a:45:52:4f:55:54:45:52:04:0f:44:39:53:42:55:33:45:43:36:35:31:30:36:37:39:05:01:35:06:0a:39:2e:31:2e:31:30:33:53:35:51:07:08:31:2e:32:2e:31:2e:36:32:08:06:30:30:30:30:43:41:09:06:54:47:38:36:32:47:0a:19:41:72:72:69:73:20:49:6e:74:65:72:61:63:74:69:76:65:2c:20:4c:2e:4c:2e:43:2e:0f:07:45:52:4f:55:54:45:52', ' dhcp-parameter-request-list', '{01', '02', '03', '04', '06', '07', '36', '7d', 'b1', '7a}', ' relay-agent-remote-id', '02:06:0c:f8:93:b5:96:b2', ' client-id', 'ff:93:b5:96:b2:00:03:00:01:0c:f8:93:b5:96:b2', ' htype', '01', ' dhcp-message-type', '01}}']



pairedlist.pop(0)
pairedlist[0] = pairedlist[0].strip('{')
pairedlist[-1] = pairedlist[-1].strip('}')

def wonky_bac_pairedlist(myl):
	result = {}
	for i in range(0, len(myl), 2):
		index = str(myl[i]).strip()
		value = str(myl[i + 1])
		result[index] = value
		if index == 'dhcp-parameter-request-list':
			ii = int(i) + 1
			for myll in myl[ii::]:
				if myll.startswith(' '):
					break
				ii = ii + 1
			result[index] = ' '.join(myl[i:ii])
			wc.pairprint(index, ' '.join(myl[i:ii]))
			remainder = wonky_bac_pairedlist(myl[ii:])
			for r in remainder:
				result[r] = remainder[r]
			return(result)
	return(result)

res = wonky_bac_pairedlist(pairedlist)
wc.jd(res)
exit(0)






raw = wc.read_file('./export.json')
raw = json.loads(raw)
wc.jd(raw[sys.argv[1].lower()])
