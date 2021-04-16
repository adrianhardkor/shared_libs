#!/usr/bin/env python3
import os
import sys
sys.path.insert(1, './lib/shared_libs/')
import wcommon as wc
import mhandle

# ./lib/shared_libs/loggerJenkins.py BUILD_TAG=${env.BUILD_TAG}  data=${data}

MH = mHANDLE(flaskIP=wc.env_dict['FLASK_IP'], flaskPort=wc.env_dict['FLASK_PORT'])
MH.who = 'JENKINS'
MH.runId = wc.argv_dict['BUILD_TAG']
MH._LOGGER(wc.argv_dict['data']); # creates timestamps too
exit(0)
