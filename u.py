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
result,GetFactRunIds = ansible.RunPlaybook('SetFacts',args={'hostName':'ARCBKBNEDGDRR01','index':'_adrianI','value':'_adrianV'})
wc.jd(GetFactRunIds)

