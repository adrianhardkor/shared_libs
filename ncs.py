#! /usr/bin/env python3
import wcommon as wc
import os
import json
from requests import Session
import hmac
import hashlib



class NCS():
	def __init__(self, host, key, secret_hmac):
		self.host = host
		self.key = key
		self.secret_hmac = secret_hmac
		self.url = 'https://' + self.host + '/json.pl'
		self.headers = {'HMAC': self.secret_hmac, 'KEY': self.key}
	def make_digest(self, message, key):
		key	 = bytes(key, 'UTF-8')
		message = bytes(message, 'UTF-8')
		digester = hmac.new(key, message, hashlib.sha1)
		return(digester.hexdigest())
	def Format(self, data, reindex={}):
		out = {}
		for d in data['results']:
			ID = d['fields']['id']['value']
			if ID not in out.keys(): out[ID] = {}
			for f in d['fields'].keys():
				if str(d['fields'][f]['value']) == 'null':
					d['fields'][f]['value'] = None
				if f in reindex.keys(): ff = reindex[f]
				else: ff = f
				out[ID][ff] = d['fields'][f]['value']
		return(out)
	def REST_POST(self, endpoint, args={}):
		timer = wc.timer_index_start()
		s = Session()
		base_api_url = self.url + endpoint
		json_payload = json.dumps(args)
		# wc.pairprint(base_api_url, json_payload)
		hmac_key = self.secret_hmac
		digest = self.make_digest(base_api_url, hmac_key)
		self.headers['HMAC'] = digest
		data = s.post(self.url + endpoint, headers=self.headers, data={'json': json_payload})
		wc.pairprint(endpoint, wc.timer_index_since(timer))
		return(data.json())
	def Update(self, multiplexer, index, value):
		index = str(index)
		value = str(value)
		data = self.REST_POST('/multiplexers/update/' + str(self.INV[multiplexer]['id']), args={'fields':{index:{'data':value}}})
		print('\t'.join(['UPDATE',multiplexer,index,value]))
		for m in ['success']:
			wc.pairprint(m, data[m])
		data = self.Format(data)
		for ID in list(data.keys()):
			# Always 1 ID - 1 device updated
			name = data[ID]['network_element_tid']
			data[name] = data.pop(ID)
		wc.pairprint(index, value + '\t' + str(data[name][index]))
		self.INV[name][index] = data[name][index]
	def LoadTables(self):
		self.Tables = {}
		self.Tables['multiplexer_manufacturer_id'] = self.Format(self.REST_POST('/multiplexer_manufacturers/list'))
		self.Tables['multiplexer_model_id'] = self.Format(self.REST_POST('/multiplexer_models/list'))
		self.Tables['multiplexer_owner_id'] = self.Format(self.REST_POST('/multiplexer_owners/list'))
		self.Tables['multiplexer_status_id'] = self.Format(self.REST_POST('/multiplexer_statuses/list'), reindex={'label':'name'})
		self.Tables['site_location_id'] = self.Format(self.REST_POST('/site_locations/list'))
		self.Tables['rack_id'] = self.Format(self.REST_POST('/racks/list'))
		# wc.jd(self.Tables['rack_id']); exit(0)
		# for rack in self.Tables['rack_id'].keys():
		# 	wc.pairprint(rack, self.Tables['rack_id'][rack]['label'])
	def GetUneditableIndexes(self, data):
		update = {'True':[],'False':[]}
		for d in data['results']:
			for field in d['fields'].keys():
				update[str(d['fields'][field]['updatable']).strip()].append(field)
		wc.jd(update)
	def GetInventory(self, site_location_id):
		data = self.REST_POST('/multiplexers/list', args = {'criteria':{'site_location_id':{'operator':'=','data':str(site_location_id)}}})
		# wc.pairprint('data',data)
		self.GetUneditableIndexes(data)
		data = self.Format(data)
		for device in list(data.keys()):
			mydevice = data.pop(device)
			wc.pairprint(mydevice['id'], mydevice['network_element_tid'])
			data[mydevice['network_element_tid']] = mydevice
			device = mydevice['network_element_tid']; # id into name
			for attr in data[device].keys():
				if attr in self.Tables.keys() and data[device][attr] != None:
					if attr == 'site_location_id' or attr == 'rack_id':
						data[device][attr] = self.Tables[attr][data[device][attr]]
						continue
					if 'name' not in self.Tables[attr][data[device][attr]].keys():
						wc.jd(self.Tables[attr][data[device][attr]])
						print(attr)
					data[device][attr] = {'id': str(data[device][attr]), 'name': self.Tables[attr][data[device][attr]]['name']}
		self.INV = data
		return(data)
key = wc.argv_dict['KEY']
myhmac = wc.argv_dict['SECRET']
N = NCS('wow-sandbox.n-c-s.net', key=key, secret_hmac=myhmac)
N.LoadTables()
N.INV = N.GetInventory('61325')
# wc.jd(N.INV)
N.Update('adrian_wopr_test1','rack_id','61797')
