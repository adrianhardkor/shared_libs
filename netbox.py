#!/usr/bin/env python3
import time
import os
import sys
import wcommon as wc
import json
import re
import requests



class NETBOX():
        def __init__(self, IP, user, token):
                self.user = user
                self.token = token
                self.headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': 'Token ' + str(self.token)
                }
                self.IP = 'https://' + IP
                self.Tenants = {}
                self.Roles = {}
                self.Sites = {}
                self.__name__ = 'NETBOX'
                self.INV = {}
        def REST_GET(self, url):
                if '?' in url: _CHAR = '&'
                else: _CHAR = '?'
                return(requests.get(self.IP + url, headers=self.headers, verify=False).json())
        def REST_POST(self, url, payload):
                if '?' in url: _CHAR = '&'
                else: _CHAR = '?'
                return(requests.post(self.IP + url, headers=self.headers, verify=False, data=json.dumps(payload)).json())
        def ChangeIPAM(self, tenant_name, ip_cidr, name):
                data = {'address':ip_cidr}
                data['tenant'] = int(self.Tenants[tenant_name])
                if name in self.INV.keys():
                        data['device'] = self.INV[device]['id']
                        pass
                else:
                        data['dns_name'] = data['description'] = name + '__unverified'
                wc.jd(self.REST_POST('/api/ipam/ip-addresses/', data))
        def GetIPAM(self, tenant_name):
                # https://netbox.cmh.wowcloud.biz/api/ipam/aggregates/
                self.IPAM = self.REST_GET('/api/ipam/ip-addresses/?tenant=' + tenant_name)['results']
                wc.jd(self.IPAM)
                wc.jd(self.REST_GET('/api/ipam/aggregates/?tenant=' + tenant_name))
        def GetInventory(self, tenant_name):
                self.Roles['ipam'] = {}
                for role1 in self.REST_GET('/api/ipam/roles')['results']:
                        role1['id'] = str(role1['id'])
                        self.Roles['ipam'][role1['slug']] = role1['id']
                        self.Roles['ipam'][role1['id']] = role1['slug']
                self.Roles['device_role'] = {}
                for device in self.REST_GET('/api/dcim/devices/?tenant=' + tenant_name)['results']:
                        if device['tenant']['slug'] not in self.Tenants.keys(): self.Tenants[device['tenant']['slug']] = device['tenant']['id']
                        if device['site']['slug'] not in self.Sites.keys(): self.Sites[device['site']['slug']] = device['site']['id']
                        if device['device_role']['slug'] not in self.Roles['device_role'].keys():
                                self.Roles['device_role'][device['device_role']['slug']] = device['device_role']['id']
                                self.Roles['device_role'][str(device['device_role']['id'])] = device['device_role']['slug']
                        self.INV[device['name']] = device
                # wc.jd(self.INV)
                # wc.jd(self.Roles)
                # wc.jd(self.Tenants)
                # wc.jd(self.Sites)
                return(self.INV)

N = NETBOX(wc.env_dict['NETBOX'], wc.env_dict['NETBOX_USER'], wc.env_dict['NETBOX_TOKEN'])
# wc.jd(N.GetInventory('arc-lab'))
N.GetIPAM('arc-lab')
# N.ChangeIPAM('arc-lab', '10.88.240.250', 'adrian_test')
