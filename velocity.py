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
		# if list(args.keys()) == ['tags']:
		# 	wc.jd(args)
		result = json.loads(wc.REST_PUT(self.V + url, verify=verify, args=args, headers=headers, convert_args=True))
		if 'response.status_code' in result.keys():
			if result['response.status_code'] not in ['200',200]:
				wc.jd(args)
				wc.jd(result)
				raise
		return(result)
	def REST_POST(self, url, args={}, verify=False):
		if '?' not in url:
			url = url + '?limit=200'
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'
		result = json.loads(wc.REST_POST(self.V + url, verify=verify, args=args, headers=headers, convert_args=True))
		if 'response.status_code' in result.keys():
			if result['response.status_code'] not in ['200',200]:
				wc.pairprint('args', args)
				wc.pairprint('result', result)
				exit(5)
		return(result)
	def REST_DELETE(self, url, args={}, verify=False):
		# wc.pairprint('[INFO] ', 'REST_DELETE: ' + url)
		headers = {"X-Auth-Token": self.TOKEN}
		headers['Content-Type'] = headers['Accept'] = 'application/json'	
		return(json.loads(wc.REST_DELETE(self.V + url, verify=verify, args=args, headers=headers, convert_args=True)))
	def DelAllMessages(self):
		for isRead in ['false', 'true']:
			gone = self.REST_DELETE('/velocity/api/message/v6/messages?filter=isRead::' + isRead)
			# wc.jd(gone)
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
				if self.INV[device_name][index]['value'] == new_value: return({}); # already matches
				else:
					old = self.INV[device_name][index]['value']
					new = new_value
			else:
				if self.INV[device_name][index]['value'] == None:
					self.INV[device_name][index]['value'] = ''
				new = self.INV[device_name][index]['value'].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				# wc.pairprint(self.INV[device_name][index]['value'].split(' '), new)
				args = {'properties': [{'definitionId':self.INV[device_name][index]['definitionId'], 'value': new}]}
				if new in self.INV[device_name][index]['value'].split(' '):
					return({}); # already exists
				else:
					old = self.INV[device_name][index]['value'].split(' ')
			self.INV[device_name][index]['value'] = new; # same definitionId
		elif type(self.INV[device_name][index]) == str:
			if not append:
				new = new_value
				args = {index: new}
				if self.INV[device_name][index] == new_value: return({}); # already matches
				else:
					old = self.INV[device_name][index]
					new = new_value
			else:
				if self.INV[device_name][index] == None:
					self.INV[device_name][index] = ''
				new = self.INV[device_name][index].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {index:new}
				if new in self.INV[device_name][index].split(' '):
					return({}); # already exists
				else:
					old = self.INV[device_name][index].split(' ')
			self.INV[device_name][index] = new
		elif type(self.INV[device_name][index]) == list:
			if not append:
				new = sorted(wc.lunique(list(new_value)))
				args = {index: new}
				if sorted(self.INV[device_name][index]) == new: return({}); # already matches
				else:
					old = sorted(self.INV[device_name][index])
			else:
				if self.INV[device_name][index] == None: self.INV[device_name][index] = []
				new = wc.lunique(self.INV[device_name][index])
				for nv in new_value:
					new.append(nv)
				new = sorted(wc.lunique(list(new)))
				args = {index:new}
				if new == sorted(list(self.INV[device_name][index])):
					return({}); # already same
				else:
					old = sorted(list(self.INV[device_name][index]))
			self.INV[device_name][index] = new
		# UPDATE NEEDED
		wc.pairprint('UPDATE NEEDED (append:%s)\t' + str(type(old)) + ': ' + str(old), str(type(new)) + ': ' + str(new))
		return(args)
	def UpdateDevice(self, device_name, index, new_value, append=False, templateName=''):
		# API PageId = 48
		# wc.pairprint('[INFO] ', device_name)
		if device_name not in self.INV.keys():
			# CreateDevice (POST)
			args = {}
			args['name'] = device_name
			args['templateId'] = self.GetTemplates(templateName=templateName)['id']
			device_new = self.REST_POST('/velocity/api/inventory/v13/device', args=args)
			# re-up GetInventory
			# self.GetInventory()
			print('  '.join(['[INFO] Created:', device_name, str(device_new['id'])]))
			self.INV = self.FormatInventory(self.INV, device_new)
		args = self.BuildDevicePropertyArgs(device_name, index, new_value, append=append); # updates self.INV
		if args == {}: return()
		data = VELOCITY.REST_PUT(self, '/velocity/api/inventory/v13/device/%s' % self.INV[device_name]['id'], args=args)
		if 'definitionId' in str(args):
			for p in data['properties']:
				if p['name'] == index:
					wc.pairprint('  '.join(['[INFO] Updated D2:', device_name,index,str( self.INV[device_name][index]['value'])]), index + ':  ' + p['value'])
		else:
			wc.pairprint('  '.join(['[INFO] Updated D1:', device_name,index,str(self.INV[device_name][index])]), index + ':  ' + str(data[index]))
		if index == 'ipAddress':
			# updated DEVICE IP ADDRESS - RE DISCOVER
			time.sleep(5); # wait 5s after applying ipAddress
			# DISCOVERY HAPPENS IN BATCHES OF 4 // ANY 1of4 CAN DELAY(Ping Timeout) THE BATCH ONLINE STATUS
			# DISCOVERY COULD TAKE UP TO TIMEOUT * 4-DEVICES
			self.Discover(self.INV[device_name]['id'],driver='ping')
		elif index == 'name' and device_name in self.INV.keys():
			# change name // already existed
			self.INV[new_value] = self.INV.pop(device_name)
		return()
	def Discover(self, deviceId, driver=''):
		discover = self.REST_POST('/velocity/api/inventory/v13/device/%s/action?type=discover' % deviceId)
		# print('  '.join(['[INFO] *ACTION*:', device_name,new_value,'discover',discover['Response']]))
		data = ['init']
		while data != []:
			# executionID
			# parametersList
			# testPath
			raw = self.REST_GET('/ito/executions/v1/executions?limit=200&filter=executionState::IN_PROGRESS')['content']
			for not_begun in self.REST_GET('/ito/executions/v1/executions?limit=200&filter=executionState::NOT_BEGUN')['content']:
				raw.append(not_begun)
			data = []
			for d in raw:
				d['parametersList']= wc.lsearchAllInline('property_', d['parametersList'])
				if driver != '' and driver in d['testPath']:
					data.append('    '.join([d['testPath'], str(d['parametersList']), d['executionState']]))
			print(data)
			time.sleep(1)
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
				# print('  '.join(['',str(self.INV[device_name]['ports'][port_name][index]['value']),str(type(self.INV[device_name]['ports'][port_name][index]['value'])),'',str(new_value),str(type(new_value))]))
			else:
				if self.INV[device_name]['ports'][port_name][index]['value'] == None:
					self.INV[device_name]['ports'][port_name][index]['value'] = ''
				new = self.INV[device_name]['ports'][port_name][index]['value'].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {'properties': [{'definitionId':self.INV[device_name]['ports'][port_name][index]['definitionId'], 'value': new}]}
				if new_value in self.INV[device_name]['ports'][port_name][index]['value'].split(' '):
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
				if self.INV[device_name]['ports'][port_name][index] == new_value:
					return(self.INV)
			else:
				new = self.INV[device_name]['ports'][port_name][index].strip(' ').split(' ')
				new.append(new_value)
				new = ' '.join(sorted(wc.lunique(new))).strip(' ')
				args = {index:new}
				if new_value in self.INV[device_name]['ports'][port_name][index].split(' '):
					return(self.INV); # already exists			
		data = VELOCITY.REST_PUT(self, '/velocity/api/inventory/v13/device/%s/port/%s' % (self.INV[device_name]['id'], self.INV[device_name]['ports'][port_name]['id']), args=args)
		# NOTIFY PORT PROP CHANGE
		if index in data.keys():
			wc.pairprint('  '.join(['[INFO] Updated1:', port_name,index,str(new_value)]), data[index])
			self.INV[device_name]['ports'][port_name][index] = new
		elif 'definitionId' in str(args):
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
			PGs = self.GetDevicePGs(self.INV[device_name]['id'])
			# wc.jd(pg)
		else:
			pg = PGs[pgName]
		# wc.pairprint(port_name, self.INV[device_name])
		if port_name not in self.INV[device_name]['ports'].keys():
			# for auto-loading template-ports
			self.INV = self.GetInventory()
			# print(self.INV[device_name]['ports'].keys())
		if port_name not in self.INV[device_name]['ports'].keys():
			# POST / create
			if self.INV[device_name]['templateName'] == 'Server': templateName = 'Server Port'
			elif self.INV[device_name]['templateName'] == 'Modem': templateName = 'Modem Port'
			elif self.INV[device_name]['templateName'] == 'CMTS' and wc.is_int(port_name[0]): templateName = 'RF Port'
			else: templateName = 'Network Port'
			wc.pairprint(self.INV[device_name]['templateName'], templateName)
			args = {}
			args['name'] = port_name
			args['templateId'] = self.GetTemplates(templateName=templateName)['id']
			if pg['id'] != None: args['groupId'] = pg['id']
			new_port = self.REST_POST('/velocity/api/inventory/v13/device/%s/port' % self.INV[device_name]['id'], args=args)
			out,ports = self.FormatPorts(self.INV, self.INV[device_name], PGs, new_port, {})
			wc.pairprint('[INFO] ' + port_name, ports[port_name].keys())
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
			if blah['id'] == None: blah['id'] = 'null'
			out[blah['name']] = blah
			out[blah['id']] = blah
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
		wc.pairprint(templateName, templateId)
		wc.jd(data)
		return(out)
	def FormatPorts(self, out, device, pg, p, ports):
		# wc.pairprint(device['name'], p['name'] + '\t' + p['templateId'])
		# template = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/template/%s/ports' % p['templateId'])
		# wc.jd(template)
		if p['groupId'] == None:
			pg = {'name': 'No Group', 'id':None}
		else:
			# print('    '.join([device['name'], p['name']]))
			if p['groupId'] not in pg.keys():
				wc.jd(pg)
				wc.jd(p)
				wc.pairprint(device['name'], p['name'])
			pg = pg[p['groupId']]
		ports[p['name']] = {'description': p['description'], 'pgName': pg['name'], 'pgId': p['groupId'], 'id':p['id'],'linkChecked':time.ctime(p['linkChecked'])}
		ports[p['name']]['isLocked'] = p['isLocked']
		ports[p['name']]['isReportedByDriver'] = p['isReportedByDriver']
		ports[p['name']]['linkChecked'] = p['linkChecked']
		ports[p['name']]['lastModified'] = p['lastModified']
		ports[p['name']]['connections'] = {}
		for PortProp in p['properties']:
			ports[p['name']][PortProp['name']] = {'value': PortProp['value'], 'definitionId': PortProp['definitionId']}
		if p['isLocked']:
			out,ports = VELOCITY.ApplyReservationTopology(self.top, out, pg, ports, p, device)
		# wc.pairprint(p['name'], pg['ports'][p['name']])
		# out[device['name']]['ports'] = ports
		return(out,ports)
	def FormatInventory(self, out, device):
		ports = {}
		if 'id' not in device.keys(): wc.jd(device)
		if device['id'] not in out.keys():
			out[device['name']] = {'tags': device['tags'], 'description': device['description'], 'ports': {}, 'name':device['name'], 'isOnline':device['isOnline'], 'templateName':self.GetTemplates(templateId=device['templateId'])['name'], 'tags':device['tags']}
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
	def CreateConnection(self, device1, port1, device2, port2):
		connection_name = '_'.join([str(device1),str(port1),'',str(device2),str(port2)])
		# SEE IF DEVICE AND PORT EXISTS
		for d in [str(device1), str(device2)]:
			if d not in self.INV.keys():
				wc.pairprint('Connection Failed:  ' + connection_name, str(d) + '  not in V.INV')
				return()
		for d2,p2 in {device1:port1,device2:port2}.items():
			if p2 not in self.INV[d2]['ports'].keys(): 
				wc.pairprint('Connection Failed:  ' + connection_name, str(p2) + '  not in ' + str(d2) + ' V.INV ports')
				return()
		# SEE IF CONNECTION ALREADY EXISTS
		if connection_name in self.INV[device1]['ports'][port1]['connections'].keys() and \
		connection_name in self.INV[device2]['ports'][port2]['connections'].keys():
			wc.pairprint('Connection Already Exists', connection_name); return()
		# GET IDs
		port1Id = self.INV[device1]['ports'][port1]['id']
		port2Id = self.INV[device2]['ports'][port2]['id']
		connect_args = {'port1Id':port1Id,'port2Id':port2Id,'type':'FIXED'}
		# RUN REST_PUT
		data = self.REST_PUT('/velocity/api/inventory/v14/physical_connections', args=[connect_args])
		# PASS/FAIL HANDLER
		result = 'FAIL'
		if data['response.status_code'] in ['200',200]:
			wc.pairprint('Connection Made:    ' + connection_name, 'SUCCESS')
			result = 'SUCCESS'
		if result == 'FAIL':
			wc.pairprint('Connection Failed:  ' + connection_name, data)
			return()
		# IF SUCCESS: ADD TO V.INV  
		self.INV[device1]['ports'][port1]['connections'][connection_name] = connection_name.split('__')[0]
		self.INV[device2]['ports'][port2]['connections'][connection_name] = connection_name.split('__')[1]
	def GetConnections(self, out):
		# PHYSICAL CONNECTIONS, USED FOR TOPOLOGY ABSTRACTION
		physical = self.REST_GET('/velocity/api/inventory/v14/physical_connections')['connections']
		for p in physical:
			connection_name = '_'.join([p['device1']['name'],p['port1']['name'],'',p['device2']['name'],p['port2']['name']])
			# print(connection_name)
			value = {}
			value['id'] = p['id']
			value[p['device1']['name'] + '_' + p['port1']['name']] = 1
			value[p['device2']['name'] + '_' + p['port2']['name']] = 2
			out[p['device1']['name']]['ports'][p['port1']['name']]['connections'][connection_name] = value
			out[p['device2']['name']]['ports'][p['port2']['name']]['connections'][connection_name] = value
		return(out)
	def GetInventory(self):
		self.DelAllMessages()
		out = {}
		self.top = VELOCITY.GetTopologies(self)
		data = VELOCITY.REST_GET(self, '/velocity/api/inventory/v13/devices', params={'includeProperties':True, 'includePortGroups': True})
		# wc.jd(data)
		for device in data['devices']:
			out = self.FormatInventory(out, device)

		out = self.GetConnections(out)
		self.INV = out
		return(out)

