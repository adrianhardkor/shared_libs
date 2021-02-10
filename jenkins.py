#!/usr/bin/env python3
import time
import os
import sys
import wcommon as wc
import json
import re

__author__ = 'wehappyfew'

import requests

def create_new_jenkins_job(j_url, j_port, new_job_name, j_user, j_pass):
	"""
	Create a new jenkins job
	:param j_url: eg http://mysite.com
	:param j_port: eg 8686 [8080 is jenkin's default]
	:param new_job_name: eg "NEW_JOB"
	:param j_user: Sauron
	:param j_pass: i_c_u
	:return:
	"""
	url     = '{0}:{1}/createItem?name={2}'.format(j_url, j_port, new_job_name)
	auth    = (j_user, j_pass)
	payload = '<project><builders/><publishers/><buildWrappers/></project>'
	headers = {"Content-Type" : "application/xml"}
	return(json.loads(wc.REST_POST(url, user=j_user, pword=j_pass,  headers={"Content-Type" : "application/xml"}, args=payload, verify=False)))

# wc.jd(create_new_jenkins_job('http://%s' % wc.argv_dict['IP'], '8080', 'ARC2', wc.argv_dict['user'], wc.argv_dict['pass']))





# curl -X POST http://localhost:8080/job/job1/build  \
#  -jenkins:f1499cc9852c899d327a1f644e61a64d \
#  --data-urlencode json='{"parameter": [{"name":"id", "value":"100"}, {"name":"loglevel", "value":"high"}]}'


class JENKINS():
	def __init__(self, IP, user, token):
		self.user = user
		self.pword = token
		self.IP = 'http://' + IP + ':8080'; # http
		self.__name__ = 'JENKINS'
	def REST_POST(self, url, args={}, verify=False):
		headers = {'Content-Type':'application/json', 'Accept':'application/json'}
		return(json.loads(wc.REST_POST(self.IP + url, user=self.user, pword=self.pword, verify=False, args=args, headers=headers, convert_args=True)))
	def REST_GET(self, url):
		return(json.loads(wc.REST_GET(self.IP + url, user=self.user, pword=self.pword,verify=False)))
	def ConsoleFormat(self, html_data):
		out = []
		# print(html_data)
		# print('\n\n\n')
		from bs4 import BeautifulSoup
		parsed = BeautifulSoup(html_data, features="html.parser")
		for line in parsed.find_all('span'):
			# find_all('span')
			out.append(line.text)
		out.append(str(line))
		return('\n'.join(out))
	def GetBuildResults(self, name):
		from bs4 import BeautifulSoup
		text = ['']
		while 'Finished: ' not in text[-1]:
			print(text[-1])
			time.sleep(3)
			text = []
			text1 = self.REST_GET('/job/%s/lastBuild/console' % name)
			if 'text' in text1.keys(): text1 = text1['text']
			else: wc.jd(text1)
			for line in BeautifulSoup(text1, features="html.parser").find_all('span'):
				text.append(line.text)
			text.append(str(line))
		return('\n'.join(text))
	def RunPipeline(self,PipelineName='',parameters={}):
		Parameters = []
		parameters_url = []
		for p in parameters.keys():
			Parameters.append({'name':p,'value':parameters[p]})
			parameters_url.append(p + '=' + parameters[p])
		wc.jd(self.REST_POST('/job/%s/buildWithParameters%s' % (PipelineName, '?' + '&'.join(parameters_url)), Parameters))
		print(self.GetBuildResults(PipelineName))
	
J = JENKINS(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['token'])
J.RunPipeline('ARC2', {'Playbook':'ARC_GetFactsMultivendor','sendmail':'jenkinsAuto'})

