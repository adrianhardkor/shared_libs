#!/usr/bin/env python3
import sys, os, getopt
import subprocess
shared_libs = '/opt/spirent/velocity-agent/shared_libs/'
os.environ['STC_PRIVATE_INSTALL_DIR'] = STC_PRIVATE_INSTALL_DIR = '/opt/STC_5.16/Spirent_TestCenter_5.16/Spirent_TestCenter_Application_Linux/'
sys.path.insert(1,shared_libs)
sys.path.insert(1,STC_PRIVATE_INSTALL_DIR + 'API/Python/')


def run(command):
    # execute shell command, handle stdout stderr
    output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (stdout, stderr) = output.communicate()
    return(stdout.decode('utf-8').strip())

# GIT And WCOMMON
git = run('cd ' + shared_libs + '; git pull;')
import wcommon as wc
wc.wcheader['wc'] = wc.__file__
wc.pairprint('[INFO] gitpull', git.split('\n'))
# run('python3 -m pip install -r ' + shared_libs + 'requirements.txt')


# VELOCITY
V,resourceDict = wc.print_vagent_header(); # resource name:id
inventory = V.GetInventory(); # ipAddress

_LEPTON_NAME = os.environ['VELOCITY_PARAM_python_parameter']




# LEPTON
import lepton
# requires 'value' because type(properties)=dict (with uuid)
LEP = lepton.LEPTON(inventory[_LEPTON_NAME]['ipAddress']['value'], inventory[_LEPTON_NAME]['username']['value'], inventory[_LEPTON_NAME]['password']['value'])
status = LEP.GetStatus()

# Apply LEPTON class to VELOCITY-INVENTORY-LEPTON
for port in status['ports'].keys():
	speed = wc.lunique(status['ports'][port]['Speed'])
	if len(speed) == 1:
		speed = speed[0]
	else:
		speed = ' '.join(speed)
	speed = int(speed * 1000); # lepton in list(GB), velocity in int(MB)
	# wc.pairprint(port,speed)
	V.ChangeDevicePortProp(inventory, _LEPTON_NAME, port, 'Port Speed', speed)
wc.pairprint('[INFO] ' + _LEPTON_NAME, str(len(status['ports'].keys())) + ' portspeed updated')
