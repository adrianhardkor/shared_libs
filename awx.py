#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)
import json,requests,ipaddress,time

class AWX():
	def __init__(self, IP, user, pword):
		self.user = user
		self.pword = pword
		self.IP = IP
		self.__name__ = 'AWX'
	def REST_GET(self,api):
		return(json.loads(wc.REST_GET('http://' + self.IP + api, user=self.user, pword=self.pword)))
	def mcsplit(mystr, cc):
		# handler for multiple splits
		if type(cc) == str:
			chars1 = []
			chars1[:0] = cc
		elif type(cc) == list:
			chars1 = cc
		for c in chars1:
			mystr = mystr.replace(c, ',')
		return(mystr.split(','))
	def IP_get(n):
		# GET ATTRIBUES FOR CIDR BLOCK
		# >>> from netaddr import IPAddress
		# >>> IPAddress('255.255.255.0').netmask_bits()
		# 24
		n = n.strip()
		cidr_split = AWX.mcsplit(n, ['/',' '])
		cidr = ipaddress.IPv4Network(('0.0.0.0',cidr_split[1])).prefixlen
		try:
			addr4 = ipaddress.ip_interface(n)
		except ValueError:
			return(['', '',cidr])
		netAddress = str(addr4.network)
		try:
			net = ipaddress.ip_network(netAddress)
			hosts = []
			for ip in net:
				hosts.append(str(ip))
			if bool([cidr_split[0]] == hosts):
				return([str(addr4.network), '',cidr])
			elif cidr_split[1] != '31' and cidr_split[1] != '255.255.255.254':
				hosts.pop()
				hosts.pop(0)
			return([str(addr4.network), hosts,cidr])
		except Exception as err:
			return([str(addr4.network), err,cidr])
	def listprint(deli,lst):
		out = []
		for l in lst:
			out.append(str(l))
		print(deli.join(out))
	def list2dict(lst):
		if lst == [] or lst == [''] or lst == ['---'] or lst == ['{}']:
			return({})
		return({lst[i]: lst[i + 1] for i in range(0, len(lst), 2)})
	def awx_job_events_format(self, je):
		# GET STDOUTLINES FROM COMPLETED JOB AND FORMAT
		new = {'stdout':[]}
		for result in je['results']:
			i = result['url']
			if 'task_path' in result['event_data']:
				if result['event_display'].startswith('Task Started'):
					print()
					wc.pairprint(i + '    ' + result['event_display'], result['event_data']['task_path'])
				elif result['event_display'] == 'Host Started':
					result['event_display'] = ' '.join([result['event_display'], result['host_name']])
				# wc.pairprint(i + '    ' + result['event_display'], result['event_data']['task_path'])
				new[i] = {'event_display': result['event_display'], 'task_path':result['event_data']['task_path']}
				if 'res' in result['event_data'].keys():
					for dump in ['stdout_lines','stderr_lines']:
						if dump in result['event_data']['res'].keys():
							# wc.pairprint(i + '    ' + dump,'\n'.join(result['event_data']['res'][dump]))
							new[i][dump] = result['event_data']['res'][dump]
			elif 'res' in result['event_data']:
				new[i] = result['event_data']['res']
			else:
				new['stdout'].append(str(i) + '\t' + str(result['stdout']))
				new[i] = {'failed': result['failed']}
			# wc.jd(json.loads(wc.REST_GET('http://' + self.IP + result['related']['children'], user=self.user, pword=self.pword)))
		return(new)
	def RunPlaybook(self,playbook_name,args={}):
		# ASYNC BY DEFAULT
		playbook_start = wc.timer_index_start()
		if args != {}:
			# wc.pairprint('REST:extra_vars', list(args.keys()))
			extra_vars = {'extra_vars':args}
			args = json.dumps(extra_vars)
		data = json.loads(wc.REST_POST('http://' + self.IP + '/api/v2/job_templates/' + playbook_name + '/launch/', user=self.user, pword=self.pword, args=args))
		self.data = data
		status_url = data['url']
		data['status'] = 'Running'
		if 'job' not in data.keys():
			# SOMETHING WENT WRONG
			print(data)
			data['response.request.body'] = json.loads(data['response.request.body'])
			wc.jd(data)
			return('')
		job = str(data['job'])
		playbook = data['playbook']
		inventory = json.loads(wc.REST_GET('http://' + self.IP + '/api/v2/inventories/' + str(data['inventory']), user=self.user, pword=self.pword))['name']
		while data['status'] not in ['successful','failed']:
			time.sleep(4)
			data = json.loads(wc.REST_GET('http://' + self.IP + status_url, user=self.user, pword=self.pword))
			if data['status'] != 'running':
				print('  '.join([job,playbook,inventory,data['status'],'',str(wc.timer_index_since(playbook_start))]))
		raw = json.loads(wc.REST_GET('http://' + self.IP + data['related']['job_events'], user=self.user, pword=self.pword))
		# wc.jd(raw)
		wc.pairprint('API','http://' + self.IP + data['related']['job_events'])
		raw = AWX.awx_job_events_format(self, raw)
		return(data['status'],raw)
		# ['related']['stdout']
		# POST https://your.tower.server/api/v2/job_templates/<your job template id>/launch/ with any required data gathered during the previous step(s). The variables that can be passed in the request data for this action include the following.
		# extra_vars: A string that represents a JSON or YAML formatted dictionary (with escaped parentheses) which includes variables given by the user, including answers to survey questions
		# job_tags: A string that represents a comma-separated list of tags in the playbook to run
		# limit: A string that represents a comma-separated list of hosts or groups to operate on
		# inventory: A integer value for the foreign key of an inventory to use in this job run
		# credential: A integer value for the foreign key of a credential to use in this job run
	def GetScaffolding(self, facts):
		def hostname_path_compare(validation, gmsList):
			invalid = []
			# ARCUAT1K8WRK01 = '{'lab': 'ARC', 'market': 'UAT1', 'service': 'K8W', 'function': 'RK0', 'iteration': '1', 'INVALID': ['RK0']}'
			for gms in ['lab','market','service']:
				if gmsList[gms] == '': continue
				if validation[gms] != gmsList[gms]:
					invalid.append({'path':gmsList[gms],'hostnameSnippet':validation[gms]}) 
			return(invalid)
		
		out = {}
		printOut = {}
		path = './inventories/'
		for inventory_file in wc.exec2('ls ' + path).split('\n'):
			if not inventory_file.lower().endswith('yml') and not inventory_file.lower().endswith('yaml'):
				continue
			inventory_file = path + inventory_file
			print('\n' + inventory_file)
			data = wc.read_yaml(inventory_file)
			# wc.jd(data)
			# print(wc.log_yaml(data, 'new.yml'))
			for a in data.keys():
				for group in data[a]['children'].keys():
					for market in data[a]['children'][group]['children'].keys():
						# if market not in wc.markets
						if 'hosts' in data[a]['children'][group]['children'][market].keys():
							# 'hosts' means no service/function groupings/scaffolding = OS/SERVICE
							for hostname in data[a]['children'][group]['children'][market]['hosts'].keys():
								valid_host = wc.validateHostname(hostname)
								valid_path = hostname_path_compare(valid_host, {'lab':group,'market':market,'service':''})
								if hostname not in out.keys():
									out[hostname] = {'readyValidateHostname':True,'ip':[]}
									out[hostname]['groups'] = [valid_host['lab'],valid_host['market'],valid_host['service'],valid_host['function']]
									printOut[hostname] = {'readyValidateHostname': True}
								if valid_host['INVALID'] != []:
									# dns name doesnt fit supported groups in Confluence page
									out[hostname]['readyValidateHostname'] = False
									out[hostname]['namingStandard'] = str(valid_host)
									printOut[hostname]['readyValidateHostname'] = str(valid_host)
								if valid_path != [] and group == 'ARC':
									# dns name doesnt match Scaffolding
									out[hostname]['readyValidateHostname'] = False
									out[hostname]['inventoryPathing'] = str(valid_path)
									printOut[hostname]['readyValidateHostname'] = str(valid_path)
							continue
						for service in data[a]['children'][group]['children'][market]['children'].keys():
							if type(data[a]['children'][group]['children'][market]['children'][service]) is None or \
							data[a]['children'][group]['children'][market]['children'][service] is None: 
								# if service not in wc.services??
								continue
							if 'hosts' not in data[a]['children'][group]['children'][market]['children'][service].keys(): continue
							for hostname in data[a]['children'][group]['children'][market]['children'][service]['hosts'].keys():
								valid_host = wc.validateHostname(hostname)
								valid_path = hostname_path_compare(valid_host, {'lab':group,'market':market,'service':service})
								if hostname not in out.keys():
									out[hostname] = {'readyService:' + service:True,'ip':[]}
									out[hostname]['groups'] = [valid_host['lab'],valid_host['market'],valid_host['service'],valid_host['function']]
									printOut[hostname] = {'readyService:' + service: True}
								if valid_host['INVALID'] != []:
									out[hostname]['readyService:' + service] = False
									out[hostname]['namingStandard'] = str(valid_host)
									printOut[hostname]['readyService:' + service] = str(valid_host)
								if valid_path != [] and group == 'ARC':
									out[hostname]['readyService:' + service] = False
									out[hostname]['inventoryPathing'] = str(valid_path)
									printOut[hostname]['readyService:' + service] = str(valid_path)
								for d in facts.keys():
									if type(facts[d]['hostnames']) == str and facts[d]['hostnames'] == hostname:
										out[hostname]['ip'].append(d)
									elif type(facts[d]['hostnames']) == list and hostname in facts[d]['hostnames']:
										out[hostname]['ip'].append(d)
		summ = {}
		# check if scaffolding has working GetFacts
		for a2v in out.keys():
			out[a2v]['readyHasFacts'] = False
			if out[a2v]['ip'] == []:
				# no ip = not out
				out[a2v]['no_ip'] = True
				continue
			# for each deviceId get facts
			idDict = {}
			for ip in wc.lunique(out[a2v]['ip']):
				for hostId in facts[ip]['ids'].keys():
					facts[ip]['ids'][hostId]['ip'] = ip
					idDict[hostId] = facts[ip]['ids'][hostId]; # 'facts'
					if idDict[hostId]['facts_size'] not in [0,1,'0','1'] and \
					sorted(list(idDict[hostId]['facts'].keys())) != ['ansible_net_system', 'groups']:
						# if any deviceId has facts then out
						out[a2v]['readyHasFacts'] = True
						printOut[a2v]['readyHasFacts'] = True
					else:
						printOut[a2v]['readyHasFacts'] = False
			if 'ip' in idDict.keys():
				if len(idDict['ip']) == 1: idDict['ip'] = idDict['ip'][0]
			out[a2v]['facts'] = idDict

			# FINAL SUMMARY
			summ[a2v] = {}
			for i in [match for match in list(out[a2v].keys()) if "ready" in match]:
				if out[a2v][i] == False:  summ[a2v]['ready'] = False; wc.jd(printOut[a2v]); print(a2v);
				summ[a2v][i] = out[a2v][i]
			if 'ready' not in summ[a2v].keys(): summ[a2v]['ready'] = True
		return(out,summ)
	def GetFacts2(self,result,raw):
		# PAGED
		result = {}
		inventories = {}
		all_hosts = AWX.REST_GET(self,'/api/v2/hosts/')['results']
		wc.pairprint('all_hosts_count', len(all_hosts))
		scm_data = {}
		for host in all_hosts:
			try:
				host['variables'] = json.loads(host['variables'].replace("'",'"'))
			except Exception:
				host['variables'] = {'_': host['variables']}
			for scm_source in self.REST_GET(host['related']['inventory'] + 'inventory_sources/')['results']:
				host['summary_fields']['inventory']['url'] = self.REST_GET(scm_source['related']['source_project'])
			# wc.pairprint('\t' + str(host['variables']), host['name'] + '\t' + str(host['id']))

			if host['inventory'] not in inventories.keys():
				inventories[host['inventory']] = AWX.REST_GET(self,host['related']['inventory'])['name']

			# FOR IP ADDRESS HOST_VAR === CHANGE TO DNS???
			if 'ansible_host' in host['variables'].keys():
				ip = host['variables']['ansible_host']
				if ip == '':
					wc.pairprint('\tEXPECTED_FAIL_NO_CONNECTIVITY\t' + str(host['variables']), host['name'] + '\t' + str(host['id']))
				if ip not in result.keys():
					result[ip] = {'hostnames':'', 'ids':{}}
					# result[ip]['pingable'] = wc.is_pingable(ip)
				result[ip]['hostnames'] += ' ' + host['name'].upper()
				result[ip]['hostnames'] = ' '.join(sorted(wc.lunique(result[ip]['hostnames'].split(' ')))).strip()
				result[ip]['ids'][host['id']] = {'inventory': inventories[host['inventory']]}
				_FACTS = AWX.REST_GET(self, '/api/v2/hosts/%d/ansible_facts/' % host['id'])
				result[ip]['ids'][host['id']]['facts_size'] = len(list(_FACTS.keys()))
				# result[ip]['ids'][host['id']]['variables'] = host['variables']
				if result[ip]['ids'][host['id']]['facts_size'] != 0:
					if 'date_time' in _FACTS.keys():
						result[ip]['ids'][host['id']]['facts_timestamp'] = _FACTS['date_time']['date'] + ' ' + _FACTS['date_time']['time'] + ' ' + _FACTS['date_time']['tz']
					elif 'ansible_date_time' in _FACTS.keys():
						result[ip]['ids'][host['id']]['facts_timestamp'] = _FACTS['ansible_date_time']['date'] + ' ' + _FACTS['ansible_date_time']['time'] + ' ' + _FACTS['ansible_date_time']['tz']
					elif 'net_routing_engines' in _FACTS.keys():
						for re in _FACTS['net_routing_engines'].keys():
							formatter = '%Y-%m-%d %H:%M:%S %Z'
							start = int(time.mktime(time.strptime(_FACTS['net_routing_engines'][re]['start_time'], formatter)))
							add = _FACTS['net_routing_engines'][re]['up_time'].split(' ')
							add_sec = int(add[-2])
							add_sec = add_sec + int(add[-4]) * 60
							add_sec = add_sec + int(add[-6]) * 3600
							add_sec = add_sec + int(add[-8]) * 86400
							# wc.pairprint('add_sec', add_sec); exit(0)
							result[ip]['ids'][host['id']]['facts_timestamp'] = time.strftime(formatter, time.localtime(start + int(add_sec)))
							break
					interesting = {}
					interesting['groups'] = host['summary_fields']['groups']['results']
					interesting['ansible_net_system'] = []
					if 'network_os' in _FACTS.keys(): interesting['ansible_net_system'].append(_FACTS['network_os'].lower())
					elif 'ansible_net_system' in _FACTS.keys(): interesting['ansible_net_system'].append(_FACTS['ansible_net_system'])
					if interesting['groups'] != []:
						for g in interesting['groups']:
							interesting['ansible_net_system'].append(g['name'])
					elif 'ansible_devices' in _FACTS.keys(): interesting['ansible_net_system'].append('linux')
					if 'ansible_env' in _FACTS.keys():
						for attr in ['SSH_CONNECTION', 'USER']:
							if attr in _FACTS['ansible_env'].keys():
								interesting[attr] = _FACTS['ansible_env'][attr]
					if 'linux' in interesting['ansible_net_system']:
						# linux
						for ens in ['ens224', 'ansible_ens224']:
							if ens in _FACTS.keys():
								del _FACTS[ens]['features']
						for factoid in ['ens224', 'ansible_ens224', 'ansible_os_family', 'ansible_memory_mb', 'ansible_distribution', 'ansible_userspace_architecture', 'ansible_hostname', 'ansible_user_dir', 'ansible_cmdline']:
							if factoid in _FACTS.keys():
								interesting[factoid] = _FACTS[factoid]
							else:
								# interesting[factoid] = '_missing'
								pass
						if 'ansible_processor' in _FACTS.keys():
							interesting['ansible_processor'] = wc.lsearchAllInline2('.* CPU .*', _FACTS['ansible_processor'])
						if 'ansible_devices' in _FACTS.keys():
							for ad in _FACTS['ansible_devices'].keys():
								interesting['ansible_devices_' + ad] = {'model':_FACTS['ansible_devices'][ad]['model'],'vendor':_FACTS['ansible_devices'][ad]['vendor']}
						if 'ansible_interfaces' in _FACTS.keys():
							interesting['ansible_net_interfaces'] = {}
							for intf in _FACTS['ansible_interfaces']:
								if 'features' in  _FACTS['ansible_' + intf].keys():
									del  _FACTS['ansible_' + intf]['features']
								interesting['ansible_net_interfaces'][intf] = _FACTS['ansible_' + intf]
						for ad in wc.lsearchAllInline('ansible_devices_.*', list(_FACTS.keys())):
							interesting[ad] = {'model':_FACTS[ad]['model'],'vendor':_FACTS[ad]['vendor']}
					elif 'junipernetworks.junos.junos' in interesting['ansible_net_system'] or 'junos' in interesting['ansible_net_system']:
						_FACTS['ansible_net_config'] = wc.xml_loads(_FACTS['ansible_net_config'])
						interesting['ansible_net_interfaces_config'] = {}
						for ancii in _FACTS['ansible_net_config']['interfaces']['interface']:
							# convert to name = data
							interesting['ansible_net_interfaces_config'][ancii['name']] = ancii
						for ansible_attr in ['ansible_net_has_2RE', 'ansible_user_dir', 'net_api', 'ansible_net_memfree_mb', 'ansible_net_memtotal_mb', 'ansible_net_model', 'ansible_net_serialnum', 'ansible_net_system', 'ansible_net_version', 'ansible_hostname', 'ansible_net_hostname', 'ansible_net_routing_engines']:
							if ansible_attr in _FACTS.keys():
								interesting[ansible_attr] = _FACTS[ansible_attr]
							else:
								# interesting[ansible_attr] = '_missing'
								pass
						interesting['ansible_net_interfaces'] = _FACTS['ansible_net_interfaces']
						#for ansible_attr in wc.lsearchAllInline2('ansible_.*', _FACTS.keys()):
							#interesting[ansible_attr] = _FACTS[ansible_attr]
					elif 'icx' in interesting['ansible_net_system']:
						intf_locs = {}
						for parent in ['ansible_net_model', 'network_os', 'ansible_net_image', 'ansible_net_interfaces', 'ansible_hostname', 'ansible_net_hostname', 'ansible_net_version', 'ansible_net_serialnum', 'ansible_net_interfaces', 'ansible_net_memfree_mb', 'ansible_net_memtotal_mb']:
							if parent in _FACTS.keys():
								interesting[parent] = _FACTS[parent]
								if parent == 'ansible_net_interfaces':
									pp = list(interesting[parent].keys())
									for intf in pp:
										intf_locs[wc.icx_intf_format(intf)] = intf
										# interesting[parent][intf]
						interesting['ansible_net_config'] = _FACTS['ansible_net_config'].split('\n')
						interesting['ansible_net_interfaces_config'] = {}
						for cfgLine in interesting['ansible_net_config']:
							clean = wc.cleanLine(cfgLine)
							if cfgLine.startswith('stack unit'):
								parentLine = cfgLine
								intf_config = {cfgLine: []}
							elif cfgLine.startswith('  module'): intf_config[parentLine].append(cfgLine)
							elif cfgLine.startswith('  stack-port'):
								clean[-1] = wc.icx_intf_format(clean[-1])
								# intf_config[parentLine].append(' '.join(clean))
								if clean[-1] not in interesting['ansible_net_interfaces_config'].keys(): 
									interesting['ansible_net_interfaces_config'][clean[-1]] = []
								interesting['ansible_net_interfaces_config'][clean[-1]].append(intf_config)
							elif 'vlan' in clean and 'by' in clean and 'port' in clean:
								parentLine = cfgLine
								intf_config = {cfgLine: {'config':[], 'vlan': clean[1]}}
								if 'name' in clean: intf_config['name'] = clean[3]
							elif cfgLine.startswith(' tagged ') or cfgLine.startswith(' untagged '):
								if 'to' not in clean: 
									ports = [intf_locs[clean[-1]]]
									# wc.pairprint(clean[-1], ports)
								else:
									# tagged ethe 1/2/1 to 1/2/8
									ports = []
									for ps in wc.expand_slash_ports(clean[-3] + '-' + clean[-1].split('/')[-1]):
										ports.append(intf_locs[ps])
									# wc.pairprint(clean, ports)
								for port in ports:
									if port not in interesting['ansible_net_interfaces_config'].keys(): 
										interesting['ansible_net_interfaces_config'][port] = []
									interesting['ansible_net_interfaces_config'][port].append(intf_config)
									
							elif clean[0] == 'interface':
								l3port = intf_locs[clean[2]]
								parentLine = cfgLine
								intf_config = {cfgLine: []}
							elif 'ip' in clean and 'address' in clean:
								# interface ethernet 1/1/4\n ip address 192.168.0.166 255.255.255.0 dynamic
								intf_config['ip'] = ' '.join(clean[2:4])
								if l3port not in interesting['ansible_net_interfaces_config'].keys(): 
									interesting['ansible_net_interfaces_config'][l3port] = []
								interesting['ansible_net_interfaces_config'][l3port].append(intf_config)
						if 'ansible_net_stacked_models' in _FACTS.keys():
							 interesting['ansible_net_model'] = ' '.join( _FACTS['ansible_net_stacked_models'])
					elif 'commscope' in interesting['ansible_net_system']:
						# all is interesting = we built the driver
						# ansible_net_config2 is non-parsed AnsibleModule driver in template/e6k.parser.py
						# look at icx.get_facts.py to build our own AnsibleModule too
						interesting = _FACTS['ansible_raw']
					elif 'gainspeed' in interesting['ansible_net_system']:
						# ansible_cable_mac
						# | replace('.','')
						_FACTS['ansible_net_model'] = []
						_FACTS['ansible_net_serialnum'] = []
						_FACTS['ansible_net_interfaces'] = {}
						_FACTS['ansible_net_interfaces_config'] = {}
						_FACTS['ansible_net_serialnum'] = []
