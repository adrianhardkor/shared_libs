#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

data = {
  "text": "{\"_class\":\"hudson.model.Queue\",\"discoverableItems\":[],\"items\":[{\"_class\":\"hudson.model.Queue$WaitingItem\",\"actions\":[{\"_class\":\"hudson.model.ParametersAction\",\"parameters\":[{\"_class\":\"hudson.model.StringParameterValue\",\"name\":\"Playbook\",\"value\":\"ARC_GetFactsMultivendor\"},{\"_class\":\"hudson.model.StringParameterValue\",\"name\":\"sendmail\",\"value\":\"jenkinsAuto\"}]},{\"_class\":\"hudson.model.CauseAction\",\"causes\":[{\"_class\":\"hudson.model.Cause$UserIdCause\",\"shortDescription\":\"Started by user Jenkins Automation\",\"userId\":\"jenkins\",\"userName\":\"Jenkins Automation\"}]}],\"blocked\":False,\"buildable\":False,\"id\":1276,\"inQueueSince\":1612972819686,\"params\":\"\\u000aPlaybook=ARC_GetFactsMultivendor\\u000asendmail=jenkinsAuto\",\"stuck\":False,\"task\":{\"_class\":\"org.jenkinsci.plugins.workflow.job.WorkflowJob\",\"name\":\"ARC2\",\"url\":\"http://10.88.48.21:8080/job/ARC2/\",\"color\":\"red\"},\"url\":\"queue/item/1276/\",\"why\":\"In the quiet period. Expires in 4.9 sec\",\"timestamp\":1612972824686}]}"
}

wc.jd(json.loads(data)); exit(0)

def VelocityReportParse(html_data):
	out = []
	from bs4 import BeautifulSoup
	parsed = BeautifulSoup(html_data, features="html.parser")
	flag = 0
	for line in parsed.find_all('span'):
		if line.text.startswith('['): flag = 1
		if flag:
			out.append(line.text)
	return('\n'.join(out))
	
