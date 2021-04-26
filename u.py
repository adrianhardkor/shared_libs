#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json

import velocity
velocity.GetDiagBundle(IP=wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
wc.pairprint('diag bundle download took', wc.fullRuntime())
