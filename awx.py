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
	def awx_job_events_format(je):
		# GET STDOUTLINES FROM COMPLETED JOB AND FORMAT
		new = {}
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
							wc.pairprint(i + '    ' + dump,'\n'.join(result['event_data']['res'][dump]))
							new[i][dump] = result['event_data']['res'][dump]
		return(new)
	def RunPlaybook(self,playbook_name,args={}):
		# ASYNC BY DEFAULT
		playbook_start = wc.timer_index_start()
		if args != {}:
			# wc.pairprint('REST:extra_vars', list(args.keys()))
			extra_vars = {'extra_vars':args}
			args = json.dumps(extra_vars)
		data = json.loads(wc.REST_POST('http://' + self.IP + '/api/v2/job_templates/' + playbook_name + '/launch/', user=self.user, pword=self.pword, args=args))
		status_url = data['url']
		data['status'] = 'Running'
		if 'job' not in data.keys():
			# SOMETHING WENT WRONG
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
		wc.pairprint('API','http://' + self.IP + data['related']['job_events'])
		raw = AWX.awx_job_events_format(raw)
		return(data['status'],raw)
		# ['related']['stdout']
		# POST https://your.tower.server/api/v2/job_templates/<your job template id>/launch/ with any required data gathered during the previous step(s). The variables that can be passed in the request data for this action include the following.
		# extra_vars: A string that represents a JSON or YAML formatted dictionary (with escaped parentheses) which includes variables given by the user, including answers to survey questions
		# job_tags: A string that represents a comma-separated list of tags in the playbook to run
		# limit: A string that represents a comma-separated list of hosts or groups to operate on
		# inventory: A integer value for the foreign key of an inventory to use in this job run
		# credential: A integer value for the foreign key of a credential to use in this job run
	def GetScaffolding(self):
		def hostname_path_compare(validation, gmsList):
			invalid = []
			# ARCUAT1K8WRK01 = '{'lab': 'ARC', 'market': 'UAT1', 'service': 'K8W', 'function': 'RK0', 'iteration': '1', 'INVALID': ['RK0']}'
			for gms in ['lab','market','service']:
				if gmsList[gms] == '': continue
				if validation[gms] != gmsList[gms]:
					invalid.append({'path':gmsList[gms],'hostnameSnippet':validation[gms]}) 
			return(invalid)
		out = {}
		path = './inventories/'
		for inventory_file in wc.exec2('ls ' + path).split('\n'):
			if not inventory_file.endswith('yml') and not inventory_file.endswith('yaml'):
				continue
			inventory_file = path + inventory_file
			print('\n' + inventory_file)
			data = wc.read_yaml(inventory_file)
			# wc.jd(data)
			# print(wc.log_yaml(data, 'new.yml'))
			for a in data.keys():
				for group in data[a]['children'].keys():
					for market in data[a]['children'][group]['children'].keys():
						if 'hosts' in data[a]['children'][group]['children'][market].keys():
							for hostname in data[a]['children'][group]['children'][market]['hosts'].keys():
								valid_host = wc.validateHostname(hostname)
								if valid_host['INVALID'] != [] or hostname_path_compare(valid_host, {'lab':group,'market':market,'service':service}) != []:
									# device not ready for sync
									print('\nDEVICE HOSTNAME NOT READY FOR SYNC:')
									wc.pairprint(hostname, valid_host)
									wc.pairprint(hostname, hostname_path_compare(valid_host, {'lab':group,'market':market,'service':service}))
							continue
						for service in data[a]['children'][group]['children'][market]['children'].keys():
							if type(data[a]['children'][group]['children'][market]['children'][service]) is None or \
							data[a]['children'][group]['children'][market]['children'][service] is None: continue
							if 'hosts' not in data[a]['children'][group]['children'][market]['children'][service].keys(): continue
							for hostname in data[a]['children'][group]['children'][market]['children'][service]['hosts'].keys():
								valid_host = wc.validateHostname(hostname)
								if valid_host['INVALID'] != [] or hostname_path_compare(valid_host, {'lab':group,'market':market,'service':service}) != []:
									# device not ready for sync
									print('\nDEVICE HOSTNAME NOT READY FOR SYNC:')
									wc.pairprint(hostname, valid_host)
									wc.pairprint(hostname, hostname_path_compare(valid_host, {'lab':group,'market':market,'service':service}))
	def GetFacts2(self,result,raw):
		# PAGED
		result = {}
		inventories = {}
		all_hosts = AWX.REST_GET(self,'/api/v2/hosts/')['results']
		wc.pairprint('all_hosts_count', len(all_hosts))
		for host in all_hosts:
			try:
				host['variables'] = json.loads(host['variables'].replace("'",'"'))
			except Exception:
				host['variables'] = {'_': host['variables']}
			# wc.pairprint('\t' + str(host['variables']), host['name'] + '\t' + str(host['id']))
			# wc.jd(host); exit(0)

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
					result[ip]['ids'][host['id']]['facts_gathered'] = _FACTS['_ansible_facts_gathered']
					interesting = {}
					if 'ansible_net_system' in _FACTS.keys():
						vendor = _FACTS['ansible_net_system']
					elif 'ansible_devices' in _FACTS.keys():
						vendor = 'linux'
					if vendor == 'linux':
						# linux
						if 'ens224' in _FACTS.keys():
							del _FACTS['ens224']['features']
						for factoid in ['ens224', 'ansible_memory_mb', 'ansible_distribution', 'ansible_userspace_architecture', 'ansible_hostname', 'ansible_user_dir']:
							if factoid in _FACTS.keys():
								interesting[factoid] = _FACTS[factoid]
							else:
								interesting[factoid] = '_missing'
						if 'ansible_processor' in _FACTS.keys():
							interesting['ansible_processor'] = wc.lsearchAllInline2('.* CPU .*', _FACTS['ansible_processor'])
						for ad in _FACTS['ansible_devices'].keys():
							interesting['ansible_devices_' + ad] = {}
							interesting['ansible_devices_' + ad]['model'] = _FACTS['ansible_devices'][ad]['model']
							interesting['ansible_devices_' + ad]['vendor'] = _FACTS['ansible_devices'][ad]['vendor']
						interesting['ansible_net_hostname'] = interesting['ansible_hostname']
					elif vendor == 'junos':
						# junos
						for ansible_attr in ['ansible_net_has_2RE', 'ansible_net_memfree_mb', 'ansible_net_memtotal_mb', 'ansible_net_model', 'ansible_net_serialnum', 'ansible_net_system', 'ansible_net_version', 'ansible_net_hostname', 'ansible_net_routing_engines']:
							if ansible_attr in _FACTS.keys():
								interesting[ansible_attr] = _FACTS[ansible_attr]
							else:
								interesting[ansible_attr] = '_missing'
						interesting['ansible_net_interfaces'] = len(list(_FACTS['ansible_net_interfaces'].keys()))
						#for ansible_attr in wc.lsearchAllInline2('ansible_.*', _FACTS.keys()):
							#interesting[ansible_attr] = _FACTS[ansible_attr]
					result[ip]['ids'][host['id']]['facts'] = interesting
				else:
					# NO FACTS
					result[ip]['ids'][host['id']]['facts_timestamp'] = ''
					result[ip]['ids'][host['id']]['facts_gathered'] = ''
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
		wc.jd(_INV)
		return(_INV)


# A = AWX(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
# wc.jd(A.GetFacts2())
# exit(0)



