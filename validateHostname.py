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


def validateHostname(hostname):
	hostname = hostname.replace(' ','').replace('-','')
	# print(hostname)
	labs = ['ARC']
	markets = ['UAT1', 'UAT2', 'VDC1', 'MDEV', 'SIT1', 'CLOD', 'BKBN', 'PODS']
	# services = '%s%s%s'
	functions = ['BBR', 'EPR', 'VAR', 'DAR', 'DRR', 'CMR', 'MSR', 'AGS', 'SWI', 'POD', 'BAR', 'OTN', 'CMT', 'VCE', 'FRW', 'TRM', 'L1S', 'TST', 'STS', 'W1S']
	# iterations = '%d%d'

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
	if INVALID == []:
		# wc.pairprint('Valid',hostname)
		# print(json.dumps(components, indent=2))
		pass
	else:
		wc.pairprint('Invalid',hostname)
	return(components)

if 'host' in wc.argv_dict.keys():
	wc.jd(validateHostname(wc.argv_dict['host']))
	exit(0)


validateHostname('ARC-EDG-BKBNFRWJ01')
validateHostname('ARC-EDG-BKBNFRWJ02')
validateHostname('ARC-EDG-BKBNEPRJ01')
validateHostname('ARC-EDG-BKBNEPRJ02')
validateHostname('ARC-EDGE-BKBNDRRJ01')
validateHostname('ARC-EDGE-BKBNDRRJ02')
validateHostname('ARC-BACKBONE-PTXJ01')
validateHostname('ARC-UAT-Z1-HUHCORJ01')
validateHostname('ARCUATMRT1HUHMSR02')
validateHostname('ARC-UAT-Z2-HUHCORJ01')
validateHostname('ARC-UAT-Z2-HUHCORJ02')
validateHostname('ARC-BACKBONE-PTXJ02')
validateHostname('ARC-BACKBONE-PTXJ03')
validateHostname('ARC-BACKBONE-PTXJ04')
validateHostname('ARC-UAT-VIDEO-VARJ01')
validateHostname('ARC-UAT-VIDEO-VARJ02')
validateHostname('ARC-UAT-DC-CLOUD-CORJ01')
validateHostname('7750-sr7')
validateHostname('ARCUAT1HUHTRMV01')
validateHostname('ARCUAT2BKBTRMV01')
validateHostname('ARCUAT2BKBTRMV02')
validateHostname('ARCUAT1VDCTRMV01')
validateHostname('ARCUAT1CLDTRMV01')
validateHostname('ARCUAT2BKBTRMV03')
validateHostname('ARC-MRV_7')
validateHostname('ARC-MRV_8')
validateHostname('ARC-MRV_9')
validateHostname('ARCUAT1CMTTRMV01')
validateHostname('ARC-UAT-BB-TRANSPORT-1')
validateHostname('ARC-UAT-BB-TRANSPORT-2')
validateHostname('ARC-UAT-MKT1-HUHOTNE01')
validateHostname('ARC-UAT-MKT1HUAOTNE01')
validateHostname('ARC-UAT-M2-HUH-TRANSPORT')
validateHostname('ARC-UAT-M2-HUB-1-TRANSPORT')
validateHostname('ARC-UAT-Z1-HUHAGSJ02')
validateHostname('ARC-PULSE-APP')
validateHostname('OHCOLMARC-DNS01')
validateHostname('OHCOLMARC-TIMJUMP')
validateHostname('OHCOLMARC-ADAMJUMP')
validateHostname('OHCOLMARC-CMS01')
validateHostname('TEST_IP')
validateHostname('LAB-RDU-01')
validateHostname('LAB-PNR-01')
validateHostname('LAB-PNR-02')
validateHostname('LAB-DPE-01')
validateHostname('LAB-DPE-02')
validateHostname('LAB-REG')
validateHostname('LAB-PWS')
validateHostname('ARCUAT1HUHCMTA01')
validateHostname('WOPR-SB')
validateHostname('STC VM')
validateHostname('SPIRENT-TESTCENTER-CHASSIS')
validateHostname('ARCAUTH')
validateHostname('ARCGITLAB')
validateHostname('LEPTON MANAGMENT ')
validateHostname('ARCUAT1CLDSWIJ01')
validateHostname('ARCUAT1CLDSWIJ02')
validateHostname('ARCUAT1VDCSWIJ01')
validateHostname('ARCUAT1CMTSWIA01')
validateHostname('ARCUAT1HUHSWIJ01')
validateHostname('ARCUAT1HUHSWIJ02')
validateHostname('ARCUAT2BKBSWIJ01')
validateHostname('ARCUAT2BKBSWIJ02')
validateHostname('ARCUAT2BKBSWIJ03')
validateHostname('ARCUAT1CLDAGSJ01')
validateHostname('ARC_EX2300_11')
validateHostname('ARC_EX2300_12')
validateHostname('ARC_EX2300_13')
validateHostname('ARC_EX2300_14')
validateHostname('ARC_EX2300_15')
validateHostname('Velocity-agent')
validateHostname('Velocity-prod')
validateHostname('Velocity-ds')
validateHostname('ARCPODVELOSLS01')
