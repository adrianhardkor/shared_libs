#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

wc.jd({'id': '94e1e91c-a1bb-41ea-8c9e-a1a5cefafb95', 'name': '1/11', 'description': '', 'templateId': 'a5266606-f35b-482b-8c3f-a4317c1ccbb9', 'groupId': '3d0591b8-1c10-42ad-a969-8d3e621f1d4f', 'parentId': '9345477b-4cb4-4587-91cd-e4436f6bff64', 'parentName': 'stc01', 'connectedPortId': None, 'connectedPortName': None, 'connectedPortParentId': None, 'connectedPortParentName': None, 'connectedPortLinkPlace': None, 'connectionType': None, 'connectedPortCableId': None, 'connectedPortCableTypeId': None, 'backConnectedPortId': None, 'backConnectedPortName': None, 'backConnectedPortParentId': None, 'backConnectedPortParentName': None, 'backConnectedPortLinkPlace': None, 'backConnectionType': None, 'backConnectedPortCableId': None, 'backConnectedPortCableTypeId': None, 'isOnline': False, 'isLocked': False, 'isShared': False, 'linkChecked': 1612567408642, 'isReportedByDriver': False, 'creatorId': 'dacaaf56-847b-494a-bd6f-751b4c1be14e', 'created': 1610569228976, 'lastModifierId': 'dacaaf56-847b-494a-bd6f-751b4c1be14e', 'lastModified': 1612568554223, 'lastAction': 'MODIFIED', 'deviceInterface': 'NONE', 'deviceLocation': None, 'lockUtilizationType': None, 'isEphemeral': False, 'properties': [{'definitionId': 'b395be08-5628-4f68-b069-42d6cf7ec466', 'name': 'portNumber', 'value': '1/11', 'type': 'TEXT', 'groupName': 'System Identification', 'description': 'System port number. Example: 1.1.1', 'isRequired': True, 'availableValues': None}, {'definitionId': '52b1cb81-9a4b-44aa-83d2-3320fb10d12c', 'name': 'Port Type', 'value': 'DX3-100GO-T12', 'type': 'TEXT', 'groupName': 'System Identification', 'description': 'Example: Ethernet, Fast Ethernet, Copper..., etc', 'isRequired': False, 'availableValues': None}, {'definitionId': 'f828c9cd-e6db-4f93-b147-386dccd95e98', 'name': 'Port Speed', 'value': '0', 'type': 'INTEGER', 'groupName': 'System Identification', 'description': 'Unit of Measure:  Mbps', 'isRequired': False, 'availableValues': None}, {'definitionId': '4f36711a-a3a9-428f-9bb8-a42fdac1aa59', 'name': 'description', 'value': 'OWNERSHIP_STATE_AVAILABLE//', 'type': 'TEXT', 'groupName': 'System Identification', 'description': '', 'isRequired': False, 'availableValues': None}]})

def VelocityReportParse(html_data):
	out = []
	from bs4 import BeautifulSoup
	parsed = BeautifulSoup(html_data, features="html.parser")
	flag = 0
	for line in parsed.find_all('span'):
		if line.text.startswith('['): flag = 1
		if flag:
			out.append(line.text)
	return('\n'.join(out))
	
