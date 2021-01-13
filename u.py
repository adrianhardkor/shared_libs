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
		self.IP = 'http://' + IP + ':8081'; # http
		self.__name__ = 'AWX'
	def GetStatus(self):
		out = {'chassis': {}, 'linecards':{}}
		data = json.loads(wc.REST_GET(self.IP + '/chassis', user=self.user, pword=self.pword))
		out['chassis']['Serial'] = data['Serial']
		out['chassis']['Model'] = data['Model']
		for l in data['Linecards']:
			if type(l) is not dict:
				continue; # null for slot missing
			l = json.loads(wc.REST_GET(self.IP + str(l['Url']), user=self.user, pword=self.pword))
			# wc.jd(l)
			out['linecards'][l['Id']] = {'Description': l['Description'], 'Model': l['Model'], 'Name': l['Name']}
		return(out)

LEP = LEPTON('10.88.240.61',wc.argv_dict['user'], wc.argv_dict['pass'])
wc.jd(LEP.GetStatus())