#						for slot in _FACTS['ansible_net_configuration']['data']['ccapproxy:ccap']['chassis']['slot']:
#							for port in slot['port']:
#								_FACTS['ansible_net_interfaces_config'][port['port-id']] = port
						for node in _FACTS['ansible_net_show_system']['data']['system:system']['node-discovery']:
							_FACTS['ansible_net_model'].append({'node:' + node['node-ip']:node['device-type']})
							_FACTS['ansible_net_serialnum'].append({'node:' + node['node-ip']:node['node-serial-number']})
						for f in _FACTS.keys():
							if not f.startswith('ansible_'): continue
							interesting[f] = _FACTS[f]
						try:
							interesting['ansible_net_hostname'] = interesting['ansible_net_configuration']['data']['tailf-aaa:session']
						except Exception:
							pass
						for node2 in _FACTS['ansible_cable_mac']['data']['node-oper-data:cable']:
							for upstream in node2['upstream-summary']['upstream-channel']:
								ppp = upstream['ucid']
								if ppp not in _FACTS['ansible_net_interfaces'].keys():
									_FACTS['ansible_net_interfaces'][ppp] = {'summary':{},'docs-mac-domain':{}}
								_FACTS['ansible_net_interfaces'][ppp]['summary']['ucid'] = ppp
								_FACTS['ansible_net_interfaces'][ppp]['summary']['ucid-modem-count'] = upstream['ucid-modem-count']
								_FACTS['ansible_net_interfaces'][ppp]['summary']['dir'] = 'upstream'
								_FACTS['ansible_net_interfaces'][ppp]['summary']['mac-domain-index'] = node2['mac-domain-index']
							for downstream in node2['downstream-summary']['primary-dcid']:
								ppp = downstream['dcid']
								if ppp not in _FACTS['ansible_net_interfaces'].keys():
									_FACTS['ansible_net_interfaces'][ppp] = {'summary':{},'docs-mac-domain':{}}
								_FACTS['ansible_net_interfaces'][ppp]['summary']['dcid'] = ppp
								_FACTS['ansible_net_interfaces'][ppp]['summary']['dcid-modem-count'] = downstream['dcid-modem-count']
								_FACTS['ansible_net_interfaces'][ppp]['summary']['dir'] = 'downstream'
								_FACTS['ansible_net_interfaces'][ppp]['summary']['mac-domain-index'] = node2['mac-domain-index']							
						for macdomain in _FACTS['ansible_net_configuration']['data']['ccapproxy:ccap']['docsis']['docs-mac-domain']['mac-domain']:
							primary_ds = macdomain.pop('primary-capable-ds')
							ofdm = macdomain.pop('ds-ofdm-channel-list')
							bonding_us = macdomain.pop('upstream-bonding-group')
							physical_us = macdomain.pop('upstream-physical-channel-ref')

							for _ds in primary_ds:
								_ds = '/'.join([str(_ds['slot']),str(_ds['ds-rf-port']),str(_ds['down-channel'])])
								if _ds not in _FACTS['ansible_net_interfaces'].keys(): _FACTS['ansible_net_interfaces'][_ds] = {'summary':{},'docs-mac-domain':{}}
								_FACTS['ansible_net_interfaces'][_ds]['docs-mac-domain'] = macdomain
								_FACTS['ansible_net_interfaces'][_ds]['docs-mac-domain']['_portType'] = 'primary-capable-ds'

							for _ofdm in ofdm:
								_ofdm = '/'.join([str(_ofdm['slot']),str(_ofdm['ds-rf-port']),str(_ofdm['ofdm-channel'])])
								if _ofdm not in _FACTS['ansible_net_interfaces'].keys(): _FACTS['ansible_net_interfaces'][_ofdm] = {'summary':{},'docs-mac-domain':{}}
								_FACTS['ansible_net_interfaces'][_ofdm]['docs-mac-domain'] = macdomain
								_FACTS['ansible_net_interfaces'][_ofdm]['docs-mac-domain']['_portType'] = 'ds-ofdm-channel-list'

							for group in bonding_us:
								groupname = group['bonding-group-name']
								for _us1 in group['upstream-logical-channel-ref']:
									logical = str(_us1['upstream-logical-channel'])
									_us1 = '/'.join([str(_us1['slot']),str(_us1['us-rf-port']),str(_us1['upstream-physical-channel'])])
									if _us1 not in _FACTS['ansible_net_interfaces'].keys(): _FACTS['ansible_net_interfaces'][_us1] = {'summary':{},'docs-mac-domain':{}}
									_FACTS['ansible_net_interfaces'][_us1]['docs-mac-domain'] = macdomain
									_FACTS['ansible_net_interfaces'][_us1]['docs-mac-domain']['_portType'] = 'upstream-bonding-group'
									_FACTS['ansible_net_interfaces'][_us1]['docs-mac-domain']['_groupName'] = groupname
									_FACTS['ansible_net_interfaces'][_us1]['docs-mac-domain']['_upstream-logical-channel'] = logical

