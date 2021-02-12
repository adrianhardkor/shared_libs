#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)
import time

class VELOCITY():
	def __init__(self, IP, user='', pword='', token=''):
		self.__name__ = 'VELOCITY'
		self.V = 'https://' + str(IP)
		if user != '' and pword != '':
			self.user = user
			self.pword = pword
			self.TOKEN = json.loads(wc.REST_GET(self.V + '/velocity/api/auth/v2/token', user=self.user, pword=self.pword))['token']
		elif token != '':
			self.TOKEN = token
		else:
			print('Failed: VELOCITY No U/P or TOKEN provided!')
			exit(5)
		self.headers = {"X-Auth-Token": self.TOKEN}
	def REST_GET(self, url, params={}, limit='?limit=200'):
		# print('\t' + self.V + url)
		# page = '1'
		# while page is ''
		# url = url + '?offset={offset}&limit={limit}&filter={filter}' == MAX 200 then OFFSET
		if '?' not in url:
			url = url + limit
		self.headers['Content-Type'] = self.headers['Accept'] = 'application/json'
		# print(headers)
		data = json.loads(wc.REST_GET(self.V + url, headers=self.headers, params=params))
		return(data)
	def REST_PUT(self, url, args={}, verify=False):
		url = url + '?limit=200'
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'	
		return(json.loads(wc.REST_PUT(self.V + url, verify=verify, args=args, headers=headers, convert_args=True)))
	def REST_POST(self, url, args={}, verify=False):
		if '?' not in url:
			url = url + '?limit=200'
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'	
		return(json.loads(wc.REST_POST(self.V + url, verify=verify, args=args, headers=headers, convert_args=True)))
	def REST_DELETE(self, url, args={}, verify=False):
		# wc.pairprint('[INFO] ', 'REST_DELETE: ' + url)
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'	
		return(json.loads(wc.REST_DELETE(self.V + url, verify=verify, args=args, headers=headers, convert_args=True)))
	def GetAgentReservation(self, resvId):
		# if has resvId then already reserved
		# if has topId then script requires reservation PUT/POST?
		INV = VELOCITY.GetTopologies(self)
		for r in VELOCITY.REST_GET(self, '/velocity/api/reservation/v16/reservations', params={'filter': 'status::ACTIVE'})['items']:
			if r['id'] == resvId:
				return(INV[r['topologyName']])
	def VelocityReportParse(self, html_data):
		if type(html_data) == dict:
			# failed?
			if 'response.body' in html_data.keys():
				return({'response.body':html_data['response.body']})
		out = []
		from bs4 import BeautifulSoup
		parsed = BeautifulSoup(html_data, features="html.parser")
		flag = 0
		for line in parsed.find_all('span'):
			if line.text.startswith('['): flag = 1
			if flag:
				out.append(line.text)
		return('\n'.join(out))
	def RunScript(self, INV, testPath, parameters=[], topology='', reservation='', HTML_FNAME=''):
		timer = wc.timer_index_start()
		args = {'testPath':testPath, 'detailLevel':'ALL_ISSUES_ALL_STEPS', 'parametersList':parameters}
		data = self.REST_POST('/ito/executions/v1/executions', args=args)
		if 'executionState' not in data.keys():
			data['html_report'] = wc.bytes_str(data['response.body'])
			data['script'] = self.GetScripts()[testPath]
			return(data)
		while data['executionState'] != 'COMPLETED':
			time.sleep(4)
			data = self.REST_GET('/ito/executions/v1/executions/' + data['executionID'])
			print('  '.join([data['executionState'], data['testPath'],str(data['parametersList']),data['executionID'],str(wc.timer_index_since(timer))]))
		html_report = json.loads(wc.REST_GET(self.V + '/ito/reporting/v1/reports/%s/print' % data['reportID'], headers=self.headers))['text']
		data['html_report'] = self.VelocityReportParse(html_report) 
		# wc.jd(data)
		if HTML_FNAME != '':
			if not HTML_FNAME.lower().endswith('.html'):
				HTML_FNAME = HTML_FNAME + '.html'
			wc.log_fname(html_report, HTML_FNAME)
		return(data)
		# wc.jd(self.REST_GET('/ito/reporting/v1/reports/' + data['reportID']))
		# wc.jd(self.REST_GET('/ito/reporting/v1/reports/' + data['executionID']))
		# wc.jd(self.REST_GET('/ito/reporting/v1/reports?filter=parentReport::%s' % data['executionID']))
		# HTML Report
		# data = json.loads(wc.REST_GET(self.V + '/ito/reporting/v1/reports/%s/print' % data['reportID'], headers=self.headers))['text']
		# wc.log_fname(data,testPath.split('/')[-1] + '.html')
	def GetScripts(self):
		scripts = self.REST_GET( '/ito/repository/v1/scripts')['content']
		out = {}
		for script in scripts:
			if not script['driver']:
				# wc.pairprint(script['fullPath'], script['guid'])
				# wc.pairprint(script['fullPath'], script['executionMessages'])
				out[script['fullPath']] = script
		return(out)
	def GetUsers(self):
		# /velocity/api/user/v9/profiles
		out = {}
		for p in VELOCITY.REST_GET(self, '/velocity/api/user/v9/profiles')['profiles']:
			out[p['id']] = p
			out[p['id']]['display'] = "%s (%s)" % (p['name'], p['login'])
		return(out)
	def GetTopologies(self):
		out = {}
		top = VELOCITY.REST_GET(self, '/velocity/api/topology/v12/topologies')['topologies']
		res = VELOCITY.REST_GET(self, '/velocity/api/reservation/v16/reservations', params={'filter': 'status::ACTIVE'})['items']
		users = VELOCITY.GetUsers(self)
		activeRes = {}
		for r in res:
			# topology-oriented, for both active and non
			r['start'] = time.ctime(r['start'])
			r['end'] = time.ctime(r['end'])
			activeRes[r['topologyId']] = r
		for t in top:
			t['resources'] = {}
			t['activeRes'] = {}
			out[t['name']] = t
			if t['id'] in activeRes.keys():
				out[t['name']]['activeRes'] = activeRes[t['id']]
				for resource in VELOCITY.REST_GET(self, '/velocity/api/topology/v12/topology/%s/resources' % t['id'])['items']:
					if resource['parentName'] == None:
						out[t['name']]['resources'][resource['name']] = resource
					else:
						out[t['name']]['resources'][resource['parentName'] + '||' + resource['name']] = resource

				out[t['name']]['activeRes']['creatorId'] = users[out[t['name']]['activeRes']['creatorId']]['display']
				out[t['name']]['activeRes']['ownerId'] = users[out[t['name']]['activeRes']['ownerId']]['display']
			out[t['name']]['creatorId'] = users[out[t['name']]['creatorId']]['display']
			out[t['name']]['lastModifierId'] = users[out[t['name']]['lastModifierId']]['display']
		return(out)
	def ApplyReservationTopology(top, out, pg, ports, p, device):
		ports[p['name']]['lockUtilizationType'] = p['lockUtilizationType']
		ports[p['name']]['connectedPortParentName'] = p['connectedPortParentName']
		ports[p['name']]['connectedPortParentId'] = p['connectedPortParentId']
		ports[p['name']]['connectedPortName'] = p['connectedPortName']
		ports[p['name']]['connectedPortId'] = p['connectedPortId']
		for t in top.keys():
			# t = topology_name
			for resource in top[t]['resources'].keys():
				# resource = 'name'
				activeRes = {
					'name': top[t]['activeRes']['name'],
					'id': top[t]['activeRes']['id'],
					'start': top[t]['activeRes']['start'],
					'end': top[t]['activeRes']['end'],
					'topologyId': top[t]['activeRes']['topologyId'],
					'topologyName': top[t]['activeRes']['topologyName'],
					'ownerId': top[t]['activeRes']['ownerId'],
					'description': top[t]['activeRes']['description'],
					'creatorId': top[t]['creatorId'],
					'descriptionTopology': top[t]['description']
				}
				if device['name'] == resource:
					# Reserved Device
					out[device['name']]['activeRes'] = activeRes
				elif '||'.join([device['name'], p['name']]) == resource:
					# Reserved Port on Device
					ports[p['name']]['activeRes'] = activeRes
				# wc.jd(p)
				if p['connectedPortParentName'] in out.keys():
					# bi-directional mapping for devices
					out[p['connectedPortParentName']]['activeRes'] = activeRes
					if p['connectedPortName'] in out[p['connectedPortParentName']]['ports'].keys():
						# reserved device and port exists
						out[p['connectedPortParentName']]['ports'][p['connectedPortName']]['activeRes'] = activeRes
		return(out,ports)
	def BuildDevicePropertyArgs(self, device_name, index, new_value, append=False):
		if type(self.INV[device_name][index]) == dict:
			# property
			if not append:
				new = new_value
				args = {'properties': [{'definitionId':self.INV[device_name][index]['definitionId'], 'value': new_value}]}
				if self.INV[device_name][index]['value'] == new_value: args = {}
			else:
				if self.INV[device_name][index]['value'] == None:
					self.INV[device_name][index]['value'] = ''
				new = self.INV[device_name][index]['value'].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				# wc.pairprint(self.INV[device_name][index]['value'].split(' '), new)
				args = {'properties': [{'definitionId':self.INV[device_name][index]['definitionId'], 'value': new}]}
				if new in self.INV[device_name][index]['value'].split(' '):
					args = {}; # already exists
			self.INV[device_name][index]['value'] = new; # same definitionId
		elif type(self.INV[device_name][index]) == str:
			if not append:
				new = new_value
				args = {index: new}
				if self.INV[device_name][index] == new_value: args = {}
			else:
				if self.INV[device_name][index] == None:
					self.INV[device_name][index] = ''
				new = self.INV[device_name][index].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {index:new}
				if new in self.INV[device_name][index].split(' '):
					args = {}; # already exists
				# wc.pairprint(self.INV[device_name][index].split(' '), new)
			self.INV[device_name][index] = new
		return(args)
	def UpdateDevice(self, device_name, index, new_value, append=False, templateName=''):
		new_value = str(new_value)
		# API PageId = 48
		if device_name not in self.INV.keys():
			# CreateDevice (POST)
			args = {}
			args['name'] = device_name
			args['templateId'] = self.GetTemplates(templateName=templateName)['id']
			device_new = self.REST_POST('/velocity/api/inventory/v13/device', args=args)
			self.INV = self.FormatInventory(self.INV, device_new)
			print('  '.join(['[INFO] Created:', device_name, device_new['id']]))
		args = self.BuildDevicePropertyArgs(device_name, index, new_value, append=append); # updates self.INV
		if args == {}: return()
		data = VELOCITY.REST_PUT(self, '/velocity/api/inventory/v13/device/%s' % self.INV[device_name]['id'], args=args)
		wc.pairprint('  '.join(['[INFO] Updated:', device_name,index,str(new_value)]), index + ':  ' + new_value)
		if index == 'ipAddress':
			# updated DEVICE IP ADDRESS - RE DISCOVER
			time.sleep(5); # wait 5s after applying ipAddress
			# DISCOVERY HAPPENS IN BATCHES OF 4 // ANY 1of4 CAN DELAY(Ping Timeout) THE BATCH ONLINE STATUS
			# DISCOVERY COULD TAKE UP TO TIMEOUT * 4-DEVICES
			self.Discover(self.INV[device_name]['id'])
		return()
	def Discover(self, deviceId):
		discover = self.REST_POST('/velocity/api/inventory/v13/device/%s/action?type=discover' % deviceId)
		# print('  '.join(['[INFO] *ACTION*:', device_name,new_value,'discover',discover['Response']]))
		data = ['init']
		while data != []:
			# executionID
			# parametersList
			# testPath
			time.sleep(2)
			data = self.REST_GET('/ito/executions/v1/executions?limit=200&filter=executionState::IN_PROGRESS')['content']
			for not_begun in self.REST_GET('/ito/executions/v1/executions?limit=200&filter=executionState::NOT_BEGUN')['content']:
				data.append(not_begun)
			for d in data:
				d['parametersList']= wc.lsearchAllInline('property_', d['parametersList'])
				print('    '.join([data['testPath'],data['parametersList']]))
		return()
	def ChangeDevicePortProp(self, device_name, port_name, index, new_value, append=False):
		args = {}
		# WILL NOT CREATE PORT IF DOESNT EXIST = SEE V.UpdatePort
		# REMINDER TO RE-UP GetInventory once updated via REST_PUT
		if index not in self.INV[device_name]['ports'][port_name].keys():
			wc.jd(self.INV[device_name]['ports'][port_name]) 
		# wc.pairprint(index, type(self.INV[device_name]['ports'][port_name][index]))
		if type(self.INV[device_name]['ports'][port_name][index]) == dict:
			# property = 'value'
			if not append:
				# dict = property with uuid
				new = new_value
				args = {'properties': [{'definitionId':self.INV[device_name]['ports'][port_name][index]['definitionId'], 'value': new_value}]}
				if self.INV[device_name]['ports'][port_name][index]['value'] == new_value:
					return(self.INV)
			else:
				if self.INV[device_name]['ports'][port_name][index]['value'] == None:
					self.INV[device_name]['ports'][port_name][index]['value'] = ''
				new = self.INV[device_name]['ports'][port_name][index]['value'].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {'properties': [{'definitionId':self.INV[device_name]['ports'][port_name][index]['definitionId'], 'value': new}]}
				if new in self.INV[device_name]['ports'][port_name][index]['value'].split(' '):
					return(self.INV); # already exists
		else:
			# Not property = [index]
			if index in ['pgName', 'pgId']:
				# CHANGE PORGROUP: /device/{deviceId}/port_group/{portGroupId}
				# wc.pairprint('/velocity/api/inventory/v13/device/%s/port/%s' % (self.INV[device_name]['id'], self.INV[device_name]['ports'][port_name]['id']), args)
				raise('portgroup changes not coded yet'); # pgName and pgId:  port_group
			if self.INV[device_name]['ports'][port_name][index] == new_value:
				return(self.INV)
			if not append:
				new = new_value
				args = {index: new_value}
			else:
				new = self.INV[device_name]['ports'][port_name][index].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {index:new}
				if new in self.INV[device_name]['ports'][port_name][index].split(' '):
					return(self.INV); # already exists			
		data = VELOCITY.REST_PUT(self, '/velocity/api/inventory/v13/device/%s/port/%s' % (self.INV[device_name]['id'], self.INV[device_name]['ports'][port_name]['id']), args=args)
		# NOTIFY PORT PROP CHANGE
		if index in data.keys():
			wc.pairprint('  '.join(['[INFO] Updated1:', port_name,index,str(new_value)]), data[index])
			self.INV[device_name]['ports'][port_name][index] = new
		elif 'properties' in data.keys():
			for p in data['properties']:
				if p['name'] == index:
					self.INV[device_name]['ports'][port_name][index]['value'] = new
					# Add confirmation here to verify value, otherwise didnt take
					wc.pairprint('  '.join(['[INFO] Updated2:', port_name,index]),p['value'])
					break
		else:
			# error
			wc.pairprint('  '.join(['[INFO] Updated3:', port_name,index,str(new_value)]), data)
	def UpdatePort(self, device_name, pgName, port_name, index, value, templateName="Network Port", append=False):
		# WILL CREATE IF NOT FOUND
		# REMINDER TO RE-UP GetInventory once updated via REST_PUT
		# slotname = portgroup, portname = portname

		# if device is Network then Port is Network
		if device_name not in self.INV.keys():
			raise('UpdatePort: ' + device_name + ' not in Inventory, cant update port yet: ' + port_name)

		# if pg doesnt exist, create and create port underneath pg
		PGs = self.GetDevicePGs(self.INV[device_name]['id'])
		if pgName not in PGs.keys():
			# pg doesnt exist on device yet
			pg = self.REST_POST('/velocity/api/inventory/v13/device/%s/port_group' % self.INV[device_name]['id'], args={'name':pgName})
			# wc.jd(pg)
		else:
			pg = PGs[pgName]
		if port_name not in self.INV[device_name]['ports'].keys():
			# for auto-loading template-ports
			self.INV = self.GetInventory()
			print(self.INV[device_name]['ports'].keys())
		if port_name not in self.INV[device_name]['ports'].keys():
			# POST / create
			if self.INV[device_name]['templateName'] == 'Server': templateName = 'Server Port'
			else: templateName = 'Network Port'
			args = {}
			args['name'] = port_name
			args['templateId'] = self.GetTemplates(templateName=templateName)['id']
			if pg['id'] != None: args['groupId'] = pg['id']
			new_port = self.REST_POST('/velocity/api/inventory/v13/device/%s/port' % self.INV[device_name]['id'], args=args)
			out,ports = self.FormatPorts(self.INV, self.INV[device_name], pg, new_port, {})
			wc.pairprint('[INFO] ' + port_name, 'created:' + str(ports[port_name]))
			# Re-Apply inventory for ChangeDevicePortProp to use
			self.INV[device_name]['ports'][port_name] = ports[port_name]
			wc.pairprint('ports_' + port_name, ports[port_name]['id'])
		else:
			# if port exists, assume pg exists
			pass
		# PUT: for each attribute, update port
		self.ChangeDevicePortProp(device_name, port_name, index, value, append=append)
	def GetDevicePGs(self, deviceId):
		out = {}
		raw = self.REST_GET('/velocity/api/inventory/v13/device/%s/port_groups' % deviceId)['portGroups']
		for blah in raw:
			wc.jd(blah)
			out[blah['name']] = blah
			out[blah['id']] = blah
		wc.jd(out)
		return(out)
	def GetDeviceName(self, uuid):
		# converted to name for reservation-resource sync (per name)
		return(self.REST_GET('/velocity/api/inventory/v13/device/' + uuid)['name'])
	def GetTemplates(self, templateName='', templateId=''):
		# /velocity/api/inventory/v13/templates
		data = self.REST_GET('/velocity/api/inventory/v13/templates')['templates']
		out = {}
		for d in data:
			out[d['name']] = out[d['id']] = d
			if d['id'] == templateId:
				return(d)
		if templateName != '':
				return(out[templateName])
		return(out)
	def FormatPorts(self, out, device, pg, p, ports):
		# wc.pairprint(device['name'], p['name'] + '\t' + p['templateId'])
		# template = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/template/%s/ports' % p['templateId'])
		# wc.jd(template)
		if p['groupId'] == None:
			pg = {'name': 'No Group', 'id':None}
		else:
			print('    '.join([device['name'], p['name'], 
			pg = pg[p['groupId']]
		ports[p['name']] = {'Description': p['description'], 'pgName': pg['name'], 'pgId': p['groupId'], 'id':p['id'],'linkChecked':time.ctime(p['linkChecked'])}
		ports[p['name']]['isLocked'] = p['isLocked']
		ports[p['name']]['isReportedByDriver'] = p['isReportedByDriver']
		ports[p['name']]['linkChecked'] = p['linkChecked']
		ports[p['name']]['lastModified'] = p['lastModified']
		for PortProp in p['properties']:
			ports[p['name']][PortProp['name']] = {'value': PortProp['value'], 'definitionId': PortProp['definitionId']}
		if p['isLocked']:
			out,ports = VELOCITY.ApplyReservationTopology(self.top, out, pg, ports, p, device)
		# wc.pairprint(p['name'], pg['ports'][p['name']])
		# out[device['name']]['ports'] = ports
		return(out,ports)
	def FormatInventory(self, out, device):
		ports = {}
		if device['id'] not in out.keys():
			# wc.jd(device)
			out[device['name']] = {'ports': {}, 'name':device['name'], 'isOnline':device['isOnline'], 'templateName':self.GetTemplates(templateId=device['templateId'])['name'], 'Tags':device['tags']}
		out[device['name']]['id'] = device['id']
		for prop in device['properties']:
			out[device['name']][prop['name']] = {'value': prop['value'], 'definitionId': prop['definitionId']}

		all_ports = self.REST_GET('/velocity/api/inventory/v13/device/%s/ports' % device['id'], params={'includeProperties':True})['ports']
		out[device['name']]['ports'] = {}
		PGs = self.GetDevicePGs(device['id'])
		for p in all_ports:
			out,ports = self.FormatPorts(out, device, PGs, p, ports)
			out[device['name']]['ports'][p['name']] = ports[p['name']]
		return(out)
	def GetInventory(self):
		out = {}
		self.top = VELOCITY.GetTopologies(self)
		data = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		# wc.jd(data)
		for device in data['devices']:
			out = self.FormatInventory(out, device)
		self.INV = out
		return(out)

# V = VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
# INV = V.GetInventory(); # device ipAddress
# wc.jd(INV)
# wc.jd(wc.FindAnsibleHost('10.88.48.237', INV))

# data = V.RunScript(INV, 'main/assets/' + wc.argv_dict['s'])
# print(data['html_report'])

# V.GetScripts()
# V.GetAgentReservation('cecf3f52-fc19-4d3c-9e58-7bf8c5975290')
# INV = V.GetInventory(); # device ipAddress
# wc.jd(INV)
# wc.jd(V.GetTopologies())
# https://10.88.48.31/velocity/inventory/resources/14a1dc9b-3347-4396-bb38-eb4ede1a30c4/ports/6ae2b408-7b9f-42d3-800d-a3cb23d7d70e/properties

# page 51-52 on 8.3.0 api ref -- create port (DRIVER)
# 59 to edit: body {'properties': [{'definitionId':prop_uuid,'value':value}]}
