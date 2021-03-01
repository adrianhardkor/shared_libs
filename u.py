#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

# import velocity
# V = velocity.VELOCITY('10.88.48.31', 'akrygows', wc.argv_dict['p'])
# INV = V.GetInventory(); # device ipAddress
# wc.jd(INV)

# /velocity/api/inventory/v13/template/{templateId}/sessions/{sessionId}?merge= <NO/INVENTORY/FULL>
# /ito/executions/v1/agents

r = 'Current configuration:\n!\nver 08.0.95bT213\n!\nstack unit 1\n  module 1 icx7150-48zp-poe-port-management-module\n  module 2 icx7150-8-sfp-plus-port-80g-module\n  stack-port 1/2/1\n  stack-port 1/2/3\n!\n!\nglobal-stp\n!\n!\n!\nvlan 1 name DEFAULT-VLAN by port\n!\n!\nvlan 1023 by port\n tagged ethe 1/2/1 \n!\nvlan 1024 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/1 \n!\n!\nvlan 1025 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/2 \n!\nvlan 1026 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/3 \n!\nvlan 1027 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/4 \n!\nvlan 1028 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/5 \n!\nvlan 1029 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/6 \n!\nvlan 1030 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/7 \n!\nvlan 1031 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/8 \n!\nvlan 1032 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/9 \n!\nvlan 1033 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/10 \n!\nvlan 1034 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/11 \n!\nvlan 1035 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/12 \n!\nvlan 1036 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/13 \n!\nvlan 1037 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/14 \n!\nvlan 1038 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/15 \n!\nvlan 1039 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/16 \n!\nvlan 1040 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/17 \n!\nvlan 1041 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/18 \n!\nvlan 1042 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/19 \n!\nvlan 1043 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/20 \n!\nvlan 1044 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/21 \n!\nvlan 1045 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/22 \n!\nvlan 1046 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/23 \n!\nvlan 1047 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/24 \n!\nvlan 1048 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/25 \n!\nvlan 1049 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/26 \n!\nvlan 1050 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/27 \n!\nvlan 1051 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/28 \n!\nvlan 1052 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/29 \n!\nvlan 1053 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/30 \n!\nvlan 1054 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/31 \n!\nvlan 1055 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/32 \n!\nvlan 1056 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/33 \n!\nvlan 1057 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/34 \n!\nvlan 1058 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/35 \n!\nvlan 1059 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/36 \n!\nvlan 1060 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/37 \n!\nvlan 1061 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/38 \n!\nvlan 1062 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/39 \n!\nvlan 1063 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/40 \n!\nvlan 1064 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/41 \n!\nvlan 1065 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/42 \n!\nvlan 1066 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/43 \n!\nvlan 1067 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/44 \n!\nvlan 1068 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/45 \n!\nvlan 1069 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/46 \n!\nvlan 1070 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/47 \n!\nvlan 1071 by port\n tagged ethe 1/2/1 \n untagged ethe 1/1/48 \n!\nvlan 1072 by port\n tagged ethe 1/2/1 \n!\n!\nvlan 2001 by port\n tagged ethe 1/2/1 to 1/2/8 \n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\noptical-monitor 8\noptical-monitor non-ruckus-optic-enable\naaa authentication web-server default local\naaa authentication login default local\njumbo\nenable aaa console\nhostname ICX7150-48ZP-Router dynamic\nip dns domain-list wowway.com dynamic\nip dns server-address 192.168.0.1(dynamic)\nip route 0.0.0.0/0 192.168.0.1 distance 254 dynamic\nip route 0.0.0.0/0 10.88.240.1 distance 254 dynamic\n!\nno telnet server\nusername super password .....\nusername admin password .....\n!\n!\n!\n!\n!\n!\nmanager registrar\n!\nmanager port-list 987\n!\n!\n!\n!\n!\n!\n!\n!\n!\ninterface management 1\n ip address 10.88.241.36 255.255.248.0\n!\ninterface ethernet 1/1/4\n ip address 192.168.0.166 255.255.255.0 dynamic\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\nend'

for rr in r.split('\n'):
	print(rr)
exit(0)

J = JENKINS(wc.argv_dict['IP'], wc.argv_dict['user'], wc.env_dict['JEN_TOKEN'])
param = {'Playbook':'ARC_GetFactsMultivendor','sendmail':'adrian.krygowski'}
param['dryrun'] = 'dryrun'
J.RunPipeline('ARC2', param)



stack unit 1
  module 1 icx7150-48zp-poe-port-management-module
  module 2 icx7150-8-sfp-plus-port-80g-module
  stack-port 1/2/1
  stack-port 1/2/3
!
vlan 1 name DEFAULT-VLAN by port
!
!
vlan 1023 by port
 tagged ethe 1/2/1 
!
vlan 1024 by port
 tagged ethe 1/2/1 
 untagged ethe 1/1/1 
!
!
interface management 1
 ip address 10.88.241.36 255.255.248.0
!
interface ethernet 1/1/4
 ip address 192.168.0.166 255.255.255.0 dynamic
!

vlan 2001 by port
 tagged ethe 1/2/1 to 1/2/8 



