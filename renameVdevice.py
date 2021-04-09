#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff

import velocity

V = velocity.VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
V.GetInventory()
V.UpdateDevice(wc.argv_dict['old'], 'name', wc.argv_dict['new'])
