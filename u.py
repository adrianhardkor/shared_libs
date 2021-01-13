#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
wc.jd(wc.wcheader)


class LEPTON():
	def __init__(self, IP, user, pword):
		self.user = user
		self.pword = pword
		self.IP = IP + ':8081'; # http
		self.__name__ = 'AWX'
	def GetStatus(self):
		data = json.loads(wc.REST_GET('http://' + self.IP + '/chassis', user=self.user, pword=self.pword))
		wc.jd(data)
		return({})

LEP = LEPTON('10.88.240.61','lepton','Lepton!')
wc.jd(LEP.GetStatus())
