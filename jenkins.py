#!/usr/bin/env python3
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
	return(wc.REST_POST(url, user=j_user, pword=j_pass,  headers={"Content-Type" : "application/xml"}, args=payload, verify=False))

print(create_new_jenkins_job('http://%s' % wc.argv_dict['IP'], '8080', 'ARC2', wc.argv_dict['user'], wc.argv_dict['pass']))
