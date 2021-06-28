#!/usr/bin/env python3
import sys,os,json
import wcommon as wc

def Format_iTest_ssv(issue, out, _id):
	oo = []
	headers = {}
	hOO = 0
	for l in issue:
		# row
		o = []
		for ll in l.split('  '):
			# colum
			ll = ll.strip()
			if ll != '': o.append(ll) 
			oo.append(o)
		hOO += 1
		if o == [] or len(o) == 1: continue; # single tag dismissed
		elif o[0] == 'Name/ID' or 'Name' in o[0]:
			# o[0] = ID
			# HEADERS
			h = 0
			for ooo in o:
				headers[h] = ooo
				h += 1
			# wc.jd(headers)
			# print(headers)
		else:
			# VALUES
			v = 0
			# wc.pairprint(len(o), o)
			out['steps'][_id]['body'][o[0]] = {}
			for vvv in o:
				# wc.pairprint(o, vvv)
				out['steps'][_id]['body'][o[0]][headers[v]] = o[v]
				v += 1
			# wc.jd(out['steps'][_id]['body'][o[0]])
	return(out)

def Format_iTest_xml(fname):
    data = wc.xml_loads2(wc.read_file(fname))
    # wc.jd(data); exit()
    out = {'steps': {}, 'items':{}}
    if 'iTestTestReport' in data.keys():
        # NOT RAW
        out['reportSummary'] = data['iTestTestReport']['reportSummary']
        report = 'iTestTestReport'
    else:
        # RAW
        report = 'report'
    for issue in data[report]['issues']['item']:
        if 'executedStepId' in issue.keys():  _id = issue['@executedStepId']
        else: _id = issue['@issueIndex']
        out['items'][_id] = issue['message']
    
    for step in data[report]['steps']['ExecutedStep']:
        if 'executedStepId' in step.keys(): _id = step['executedStepId']
        else: _id = step['orderIndex']
        # print(_id)
        if _id not in out['steps'].keys(): out['steps'][_id] = {}
        for field in ['executionDuration', 'executionState', 'executableStep']:
            out['steps'][_id][field] = step[field]
        if 'response' in step.keys(): body = step['response']['body']
        else:
            if 'body' not in step['result']['response'].keys():
               if 'command' not in step['result']['action'].keys(): continue 
               body = {'issue': step['result']['action']['command']['body']}
            else: body = step['result']['response']['body']
        if body != None:
            if 'body' not in out['steps'][_id].keys(): out['steps'][_id]['body'] = {}
            if type(body['issue']) == str:
                 for line2 in body['issue'].split('\n'):
                    if '-------' in str(body['issue']):
                        out = Format_iTest_ssv(body['issue'].split('\n'), out, _id); # ssv = space-spaced value RESULTS
                    elif ':' in line2:
                        line2 = line2.split(':')
                        index = line2.pop(0).strip()
                        out['steps'][_id]['body'][index] = ':'.join(line2).strip()
                        # wc.pairprint(str(_id) + '\t' + index, line2)
                        # wc.jd(out['steps'][_id]['body']); exit()
                    else: out['steps'][_id]['body'][line2] = None               
            elif type(body['issue']) == list:
                for line in body['issue']:
                    if type(line) == dict:
                        for k in line.keys():
                            out[k] = line[k]
                    elif type(line) == str: 
                        for line2 in line.split('\n'):
                            if ':' in line2:
                                line2 = line2.split(':')
                                index = line2.pop(0).strip()
                                out['steps'][_id]['body'][index] = ':'.join(line2).strip()
                                # wc.pairprint(index, line2)
                                # wc.jd(out['steps'][_id]['body'])
                            else: out['steps'][_id]['body'][line2] = None
                    elif line == None: pass
                    else: wc.jd(line); exit()
            else: wc.jd(body['issue']); exit()
            if 'item' in body.keys():
                out['steps'][_id]['item'] = body['item']
        else: out['steps'][_id]['body'] = ''
    return(out)

path = '/home/akrygows/win/OneDrive/Desktop/samplereportfiles/'    
# wc.jd(wc.xml_loads2(wc.read_file(path + 'stc_2021-06-22_13-17-29_raw.xml'))); exit()
out = Format_iTest_xml(path + 'stc_2021-06-22_13-17-29.xml')
wc.jd(out)
exit()


tryme = {'commands':['show ver'], 'ip':'10.88.240.32', 'username':'ADMIN','password':'ArcLabAdmin','settings_prompt':"([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])",'buffering':'set cli screen-length 0','ping':False}
tryme['quiet'] = True
tryme['exit'] =  ['request system logout user ADMIN']
tryme['exit'] = ['exit']
for ex in tryme['exit']:
    tryme['commands'].append(ex)

i = 1
while i < 16:
  wc.PARA_CMD_LIST(**tryme)
  i += 1
