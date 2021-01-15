#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)

# hostname = 'ARC UAT1 HUH CMR 01'
# print(hostname)


def sanitizeARChostname(hostname):
	hostname = hostname.replace(' ','').replace('-','')
	print(hostname)
	labs = ['ARC']
	markets = ['UAT1', 'UAT2', 'VDC1', 'MDEV', 'SIT1', 'CLOD', 'BKBN', 'PODS']
	# services = '%s%s%s'
	functions = ['BBR', 'EPR', 'VAR', 'DAR', 'DRR', 'CMR', 'MSR', 'AGS', 'SWI', 'BAR', 'OTN', 'CMT', 'VCE', 'FRW', 'TRM', 'L1S', 'TST', 'STS', 'W1S']
	iterations = '%d%d'

	INVALID = []
	components = {}

	components['lab'] = hostname[:3].upper()
	if components['lab'] not in labs: INVALID.append(components['lab'])

	components['market'] = hostname[3:7].upper()
	if components['market'] not in markets: INVALID.append(components['market'])

	components['service'] = hostname[7:10].upper()
	if re.search('...', components['service']) is False: INVALID.append(components['service'])

	components['function'] = hostname[10:13].upper()
	if components['function'] not in functions: INVALID.append(components['function'])

	components['iteration'] = hostname[13:].upper()
	if re.search('..', components['iteration']) is False: INVALID.append(components['iteration'])

	components['INVALID'] = INVALID
	print(json.dumps(components, indent=2))

sanitizeARChostname('arcpodsvelsts01')
sanitizeARChostname('ARCCOLM-ARC-MSRJ0')
exit(0)
