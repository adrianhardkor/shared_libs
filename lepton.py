#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)


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
		SLOTID = 0
		for l in data['Linecards']:
			if type(l) is not dict:
				SLOTID += 1
				continue; # null for slot missing
			l = json.loads(wc.REST_GET(self.IP + str(l['Url']), user=self.user, pword=self.pword))
			for Port in l['Ports']:
				PortProp = json.loads(wc.REST_GET(self.IP + '/chassis/linecards/%s/ports/%s' % (SLOTID, Port['Url'].split('/')[-1]), user=self.user, pword=self.pword))
				if PortProp['Slot'] not in out['linecards'].keys():
					out['linecards'][PortProp['Slot']] = {'Description': l['Description'], 'Model': l['Model'], 'Name': l['Name'], 'Ports':{}}
				out['linecards'][PortProp['Slot']]['Ports'][PortProp['Id']] = PortProp
			SLOTID += 1
		return(out)
	def PrintStatus(self, finit):
		for card in finit['linecards'].keys():
			for port in finit['linecards'][card]['Ports'].keys():
				if 'NUL' not in str(finit['linecards'][card]['Ports'][port]['PhyLink']): 
					if type(finit['linecards'][card]['Ports'][port]['Protocol']) is list:
						finit['linecards'][card]['Ports'][port]['Protocol'] = ' '.join(wc.lunique(finit['linecards'][card]['Ports'][port]['Protocol']))
					if type(finit['linecards'][card]['Ports'][port]['PhyLink']) is list:
						finit['linecards'][card]['Ports'][port]['PhyLink'] = ' '.join(wc.lunique(finit['linecards'][card]['Ports'][port]['PhyLink']))
					wc.pairprint(str(card) + '.' + str(port) + '\t' + finit['linecards'][card]['Model'], str(finit['linecards'][card]['Ports'][port]['Protocol']) + '\t' + str(finit['linecards'][card]['Ports'][port]['PhyLink']))
# wc.jd(finit)

LEP = LEPTON(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
LEP.PrintStatus(LEP.GetStatus())

