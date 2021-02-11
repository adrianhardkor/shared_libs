#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

import velocity
V = velocity.VELOCITY('10.88.48.31', 'akrygows', wc.argv_dict['p'])
INV = V.GetInventory(); # device ipAddress
wc.jd(INV)
