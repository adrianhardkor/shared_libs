#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re


import paramiko
k = paramiko.RSAKey.from_private_key_file("/opt/paramiko-test-key")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect( hostname = "10.88.232.24", username = "admin", password = 'admin') 
# pkey = k 
commands = [ 'set paginate false', 'show config | match prompt']
for command in commands:
	print("Executing {}".format( command ))
	stdin , stdout, stderr = c.exec_command(command)
	print(wc.bytes_str(stdout.read()))
	print( "Errors")
	print(stderr.read())
c.close()

