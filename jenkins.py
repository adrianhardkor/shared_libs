#!/usr/bin/env python3
import time
import os
import sys
import wcommon as wc
import json
import re

class JENKINS():
	def __init__(self, IP, user, token):
		self.user = user
		self.pword = token
		self.IP = 'http://' + IP + ':8080'; # http
		self.__name__ = 'JENKINS'
	def REST_POST(self, url, args={}, verify=False):
		headers = {'Content-Type':'application/json', 'Accept':'application/json'}
		# print('\t' + url)
		wc.pairprint('url', self.IP + url)
		wc.pairprint('args', args)
		return(json.loads(wc.REST_POST(self.IP + url, user=self.user, pword=self.pword, verify=False, args=args, headers=headers, convert_args=True)))
	def REST_GET(self, url):
		# print('\t' + url)
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
	def PurgePipeline(self, name):
		# http://HOST/job/JOBNAME/doDelete
		wc.jd(self.REST_GET('/job/%s/%s/doDelete' % (name)))
		# curl -X POST http://jenkinUser:jenkinAPIToken@yourJenkinsURl.com/job/theJob/[11-1717]/doDelete
	def GetBuildResults(self, name):
		# print(self.REST_GET('/overallLoad/api/json'))
		out = {'results':[]}
		from bs4 import BeautifulSoup
		flag = False
		running = True
		build = self.REST_GET('/job/%s/lastBuild/api/json' % name)
		# wc.jd(build)
		if build['building']: flag = True
		while running:
			build = self.REST_GET('/job/%s/lastBuild/api/json' % name)
			if build['building']: 
				flag = True
				runId = build['id']
			if flag and build['building'] is False and build['result'] in ['SUCCESS', 'FAILURE']:
				# if jobStarted, jobComplete, and jobHasResult:
				running = False
			if flag:
				out[str(wc.timer_index_since(self.runTimer))] = {'status':'RUNNING','building':build['building'],'id':build['id'],'result':build['result']}
				return(str(build['id']),'')
				time.sleep(7)
			else:
				out[str(wc.timer_index_since(self.runTimer))] = {'status':'STARTED','building':build['building'],'id':build['id'],'result':build['result']}
				return(str(build['id']),'')
				time.sleep(2)
			text = []
		# GET CONSOLE (NON-API)
		text1 = self.REST_GET('/job/%s/lastBuild/consoleFull' % name)
		if 'text' in text1.keys(): text1 = text1['text']
		else: wc.jd(text1)
		for line in BeautifulSoup(text1, features="html.parser").find_all('span'):
			out['results'].append(line.text)
		out['results'] = '\n'.join(out['results'])
		return(runId,out)
	def RunPipeline(self,PipelineName='',parameters={}):
		Parameters = []
		parameters_url = []
		for p in parameters.keys():
			Parameters.append({'name':p,'value':parameters[p]})
			parameters_url.append(p + '=' + parameters[p])
		self.runTimer = wc.timer_index_start()
		# wc.pairprint('Parameters', Parameters)
		result = self.REST_POST('/job/%s/buildWithParameters%s' % (PipelineName, '?' + '&'.join(parameters_url)), Parameters)
		if result['response.status_code'] != "201":
			# FAIL KICKOFF
			wc.jd(result); exit(5)
		else:
			# SUCCESS KICKOFF
			# wc.pairprint(result['Response'], result['response.request.body'])
			pass
		runId,output = self.GetBuildResults(PipelineName)
		return(runId)
		# wc.jd(output)
	
# J = JENKINS(wc.argv_dict['IP'], wc.argv_dict['user'], wc.env_dict['JEN_TOKEN'])
# param = {'Playbook':'ARC_GetFactsMultivendor','sendmail':'adrian.krygowski'}
# param['dryrun'] = 'dryrun'
# J.RunPipeline(wc.argv_dict['Pipe'], param)
# curl -X POST http://jenkinUser:jenkinAPIToken@yourJenkinsURl.com/job/theJob/[11-1717]/doDelete

