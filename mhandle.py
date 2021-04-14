akrygows@LAPTOP-FE8856IV:~/wow/Sandbox/shared_libs$ cat mhandle.py
#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import jinja2

class mHANDLE():
        def __init__(self, flaskIP, flaskPort):
                self.flaskIP = flaskIP
                self.flaskPort = flaskPort
		self.url = 'http://%s:%s' % (self.flaskIP, self.flaskPort)
                self.__name__ = 'mHANDLE'
        def GetRun(self, myID):
		data = json.loads(wc.REST_GET(self.url + '/vAgent?reportId=' + str(myID)))
		return(data)
        def delDevice(self, cmac):
                data = runner(self.PATH, 'delDevice', 'http://%s:9100/cp-ws-prov/provService' % self.PWS, args={'sessionId':self.sessionId, 'cmac':cmac})
                # wc.jd(data)
                return(data)

MH = mHANDLE(flaskIP='10.88.48.21', flaskPort='5000')
wc.jd(MH.GetRun('test'))

