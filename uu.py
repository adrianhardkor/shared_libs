#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

import velocity
# V = velocity.VELOCITY('10.88.48.31', 'akrygows', wc.argv_dict['p'])
# INV = V.GetInventory(); # device ipAddress
# wc.jd(INV)

# /velocity/api/inventory/v13/template/{templateId}/sessions/{sessionId}?merge= <NO/INVENTORY/FULL>
# /ito/executions/v1/agents

import awx
ansible = awx.AWX(os.environ['AWX_IP'], os.environ['AWX_USER'], os.environ['AWX_PASS'])
# data = json.loads(wc.REST_GET('http://' + ansible.IP + '/api/v2/job_templates/' + 'SetFacts' + '/launch/', user=ansible.user, pword=ansible.pword))
# wc.jd(data)
result,GetFactRunIds = ansible.RunPlaybook('SetFacts',args={'hostName':'ARCBKBNEDGDRR01','index':'_adrianI','value':'try2'})
wc.jd(GetFactRunIds)

