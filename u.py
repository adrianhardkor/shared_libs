#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re

def raw():
	import paramiko
	k = paramiko.RSAKey.from_private_key_file("/opt/paramiko-test-key")
	paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
	c = paramiko.SSHClient()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect( hostname = "10.88.240.77", username = "admin", password = 'a10') 
	# pkey = k 
	commands = [ '', 'show ver', 'enable', '', 'terminal length 0', 'show ip int']
	for command in commands:
		print("Executing {}".format( command ))
		stdin , stdout, stderr = c.exec_command(command)
		print(wc.bytes_str(stdout.read()))
		print( "Errors")
		print(stderr.read())
	c.close()

# raw()

def para():
	paramiko_args = {}
	paramiko_args['commands'] = [ '', 'enable', '', 'terminal length 0', 'show version']
	paramiko_args['ip'] = '10.88.240.77'
	paramiko_args['driver'] = 'a10t'
	paramiko_args['username'] = 'admin'
	paramiko_args['password'] = 'a10'
	paramiko_args['become'] = ''
	paramiko_args['ping'] = False
	paramiko_args['quiet'] = False
	paramiko_args['buffering'] = ''
	paramiko_args['settings_prompt'] = "([a-zA-Z0-9\-\.\(\)\_\ ]+[\[\/\]0-9]+[>#])"
	# wc.jd(paramiko_args)
	raw = wc.PARA_CMD_LIST(**paramiko_args)

para()