#							for _us2 in physical_us:
#								_us2 = '/'.join([_us2['slot'],_us2['us-rf-port'],_us2['upstream-physical-channel']])
#								if _us2 not in _FACTS['ansible_net_interfaces'].keys(): _FACTS['ansible_net_interfaces'][_us2] = {'summary':{},'docs-mac-domain':{}}
#								_FACTS['ansible_net_interfaces'][_us2]['docs-mac-domain'] = macdomain
#								_FACTS['ansible_net_interfaces'][_us2]['docs-mac-domain']['_portType'] = 'physical-us'
						# docs-mac-domain
					elif 'none' in interesting['ansible_net_system']:
						result[ip]['ids'][host['id']]['facts_timestamp'] = ''
						result[ip]['ids'][host['id']]['facts_gathered'] = ''
						result[ip]['ids'][host['id']]['host_vars'] = host
					else:
						wc.pairprint('awx.GetFacts2 ', 'vendor %s not coded' % str(interesting['ansible_net_system']))
						exit(5)
					if 'ansible_hostname' in _FACTS.keys() and 'ansible_net_hostname' not in _FACTS.keys():
						# if no net_hostname then get ansible_hostname (might be ans.self.hostname?)
						interesting['ansible_net_hostname'] = interesting['ansible_hostname']
					elif 'ansible_hostname' in _FACTS.keys() and 'ansible_hostname' in _FACTS.keys():
						wc.pairprint('\n\nNO HOSTNAME IN FACTS???', host['name'] + '  ' + str(host['id']))
					if '_ansible_facts_gathered' in _FACTS.keys():
						result[ip]['ids'][host['id']]['facts_gathered'] = _FACTS['_ansible_facts_gathered']
					elif 'gather_subset' in _FACTS.keys():
						if _FACTS['gather_subset'] == ['all']:
							result[ip]['ids'][host['id']]['facts_gathered'] = True
						else:
							result[ip]['ids'][host['id']]['facts_gathered'] = _FACTS['gather_subset']
					else:
						# wc.pairprint('_ansible_facts_gathered: False',str(host['id']) + '  ' + host['name'])
						# print(_FACTS)
						# print('\n')
						result[ip]['ids'][host['id']]['facts_gathered'] = False
					result[ip]['ids'][host['id']]['facts'] = interesting
					result[ip]['ids'][host['id']]['host_vars'] = host
				else:
					# NO FACTS
					result[ip]['ids'][host['id']]['facts_timestamp'] = ''
					result[ip]['ids'][host['id']]['facts_gathered'] = ''
					result[ip]['ids'][host['id']]['host_vars'] = host
			else:
				# NO IP INFO -- DNS INFO?
				wc.pairprint('\tEXPECTED_FAIL_NO_CONNECTIVITY\t' + str(host['variables']), host['name'] + '\t' + str(host['id']))
				if '' not in result.keys():
					result[''] = {'ids': {}, 'hostnames':''}
				result['']['ids'][host['id']] = {'inventory': inventories[host['inventory']] + '_ButNotReachable', 'hostname':host['name']}
		for i in result.keys():
				if ' ' in result[i]['hostnames']:
					result[i]['hostnames'] = result[i]['hostnames'].split(' ')

		return(result)
	def GetInventory(self):
		_INV = {}
		data = json.loads(wc.REST_GET('http://' + self.IP + '/api/v2/inventories', user=self.user, pword=self.pword))
		for inventory in data['results']:
			# single page
			wc.pairprint(inventory['id'],inventory['name'])
			_INV[inventory['name']] = {}
			hosts = json.loads(wc.REST_GET('http://' + self.IP + inventory['related']['hosts'], user=self.user, pword=self.pword))
			for host in hosts['results']:
				print(host['name'])
				# single page
				mylist = AWX.mcsplit(host['variables'], ['\n', ': '])
				host['variables'] = AWX.list2dict(mylist)
				facts = json.loads(wc.REST_GET('http://' + self.IP + host['related']['ansible_facts'], user=self.user, pword=self.pword))
				interestingfact = {}
				interestingfact['id'] = host['related']['ansible_facts'].split('/')[4]
				if 'ansible_default_ipv4' in facts.keys():
					# has CIDR info (add cidr from device)
					cidr = str(AWX.IP_get(host['name'] + ' ' + facts['ansible_default_ipv4']['netmask'])[-1])
					interestingfact['networks'] = [ AWX.IP_get(host['name'] + '/' + cidr)[0] ]
					interestingfact['mac'] = facts['ansible_default_ipv4']['macaddress']
				if 'junos' in facts.keys():
					# JUNIPER
					interestingfact['model'] = facts['junos']['model']
					interestingfact['junos'] = {}
					for re in facts['junos']['junos_info'].keys():
						interestingfact['junos'][re] = facts['junos']['junos_info'][re]['text']
					interestingfact['dns'] = facts['ansible_dns']['search']
					interestingfact['api'] = facts['ansible_net_api']
					interestingfact['intf'] = {}
					for intf in facts['ansible_net_interfaces'].keys():
						interestingfact['intf'][intf] = '/'.join([facts['ansible_net_interfaces'][intf]['oper-status'],facts['ansible_net_interfaces'][intf]['admin-status']])
					if 'l3_interfaces' in facts['ansible_network_resources'].keys():
						for n in facts['ansible_network_resources']['l3_interfaces']:
							if 'ipv4' in n.keys():
								for block in n['ipv4']:
									interestingfact['networks'].append(block['address'])
				elif 'ansible_devices' in facts.keys():
					# LINUX
					interestingfact['ansible_devices'] = list(facts['ansible_devices'].keys())
					interestingfact['vendor'] = facts['ansible_devices']['sda']['host'] + ' '  + facts['ansible_devices']['sda']['vendor']
					interestingfact['hdd'] = facts['ansible_devices']['sda']['size']
				
				AWX.listprint('  ', [host['name'], host['enabled'], host['variables'], interestingfact])
				_INV[inventory['name']][interestingfact['id']] = {'Host':host['name'],
					'Enabled':host['enabled'],
					'Variables':host['variables'],
					'facts':interestingfact}
		# wc.jd(_INV)
		return(_INV)

