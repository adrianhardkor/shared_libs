#!/usr/bin/env python3
import os
import sys
sys.path.insert(1, './lib/shared_libs/')
import wcommon as wc
import mhandle

# ./lib/shared_libs/loggerJenkins.py flask=IP:PORT  BUILD_TAG=${env.BUILD_TAG}  data=${data}

MH = mHANDLE(flaskIP=wc.argv_dict['flask'].split(':')[0], flaskPort=wc.argv_dict['flask'].split(':')[1])
MH.UpdateRun(wc.argv_dict['BUILD_TAG'], wc.argv_dict['data'])