# V = VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
# V.DelAllMessages()

# V.INV = V.GetInventory(); # device ipAddress
#wc.jd(V.INV['ARCBKBNEDGDRR01'])
# args = {'tags': ['ARC', 'BKBN', 'DRR', 'EDG']}
# wc.jd(V.REST_PUT('/velocity/api/inventory/v13/device/c2bc86a5-71fc-4fdf-bd74-8973ce3c71f9?limit=200', args=args))
# V.Discover(INV['ARCBKBNEDGEPR02']['id'], driver='ping')
# wc.jd(V.INV)
# wc.jd(wc.FindAnsibleHost('10.88.48.237', INV))

# data = V.RunScript(INV, 'main/assets/' + wc.argv_dict['s'])
# print(data['html_report'])

# V.GetScripts()
# V.GetAgentReservation('cecf3f52-fc19-4d3c-9e58-7bf8c5975290')
# INV = V.GetInventory(); # device ipAddress
# wc.jd(V.INV)
# wc.jd(V.GetTopologies())
# https://10.88.48.31/velocity/inventory/resources/14a1dc9b-3347-4396-bb38-eb4ede1a30c4/ports/6ae2b408-7b9f-42d3-800d-a3cb23d7d70e/properties

# page 51-52 on 8.3.0 api ref -- create port (DRIVER)
# 59 to edit: body {'properties': [{'definitionId':prop_uuid,'value':value}]}
