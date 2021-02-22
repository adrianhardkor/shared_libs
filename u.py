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



J = JENKINS(wc.argv_dict['IP'], wc.argv_dict['user'], wc.env_dict['JEN_TOKEN'])
param = {'Playbook':'ARC_GetFactsMultivendor','sendmail':'adrian.krygowski'}
param['dryrun'] = 'dryrun'
J.RunPipeline('ARC2', param)

