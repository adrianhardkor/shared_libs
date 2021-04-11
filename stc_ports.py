#!/usr/bin/env python3
import sys, os, getopt
import subprocess
import time
shared_libs = '/opt/spirent/velocity-agent/shared_libs/'
os.environ['STC_PRIVATE_INSTALL_DIR'] = STC_PRIVATE_INSTALL_DIR = '/opt/STC_5.16/Spirent_TestCenter_5.16/Spirent_TestCenter_Application_Linux/'
sys.path.insert(1,shared_libs)
sys.path.insert(1,STC_PRIVATE_INSTALL_DIR + 'API/Python/')


def run(command):
    # execute shell command, handle stdout stderr
    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
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

# STC
import Stc
if 'VELOCITY_PARAM_RESERVATION_ID' in wc.env_dict.keys():
	# PULL STC from TOPOLOGY/RESERVATION
	_CHASSIS_IP,_CHASSIS_NAME = wc.vagent_getStcResource(resourceDict, inventory)
else:
	# NOT RUNNING RESERVATION, GET PARAMETER
	_CHASSIS_NAME = wc.env_dict['VELOCITY_PARAM_python_parameter']
	_CHASSIS_IP = inventory[_CHASSIS_NAME]['ipAddress']['value']

# CONNECT to STC
wc.pairprint('[INFO] ' + _CHASSIS_IP, _CHASSIS_NAME)
system1,project = Stc.init('stcVelocityDriver.py')
Stc.disconnectChassis()
Stc.connectChassis(_CHASSIS_IP)
physical = Stc.getConnectedChassisPhysical([_CHASSIS_IP])
Stc.disconnectChassis()
physical['//' + _CHASSIS_IP]['VELOCITY_NAME'] = _CHASSIS_NAME; # pair StcPython and velocity classes
# wc.jd(physical)

# UPDATE DEVICE
V.UpdateDevice(_CHASSIS_NAME, 'Model', physical['//' + _CHASSIS_IP]['PartNum'] + '  ' + physical['//' + _CHASSIS_IP]['FirmwareVersion'])
V.UpdateDevice(_CHASSIS_NAME, 'Serial Number', physical['//' + _CHASSIS_IP]['SerialNum'])

# UPDATE SLOT
for slot in physical['//' + _CHASSIS_IP]['slots'].keys():
	if physical['//' + _CHASSIS_IP]['slots'][slot]['ports'] == {}:
		continue


	# UPDATE PORT
	for port in physical['//' + _CHASSIS_IP]['slots'][slot]['ports'].keys():
		slotNum = port.split('/')[-2]
		portNum = port.split('/')[-1]
		slotName = 'S' + slotNum
		portName = slotNum + '/' + portNum
		new_descr = []
		# new_descr.append(str(physical['//' + _CHASSIS_IP]['slots'][slot]['PartNum']))
		OwnershipState = physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['OwnershipState']
		new_descr.append(OwnershipState)
		new_descr.append(physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['OwnerUserId'])
		new_descr.append(physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['OwnerTimestamp'])
		# new_descr.append(physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['LinkStatus'])
		# new_descr.append(physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['LineSpeedStatus'])
		# auto-creates name: slotName/portName
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'description', '/'.join(new_descr))
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'Port Type', str(physical['//' + _CHASSIS_IP]['slots'][slot]['PartNum']))
		wc.pairprint('LineSpeedStatus', physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['LineSpeedStatus'])
		try:
			V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'Port Speed', int(physical['//' + _CHASSIS_IP]['slots'][slot]['ports'][port]['LineSpeedStatus']))
		except Exception:
			V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'Port Speed', 0)
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'isLocked', bool(OwnershipState != 'OWNERSHIP_STATE_AVAILABLE'))
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'isReportedByDriver', True)
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'linkChecked', int(time.time()))
		V.UpdatePort(_CHASSIS_NAME, slotName, portName, 'lastModified', int(time.time()))
		# isOnline
