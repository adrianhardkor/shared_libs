from __future__ import print_function
import datetime
import copy
import subprocess
import ipaddress
from collections import defaultdict
from time import sleep
import time
import sys
import csv
import json
import platform
import os
import re
import getpass
# import shutil
import binascii
import requests
import paramiko
import uuid
import urllib3
from bs4 import BeautifulSoup
import deepdiff
import yaml
urllib3.disable_warnings()

def import_or_install(package):
    import pip
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])     
packages = ['datetime','platform','copy','subprocess','ipaddress','xml','collections','time','sys','csv','json','os','re','getpass','shutil','binascii','requests','paramiko','urllib3','uuid']

try:
    basestring
except NameError:
    # python3
    basestring = str

global env_dict
global argv_dict
global wow_time
global clock_format
clock_format = '%a, %d %b %Y %H:%M:%S GMT'

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

def xml_loads(xml_string):
	from xml.etree import cElementTree as ElementTree
	root = ElementTree.XML(xml_string.replace('\n',''))
	xml = XmlDictConfig(root)
	return(xml)
	return(json.loads(json.dumps(xml)))

def xml_loads2(my_xml):
	import xmltodict
	return(json.loads(json.dumps(xmltodict.parse(my_xml))))
	# json.dumps(xmltodict.parse(my_xml)))

def bdd_bool_inp(inp2):
	if str(inp2).lower() == 'true':
		return(True)
	elif str(inp2).lower() == 'false':
                return(False)

def now():
    # CURRENT TIME
    return(time.ctime(time.time()))

def jd(mydict):
    # json.dumps shorthand
    out = json.dumps(mydict, sort_keys=True, indent=2)
    print(out)
    pairprint('Timestamp',fullRuntime())
    print('\n')
    return(out)

def compareDict(old,new):
	out = deepdiff.DeepDiff(old,new)
	out = json.dumps(str(out))
	out = json.loads(out)
	return(out)

def compareList(old,new):
	out = {'added':[],'removed':[]}
	for o in old:
		if o not in new:
			# pairprint('compareList removed', o)
			out['removed'].append(o)
	for n in new:
		if n not in old:
			# pairprint('compareList added', n)
			out['added'].append(n)
	if out == {'added':[],'removed':[]}: return(True)
	else: return(False)

def read_yaml(fname):
    return(yaml.load(read_file(fname), Loader=yaml.FullLoader))

def log_yaml(data, fname):
    with open(fname, 'w') as file:
        doc = yaml.dump(data, file, sort_keys=True)
    return(read_file(fname))


def lindex_exists(ls, i):
    return (0 <= i < len(ls)) or (-len(ls) <= i < 0)

def listprint(d, l):
	newl = []
	for ll in l:
		newl.append(str(ll))
	print(d.join(newl))

def timer_index_start():
    # timer sub-commands
    global timer
    timer = time.time()
    return(timer)

# Init wow-common library timestamp (start of scripts)
wow_time = timer_index_start()

def wait_start():
    # animation scroller for waiting for things to work
    global animation
    global idx
    animation = "|/-\\"
    idx = 0


def expand(unformatted):
    # 1-3 into [1,2,3]
    result = []
    unformatted = unformatted.split('-')
    start = int(unformatted[0])
    while start <= int(unformatted[1]):
        result.append(start)
        start += 1
    # pairprint(unformatted, result)
    return(result)


def wait_update():
    # animation scropper for waiting for things to work
    global animation
    global idx
#    try:
#        print(animation[idx % len(animation)], end="\r")
#    except SyntaxError:
#        print(animation[idx % len(animation)])
    idx += 1


def do_nothing():
    return()


def encode(s):
    s = str(s)
    unic = 'utf-8'
    s = bytes(s, unic)
    s = binascii.hexlify(s)
    # s = s.decode(unic)
    return(s)


def decode(s):
    unic = 'utf-8'
    un = binascii.unhexlify(s)
    un = un.decode(unic)
    return(un)


def genUUID(identifyer=''):
    # convert from input, so UUID always same, if same input
    if identifyer != '':
        myUUID = uuid.uuid3(uuid.NAMESPACE_X500, identifyer)
    else: myUUID = str(uuid.uuid4())
    # myUUID = ''
    # pairprint(identifyer, myUUID)
    return(str(myUUID))


def covertMaskToCIDR(netmask):
    # 255.255.255.0 = 24
    return(sum(bin(int(x)).count('1') for x in netmask.split('.')))


def IP_get(n):
    # GET ATTRIBUES FOR CIDR BLOCK
    # >>> from netaddr import IPAddress
    # >>> IPAddress('255.255.255.0').netmask_bits()
    # 24
    n = n.strip()
    cidr_split = mcsplit(n, '/ ')
    cidr = ipaddress.IPv4Network((cidr_split[0],cidr_split[1])).prefixlen
    try:
        addr4 = ipaddress.ip_interface(n)
    except ValueError:
        return(['', ''])
    netAddress = str(addr4.network)
    try:
        net = ipaddress.ip_network(netAddress)
        hosts = []
        for ip in net:
            hosts.append(str(ip))
        if bool([cidr_split[0]] == hosts):
            return([str(addr4.network), ''])
        elif cidr_split[1] != '31' and cidr_split[1] != '255.255.255.254':
            hosts.pop()
            hosts.pop(0)
        return([str(addr4.network), hosts])
    except Exception as err:
        return([str(addr4.network), err])

def IP_lsort(unsorted_list):
	new_list = []
	for element in unsorted_list:
		new_list.append(ipaddress.ip_address(element))
	new_list.sort()
	out = []
	for n in new_list:
		out.append(str(n))
	return(out)

def sorted_dict(inDict):
    # sort in-dict (without .dumps)
    result = {}
    for i in sorted(inDict):
        result[i] = inDict[i]
    return(result)


def dict_move(myDict, old, new):
    # move to new mem space
    if old == new: return(myDict)
    myDict[new] = myDict[old]
    del myDict[old]
    return(myDict)

def cleanLine(line):
    # split by space and tab, and special char's
    # used as an 'awk'
    result = []
    mcs = mcsplit(line, ' \t')
    for word in mcs:
        if word != '':
            result.append(word)
    return(result)


def lfind(myList, what):
    # return list of indexes
    return([i for i, x in enumerate(myList) if x == what])
    try:
        result = myList.index(what)
    except ValueError:
        result = -1
    return(result)


def per(unit, of):
    # percentage handler
    # echo_param({'unit': unit, 'of': of})
    unit = float(unit)
    of = float(of)
    major = unit / of
    major = major * 100
    return(str(int(major)) + '%')


def cp(element):
    # deepcopy handler
    # cp = timer_index_start()
    result = copy.deepcopy(element)
    # pairprint('deepcopy', timer_index_since(cp))
    return(result)

def qcp(element):
        # quick copy for large dict - new mem spaces
        result = ''
        if type(element) is dict:
                result = {}
                for tag in element:
                        if type(element[tag]) == str:
                                result[tag] = str(element[tag])
                        elif type(element[tag]) == list:
                                result[tag] = []
                                for l in element[tag]:
                                        result[tag].append(l)
                        else:
                                print('qcp failure')
                                exit(5)
        return(result)

def str_int_split(raw):
    # ge-1/0/8 = ['ge', '-1/0/8']
    # Gigabit0/1 = ['Gigabit', '0/1']
    strings = []
    integers = []
    for r in list(raw):
        if r.isdigit():
            integers.append(str(r))
        else: strings.append(r)
    return(''.join(strings), ''.join(integers))


def could_be_int(element):
    # if type could be int
    if element == '':
        return(1)
    try:
        blah = float(element) + 1
        return(1)
    except Exception:
        return(0)


def grep(re, output):
    # grep regex against string
    result = []
    for line in output.split('\n'):
        if string_match(re, line): result.append(line)
    result = "\n".join(result)
    return(result)


def ls(path):
    # os.exec an ls $path
    result = sorted(exec2('ls ' + path).split('\n'))
    for popMe in lfind(result, ''): result.pop(popMe)
    return(result)


def return_code_error(message):
    # python handler for TCL thinking
    message = "\n\n%s" % message
    raise Exception(message)


def split(word):
    return [char for char in word]


def lremove(myList, element):
    return([x for x in myList if element not in x])

def fname_age(fname):
    global clock_format
    try:
        fname_epoch = os.path.getmtime(fname)
    except FileNotFoundError:
        return(['',''])
    my_epoch = current_time
    age = int(my_epoch) - int(fname_epoch)
    return([age, time_epoch_human(age)])

def fname_age_check(fname):
    age = fname_age(fname)
    try:
        if int(age[1][0]) > 0:
            pass
    except IndexError:
        pass 

def rmf(fname):
    # remove file
    try:
        return(os.remove(fname))
    except OSError as err:
        return(err)


def rmrf(dirname):
    # remove dir
    try:
        result = shutil.rmtree(dirname)
    except OSError as e:
        result = 'Warning: %s - %s' % (e.filename, e.strerror)
    return(result)

def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, 'a').close()

def exec2(command):
    # execute shell command, handle stdout stderr
    output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (stdout, stderr) = output.communicate()
    return(bytes_str(stdout).strip())

def bytes_str(data):
    try:
        # data = data.decode("utf-8")
        data = data.decode("utf-8")
    except Exception:
        pass
    return(data)

def str_insert(old,num,new):
    return(old[:num] + new + old[num:])

def post_fname(data, fname):
    # write data to fname
    f = open(fname, "a")
    for line in data.split('\n'):
        f.write(line)
    f.close()
    return(data)

def log_fname(data, fname):
    # write data to fname
    f = open(fname, "a+")
    for line in data.split('\n'):
        f.write(line + '\r\n')
    f.close()
    return(data)

def read_binary_file(fname):
    # if read_file fails as binary-file, retry as binary
    result = []
    try:
        f = open(fname, 'rb')
    except FileNotFoundError:
        return('')
    return(f.readlines())
    with open(fname, 'rb') as f:
        for line in f.readline():
            result.append(line)
    return(result)


def read_file(fname):
    # read file, if fails, try as binary
    try:
        f = open(fname, "r")
    except FileNotFoundError:
        return('')
    try:
        contents = f.read()
    except UnicodeDecodeError:
        return(read_binary_file(fname))
    except Exception:
        return('')
    contents = contents.strip('\r')
    contents = contents.strip('\n')
    return(contents)


def log_json(mydict, fname):
    # write dict to fname file as json.dumps
    myjson = json.dumps(mydict, sort_keys=True, indent=2)
    f = open(fname, "w")
    f.write(myjson)
    f.close()

def list_match(regex, mylist):
    # same as re.match
    r = re.compile(regex)
    return(list(filter(r.match, mylist)))


def string_match(regex, word):
    # old TCL thinking, regex against string
    if regex in word: return(True)
    else: return(False)
    return bool(re.search(regex, word))

def mcstrip(mystr, cc):
    # handler for multiple strips
    chars1 = []
    chars1[:0] = cc
    for c in chars1:
        mystr = mystr.strip(c)
    return(mystr)

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

def execPy(command):
    # exec via os.system
    out = os.system(command)
    return out

def timer_index_since(index=-1):
    # time handler
    if index == -1:
        global timer
    else:
        timer = index
    x = (time.time() - timer) * 1000
    return(float("{0:.2f}".format(x)))

def array_get(ary):
    # TCL handler for ary/dict
    return sorted(ary.items())

def lunique(list1):
    # lunique handler for list
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)

def Merge(dict1, dict2):
    dict2.update(dict1)
    return(dict2)

def lflatten(object):
	gather = []
	for item in object:
		if isinstance(item, (list, tuple, set)):
			gather.extend(lflatten(item))			
		else:
			gather.append(item)
	return(gather)

def findList(regex, mylist):
	return(lsearchAllInline(regex, mylist))

def lsearchAllInline(regex, mylist):
    return([name for name in mylist if regex in name])

def lsearchAllInline2(regex, mylist):
    # find via re
    r = re.compile(regex)
    newlist = list(filter(r.match, mylist))
    return(newlist)

def pairedList(myl):
    # ['eng1', 'WOPR', 'eng2', 'VOLTRON'] = 
    # {'eng1': 'WOPR', 'eng2': 'VOLTRON'}
    result = {}
    for i in range(0, len(myl), 2):
        index = str(myl[i]).strip()
        value = str(myl[i + 1])
        # pairprint(index, value)
        if index in result:
            # append
            if type(result[index]) is str:
                # pairprint('already', type(result[index]))
                # new
                spare = result[index]
                result[index] = []
                result[index].append(spare)
            result[index].append(value)
        else: result[index] = value
        # print('\t' + str(result))
    return(result)


def echo_param(ary):
    # print dict pretty
    return(parray_slow(ary))

def pairprint(i, v, printMe=True):
    # print (i,v) pretty
    result = "%s = '%s'" % (str(i), str(v))
    if printMe:
        print(result)
    else:
        return(result)

def parray_slow(ary):
    # print no matter what type()
    # template = "{0:20}|{1:20}"
    border = "==========================================="
    print(border)
    if type(ary) is dict:
        for i, v in array_get(ary):
            print("%s = '%s'" % (str(i).ljust(20), v))
    elif type(ary) is str:
        jd(ary)
    elif type(ary) is list:
        for i, v in pairedList(ary):
            print("%s = '%s'" % (str(i).ljust(20), v))
    print(border)
    return("")

def sendmail(destinations, subject, data, source='wopr-sb@arc.ninjaneers.net'):
    if destinations == '': return()
    data = str(data).replace("'","").replace('\t','    ').replace('\\t','    ')
    dest = ','.join(mcsplit(destinations, ', '))
    print('\t'.join(['SENDMAIL:', subject, dest.strip(), send_email_single(dest, subject, data.replace("'",""), source)]))
    return()


def send_email_single(dest, subject, data, source='wopr-sb@arc.ninjaneers.net'):
    start = timer_index_start()
    sendmail_location = "sendmail"
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % source)
    p.write("To: %s\n" % dest)
    p.write("Subject: %s\n" % subject)
    p.write("\n") 
    p.write(str(data))
    p.write("\n") 
    status = p.close()
    try:
        # push p to complete fast
        p.write("\n")
    except ValueError:
        do_nothing()
    if str(status) == 'None': status = 'Success, took %s' % str(timer_index_since(start))
    return(status)


# SSH
def run_commands_paramiko(commands, IP, driver, remote_conn, quiet):
    result = paramiko_send_expect(commands, IP, remote_conn, driver, quiet)
    return(result)

def device_buffering_commands(driver):
    commands = []
    if driver == "cisco_ios": commands = ['term len 0', '']
    elif driver == 'commscope': commands = ['terminal length 0']
    elif driver == "cisco_nxos": commands.insert(0, 'terminal length 0')
    elif driver == "juniper_junos": commands.insert(0, 'set cli screen-length 0')
    elif driver == 'mrvTS': commands.insert(0,'no pause')
    elif driver == 'mrv_mcc':
        commands.insert(0,'term width 512')
        commands.insert(0,'term len 0')
    else: pairprint(driver, 'device_buffering_commands')
    return(commands)

def device_prompt(tn, driver):
    runtime_device_prompt = timer_index_start()
    # capture prompt instead of setting prompt
    str2 = ''
    while str2 == '':
        tn.send("\n")
        time.sleep(.4)
        str2 = bytes_str(tn.recv(65535))
        str2 = str2.split('\r\n')[-1]
        # print(" - Waiting.. '%s'" % str2)
    global prompt
    prompt = str2
    print("DEVICE PROMPT = \'%s\' Took %s" % (str2, timer_index_since(runtime_device_prompt)))
    return(str2)

def get_prompt():
    global errorPrompt
    default = "hf3023f23jfg02gn30n23ggm}{}:<>"
    global prompt
    prompt = {}
    errorPrompt = {}
    prompt['cisco_ios'] = "([a-zA-Z0-9\-\.\(\)\_]*[>#])"
    errorPrompt['cisco_ios'] = "(nable to get configuratio)"
    prompt['commscope'] = "([a-zA-Z0-9\-\.\(\)\_]*[># ])"
    errorPrompt['commscope'] = errorPrompt['cisco_ios']
    prompt['cisco_nxos'] = "([a-zA-Z0-9\-\.\(\)\_]*[># ])"
    errorPrompt['cisco_nxos'] = default
    prompt['juniper_junos'] = "([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])"
    errorPrompt['juniper_junos'] = default
    # prompt['f5'] = "([\[]+[a-zA-Z0-9\:\;\.\-\_]+[@]+[a-zA-Z0-9\(\)\/\~\_\-\:\;\ ]+[\]])|([a-zA-Z0-9\:\;\.\-\_]+[@]+[a-zA-Z0-9\/\~\_\-\(\)\:\;\ \(\)\]]+[#])|\(tmos\)\# "
    errorPrompt['f5'] = default

    prompt['mrvTS'] = "([a-zA-Z0-9\-\_]+[0-9\:\ ]+[>])"
    errorPrompt['mrvTS'] = "(Syntax Error)"
    prompt['mrv_mcc'] = "([a-zA-Z0-9\-\.\(\)\_]+[#]+[\ ])"
    errorPrompt['mrv_mcc'] = errorPrompt['cisco_ios']
    return()

def mgmt_login_paramiko(ip, username, driver, quiet, password='', key_fname='', ping=True, buffering=''):
    global login_diff
    login_time = timer_index_start()
    global wow_time
    if ping:
        ping_result = is_pingable(ip)
        print('PING %s:  %r @ %s' % (ip, ping_result, timer_index_since(WOW_time)))
        if ping_result == False:
            return_code_error("\n\nUnexpected error:\nPing:%s" % ping_result)
    global paramiko_buffer
    global sleep_interval
    global prompt
    global passwords
    global result
    result = {}
    paramiko_buffer = 65535
    # driver-less
    if buffering != '': commands = buffering.split(',')
    else: commands = device_buffering_commands(driver)

#    if password == '':
#        # global via dict/json
#        password = passwords[ip]

    port = 22
    sleep_interval = .6
    remote_conn_pre = paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if not quiet: echo_param({'IP': ip, 'port': port, 'username': username, 'pre-commands': commands})
    if key_fname != '':
        pairprint('using key', key_fname)
        try:
            remote_conn_pre.connect(ip, port=port, username=username, pkey = paramiko.RSAKey.from_private_key_file(key_fname))
        except Exception:
            return_code_error("\n\nUnexpected error, user %s: %s" % (username, sys.exc_info()[0]))
    else:        
        print('not using key')
        try:
            remote_conn_pre.connect(ip, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
        except Exception:
            return_code_error("\n\nUnexpected error, user %s: %s" % (username, sys.exc_info()[0]))
    # print('Connection Built.. DONE:%s @ %s' % (timer_index_since(login_time), timer_index_since(wow_time)))

    remote_conn = remote_conn_pre.invoke_shell()
    init = remote_conn.recv(paramiko_buffer)

    # pre-commands
    result = {'_':{'_': bytes_str(init)}, '_buffering': paramiko_send_expect(commands, ip, remote_conn, driver, quiet)}

    if not quiet: print(result)
    login_diff = timer_index_since(login_time)
    result['_']['login'] = login_diff
    return(remote_conn)

def prompt_check(output, remote_conn, IP, prompt_status, quiet):
    # paramiko_ready(remote_conn, prompt_status, quiet)
    last_line = output.split('\n')
    # print("prompt_check '%s'" % last_line[-1])
    print('.', end='')
    if string_match("assword", last_line[-1]):
        global passwords
        password = passwords[IP]
        remote_conn.send(password)
        time.sleep(0.03)
        remote_conn.send('\n')
        print('PASSWORD FOUND: %s' % last_line[-1])

def paramiko_ready(remote_conn, command, quiet, check):
    time.sleep(.4)
    while remote_conn.recv_ready() is False:
        # Not Ready
        time.sleep(0)
    if not quiet: print("\n\nReady/Sending:  '%s' = %r" % (command, remote_conn.recv_ready()))

def paramiko_send_expect(commands, IP, remote_conn, driver, quiet):
    global runcommands_diff
    diff = timer_index_start()
    s = '\n'
    global sleep_interval
    global result
    global prompt
    global paramiko_buffer
    thisPrompt = '.*%s$' % prompt[driver]
    regexPrompt = re.compile(thisPrompt)
    commandIndex = 1
    for command in commands:
        result[str(commandIndex) + command] = []
        timer_index_start()
        output = ''
        check = 1
        if string_match('enable', command): check = 1

        remote_conn.send(command + '\n')
        time.sleep(.6)
        paramiko_ready(remote_conn, command, quiet, check)

        prompt_status = regexPrompt.search(output)
        while prompt_status is None:
            if check: prompt_check(output, remote_conn, IP, prompt_status, quiet)
            buff = bytes_str(remote_conn.recv(paramiko_buffer))
            if not quiet: print(buff)
            output += buff
            time.sleep(0.3)
            prompt_status = regexPrompt.search(output)

        result[str(commandIndex) + command].append(output)
        result[str(commandIndex) + command] = s.join(result[str(commandIndex) + command]).lstrip(command)
        if not quiet: print(output)
        try:
            result['_'][str(commandIndex) + command] = timer_index_since()
        except KeyError:
            pass
        print("DONE: '%s', took '%s'" % (command, timer_index_since()))
        commandIndex = commandIndex + 1
    runcommands_diff = timer_index_since(diff)
    return(result)

def humanSize(fileSize):
    fileSize = float(fileSize)
    divider = 1000.0
    for count in ['Bytes', 'KB', 'MB', 'GB']:
        if fileSize >= divider:
            # print("%3.1f%s" % (fileSize, count))
            fileSize = fileSize / divider
        else:
            return("%3.1f%s" % (fileSize, count))
    return("%3.1f%s" % (fileSize, 'TB'))

def IP_DNS(ID):
    # check if IP valid or dns-name
    if IP_get(ID + '/24')[0] != '':
        return('IP')
    else: return('DNS')

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def expand_slash_ports(port):
        result = []
        if type(port) == str:
                port = port.split('/')
                channels = expand(port.pop(-1))
        elif type(port) == list:
                # expand_e6k_channels = '['12/0/0-30', ['32']]'
                sOne = port[0].split('/')
                # print(sOne)
                channels = expand(sOne[2])
                for p in port[1]:
                        channels.append(p)
                port = [sOne[0],sOne[1]]
        for channel in channels:
                result.append('/'.join([port[0],port[1],str(channel)]))
        return(result)

def icx_intf_format(raw):
	# first int of char+
	i = 0
	flag = False
	for char in raw:
		isint = is_int(char)
		if isint and flag and str(char) != '.':
			return(raw[i::])
		elif not isint and str(char) != '.': flag = True
		i = i + 1
	return('')

def is_pingable(IP):
    global matcher
    if IP == '': return(False)
    timer_index_start()
    global wcheader
    if 'darwin' in wcheader['platform']['os'].lower():
        ping_cmd = 'ping -c 2 '
    elif 'win' in wcheader['platform']['os'].lower():
        ping_cmd = 'ping -n 2 -w 3 '
    else:
        ping_cmd = 'ping -c 2 -W 3 '
    possible_zero_loss = [" 100.0% packet los", " 100% packet los", "100% loss"]
    output = exec2(ping_cmd + IP)
    result = True
    for zero in possible_zero_loss:
        if zero in str(output):
            result = False
    return(result)

def PARA_CMD_LIST(commands=[], ip='', driver='', username='', password='', become='', key_fname='', quiet=False,ping=True,windowing=True, settings_prompt='', buffering=''):
    global passwords
    try:
        passwords[ip] = become; # BECOME = priv15 is global 
    except NameError:
        passwords = {ip:become}
    global wow_time
    global login_diff
    global runcommands_diff
    # global errorPrompt
    global prompt

    if windowing == False:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_fname != '':
            k = paramiko.RSAKey.from_private_key_file(key_fname)
            c.connect( hostname = ip, username = username, pkey = k )
        else:
            c.connect( hostname=ip, username=username, password=password)
        o = []
        for command in commands:
            stdin , stdout, stderr = c.exec_command(command)
            o.append(bytes_str(stdout.read()))
        c.close()
        return(o)

    if settings_prompt != '': prompt = {driver: settings_prompt}
    else: get_prompt(); # regex list 'global prompt'
    spawnID = mgmt_login_paramiko(ip, username, driver, quiet, password, key_fname, ping=ping, buffering=buffering)
    if spawnID == -1:
        return('')

    timer_index_start()
    output = run_commands_paramiko(commands, ip, driver, spawnID, quiet)
    # command_time = timer_index_since()

    discontime = timer_index_start()
    # spawnID.disconnect(); # kills process, doesnt kill session
    spawnID.send('exit' + '\n'); # kills session
    disconnect_time = timer_index_since(discontime)

    # if not quiet:
    print("\n\n PARA_CMD_LIST Summary at %s" % timer_index_since(wow_time))
    print(" - Login Took: %s" % login_diff)
    print(" - Output Took: %s" % runcommands_diff)
    print(" - Exit Took: %s" % disconnect_time)
    sumIs = login_diff + runcommands_diff + disconnect_time
    print(" TOTAL Took: %s @ %s" % (float("{0:.2f}".format(sumIs)), timer_index_since(wow_time)))

    # if string_match(errorPrompt[driver], output): return_code_error('Unknown Error on Switch: %s' % output)
    return(output)

def grep_until(begin, ending, data):
    # 'show run', 'end', list(output) 
    flag = 0
    result = []
    for each in data:
        if string_match(begin, each): flag = 1
        if string_match(ending, each): flag = 0
        if flag: result.append(each)
        # pairprint(each, flag)
    return(result)

def REST_GET(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, user='', pword='', verify=False, params={}):
    # RETURNS JSON
    data = {}
    # print('\t' + url)
    response = requests.get(url, auth=(user, pword), headers=headers, verify=verify, params=params)
    if response.status_code != 200:
        data['url'] = url
        data['user'] = user
        data['response.status_code'] = str(response.status_code)
        data['Headers'] = {}
        for h in response.headers:
            data['Headers'][h] = response.headers[h]
        data['response.request.body'] = bytes_str(response.request.body)
        data['Response'] = str(response)
    else:
        try:
            data = response.json()
        except Exception:
            data = REST_responseHandler(response, url, user)
            data['text'] = response.text
    return(json.dumps(data))

def REST_DELETE(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, args={}, user='', pword='', verify=False, convert_args=False):
    # RETURNS JSON
    data = {}
    if convert_args:
        args = json.dumps(args)
    response = requests.delete(url, auth=(user, pword), headers=headers, verify=verify, data=args)
    if response.status_code not in [200, 201]:
        data['url'] = url
        data['user'] = user
        data['response.status_code'] = str(response.status_code)
        data['Headers'] = {}
        for h in response.headers:
            data['Headers'][h] = response.headers[h]
        data['response.request.body'] = bytes_str(response.request.body)
        data['Response'] = str(response)
    else: 
        try:
            data = response.json()
        except Exception:
            data = REST_responseHandler(response, url, user)
            data['text'] = response.text
    return(json.dumps(data))

def REST_responseHandler(response, url, user):
    dd = {}
    dd['url'] = url
    dd['user'] = user
    dd['response.status_code'] = str(response.status_code)
    dd['Headers'] = {}
    for h in response.headers:
        dd['Headers'][h] = response.headers[h]
    try:
        dd['response.request.body'] = json.loads(bytes_str(response.request.body))
    except Exception:
        dd['response.request.body'] = bytes_str(response.request.body)
    dd['response.body'] = bytes_str(response.content)
    dd['Response'] = str(response)
    return(dd)

def REST_POST(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, user='', pword='', args={},verify=False,convert_args=False):
    # RETURNS JSON
    dd = {}
    if convert_args:
        args = json.dumps(args)
    response = requests.post(url, auth=(user, pword), headers=headers, data=args, verify=verify)
    if response.status_code not in [201, 200]:
        dd = REST_responseHandler(response, url, user)
    else:
        # 200 or 201 = success
        try:
            dd = response.json()
        except Exception:
            dd = REST_responseHandler(response, url, user)  
            dd['text'] = response.text
    return(json.dumps(dd))

def REST_PUT(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, user='', pword='', args={},verify=False,convert_args=False):
    # RETURNS JSON
    dd = {}
    if convert_args:
        args = json.dumps(args)
    response = requests.put(url, auth=(user, pword), headers=headers, data=args, verify=verify)
    if response.status_code not in [201, 200]:
        dd['url'] = url
        dd['user'] = user
        dd['response.status_code'] = str(response.status_code)
        dd['Headers'] = {}
        for h in response.headers:
            dd['Headers'][h] = response.headers[h]
        dd['response.request.body'] = bytes_str(response.request.body)
        dd['response.body'] = str(response.content)
        dd['Response'] = str(response)
    else:
        # 200 or 201 = success
        try:
            dd = response.json()
        except Exception:
            dd = REST_responseHandler(response, url, user)  
            dd['text'] = response.text
    return(json.dumps(dd))

def REST_UPLOAD(url, fname, DB=''):
	payload = {'upload_file':fname, 'OUT':fname.split('.')[-1].lower(), 'SHORT':'short'}
	if DB != '': payload['DB'] = DB
	files = {'file': open(fname,'rb')}
	pairprint('[INFO] ', payload)
	data2 = requests.post(url, files=files, data=payload, verify=False)
	return(json.dumps({'response': str(data2)}))

def time_epoch_human(myTime):
    # epoch = [10, 6, 3, 2]
    day = myTime // (24 * 3600)
    myTime = myTime % (24 * 3600)
    hour = myTime // 3600
    myTime %= 3600
    minutes = myTime // 60
    myTime %= 60
    seconds = myTime
    return([day, hour, minutes, seconds])

def roundMe(numm):
    return(float("{0:.2f}".format(numm)))

def fullRuntime():
    global wow_time
    timer = timer_index_since(wow_time)
    # sec = str(float("{0:.2f}".format(timer / 1000)))
    # return(sec + 'sec')
    return(str(timer) + 'ms')

# INIT
def PyVersion():
    # win/linux
    return('.'.join([str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2])]))

def platform2():
    plat = {}
    plat['os'] = platform.platform()
    plat['processor'] = platform.processor()
    plat['machine'] = platform.machine()
    return(plat)

def what_server():
    if platform2()['os'].startswith('Windows'):
        return(exec2('hostname'))
    else:
        return(str(os.uname()[1]))

def whoami():
    if platform2()['os'].startswith('Windows'):
        return(exec2('whoami'))
    else:
        return(getpass.getuser())

def what_path():
    if platform2()['os'].startswith('Windows'):
        return(exec2('echo %cd%'))
    else:
        return(os.getcwd())

def add_pkgs():
    output = {}
    try:
        from pip._internal.operations import freeze
    except Exception:
        try:
                from pip.operations import freeze
        except Exception:
                return(output)
    for pkg in freeze.freeze():
        pkg = pkg.split('==')
        if pkg[0] in packages:
            output[pkg[0]] = pkg[-1]
    return(output)

def load_argv():
    global argv_dict
    argv_dict = dict()
    for user_input in sys.argv[1:]:
        if "=" not in user_input: continue
        varname = user_input.split("=")[0]
        varvalue = user_input.split("=")[1].split(',')
        if len(varvalue) == 1: varvalue = varvalue[0]
        argv_dict[varname] = varvalue
        # pairprint(varname, varvalue)

def load_env():
	global env_dict
	env_dict = {}
	if platform2()['os'].startswith('Windows'):
		cmd = 'set'
	else:
		cmd = 'printenv'
	out = exec2(cmd)
	for line in exec2(cmd).split('\n'):
		line = line.split('=')
		index = line.pop(0)
		env_dict[index] = '='.join(line)
	return(env_dict)	

global labs
global markets
global services
global functions
def validateHostname(hostname):
    hostname = hostname.replace(' ','').replace('-','')
    # print(hostname)
    global labs
    global markets
    global services
    global functions
    labs = ['ARC']
    markets = ['UAT1', 'UAT2', 'VDC1', 'MDEV', 'NDEV', 'SIT1', 'CLOD', 'BKBN', 'PODS', 'EDGE']
    services = ['UAT', 'EDG', 'HUB', 'HUA', 'HUC', 'HUH', 'VDC', 'CLD']
    # services = '%s%s%s'
    functions = ['COR', 'LBD', 'CIN', 'BBR', 'EPR', 'VAR', 'DAR', 'DRR', 'CMR', 'MSR', 'AGS', 'SWI', 'POD', 'BAR', 'OTN', 'CMT', 'VCE', 'FRW', 'TRM', 'L1S', 'TST', 'STC', 'W1S', 'VEL', 'AWX', 'DNS', 'K8M', 'K8W']
    # iterations = '%d%d'
    INVALID = []
    components = {}
    components['lab'] = hostname[:3].upper()
    if components['lab'] not in labs: INVALID.append(components['lab'])
    components['market'] = hostname[3:7].upper()
    if components['market'] not in markets: INVALID.append(components['market'])
    components['service'] = hostname[7:10].upper()
    if components['service'] not in services: INVALID.append(components['service'])
    # if re.search('...', components['service']) is False: INVALID.append(components['service'])
    components['function'] = hostname[10:13].upper()
    if components['function'] not in functions: INVALID.append(components['function'])
    components['iteration'] = hostname[13:].upper()
    if re.search('..', components['iteration']) is False: INVALID.append(components['iteration'])
    components['INVALID'] = INVALID
    if INVALID == []:
        # pairprint('Valid',hostname)
        # print(json.dumps(components, indent=2))
        pass
    else:
        # pairprint('Invalid: ' + hostname, INVALID)
        pass
    return(components)

def getFnameScaffolding(fname_list, directory=''):
	result = {}
	for f in fname_list:
		lf = f.lower()
		sf = mcsplit(lf, ['.','/'])
		if 'yml' in sf and ('dcim' in sf or 'itsm' in sf or 'cable' in sf) and len(f.split('-')) >= 5:
			if sf[2] not in result.keys(): result[sf[2]] = {'dcim':None,'itsm':None,'cable':None}
			result[sf[2]][sf[3]] = read_yaml(directory + f)
	return(result)

def intfListCmd(itsm):
	intfList = []
	if itsm['settings'] == 'juniper_junos':
		cmd = 'show_interface_terse_|_display_json'
		attempt = json.loads(REST_GET('http://10.88.48.21:5000/aie?settings=%s&hostname=%s&cmd=%s' % (itsm['settings'],itsm['ip'], cmd)))
		if 'err' in attempt.keys(): return(False,intfList)
		for intfs in attempt['1show interface terse | display json']['interface-information']:
			for intf in intfs['physical-interface']:
				for name in intf['name']: name = name['data']
				for admin in intf['admin']: admin = admin['data']			
				for oper in intf['oper']: oper = oper['data']
				intfList.append({name: '/'.join([admin,oper])})
	return(True,intfList)

def validateITSM(fname_list, directory='', CIDR='10.88.0.0/16'):
	result = {}
	data = getFnameScaffolding(fname_list,directory=directory)
	for device in data.keys():
		result[device] = {}
		result[device]['data'] = data[device]
		itsm = data[device]['itsm']
		for k in itsm.keys():
			itsm[k.lower()] = itsm.pop(k); # lower all keys
		result[device]['valid'] = {}
		result[device]['valid']['allFilesExist'] = True
		for fname in ['dcim', 'itsm', 'cable']:
			if data[device][fname] == None: result[device]['valid']['allFilesExist'] = False
		if 'ip' not in itsm.keys() or 'settings' not in itsm.keys():
			result[device]['valid']['itsm:ip in CIDR:' + CIDR] = False
			result[device]['valid']['itsm:ip pingable'] = False
			result[device]['valid']['itsm:settings Worked'] = False
		else:
			result[device]['valid']['itsm:ip pingable'] = is_pingable(itsm['ip'])
			result[device]['valid']['itsm:ip in CIDR:' + CIDR] = bool(itsm['ip'] in IP_get(CIDR)[1])
			worked,intfList = intfListCmd(itsm)
			result[device]['valid']['itsm:settings Worked'] = worked
			result[device]['valid']['itsm:intfList'] = intfList
	return(result)


def jenkins_header():
	global env_dict
	global wcheader
	for inp in env_dict.keys():
		if inp.startswith('jenkins_'):
			if 'jenkins' not in wcheader.keys():
				wcheader['jenkins'] = {}
			wcheader['jenkins'][inp] = env_dict[inp]
		else:
			wcheader[inp] = env_dict[inp]

def FindAnsibleHost(ansible_host, INV):
	# Could be used for multiple repos?
	vByIP = {}
	for d in INV.keys():
		# pairprint(d,INV[d]['ipAddress'])
		if str(INV[d]['ipAddress']['value']).strip() == str(ansible_host).strip():
			# pairprint('Velocity Device Found by ansible_host_ip', d)
			return(INV[d])
		else:
			vByIP[str(INV[d]['ipAddress']['value']).strip()] = str(ansible_host).strip()
	# jd(vByIP)
	return({})

def print_vagent_header():
	# ASSUMES RUNNING ON VAGENT
	V = None
	global env_dict
	global wcheader
	import velocity
	jenkins_header()
	reserved_topology_resources = {}
	for inp in sorted(env_dict.keys()):
		if inp.startswith('VELOCITY_PARAM_'):
			pairprint('[INFO] ' + inp, env_dict[inp])
	if 'VELOCITY_PARAM_VELOCITY_TOKEN' in env_dict.keys():
		ip = env_dict['VELOCITY_PARAM_VELOCITY_API_ROOT'].split('/')[-1]
		token = env_dict['VELOCITY_PARAM_VELOCITY_TOKEN']
		V = velocity.VELOCITY(env_dict['VELOCITY_PARAM_VELOCITY_API_ROOT'].split('/')[-1], token=env_dict['VELOCITY_PARAM_VELOCITY_TOKEN'])
		if 'VELOCITY_PARAM_RESERVATION_ID' in env_dict.keys():
			vEnv = V.GetAgentReservation(env_dict['VELOCITY_PARAM_RESERVATION_ID'])
			pairprint('[INFO] creatorId', vEnv['activeRes']['creatorId'])
			pairprint('[INFO] topologyName', vEnv['activeRes']['topologyName'])
			pairprint('[INFO] reservationName', vEnv['name'])
			pairprint('[INFO] reservationStatus', vEnv['activeRes']['status'] + ' until ' + vEnv['activeRes']['end'])
			for resource in vEnv['resources'].keys():
				if vEnv['resources'][resource]['parentId'] is None:
					name = vEnv['resources'][resource]['name']; # devices
				else:
					name = vEnv['resources'][resource]['parentName'] + '_' + vEnv['resources'][resource]['name']; # intfs
				reserved_topology_resources[name] = vEnv['resources'][resource]['id'] 
	pairprint('[INFO] reserved_topology_resources, ' + str(V), sorted(list(reserved_topology_resources.keys())))
	return(V,reserved_topology_resources); # object-return, dict(resources: uuid's)

def vagent_getStcResource(resources, master_topology):
	# INV: dns-naming right now, IP?
	for t in resources.keys():
		if t.lower().startswith('n12') or t.lower().startswith('n11') or 'stc' in t.lower():
			if '_' not in t: return(master_topology[t]['ipAddress']['value'],t)

def GetStcPortMappings(_CHASSIS_NAME, _CHASSIS_IP, resourceDict, V, L):
	out = {}
	global TopologyRoles
	count = 1
	for reserved_stc_port in lsearchAllInline2(_CHASSIS_NAME + '_', list(resourceDict.keys())):
		stc_port = reserved_stc_port.split('_')[-1]
		split_stc_port = mcsplit(stc_port, ['S','P'])
		connections = list(V.INV[_CHASSIS_NAME]['ports'][stc_port]['connections'].keys())
		if connections == []: pairprint(reserved_stc_port, 'HAS NO PHYSICAL CONNECTIONS in VELOCITYY'); sys.exit(1)
		else:
			connection = GetMapping(connections[0], L, V).split('_')
			if 'lep' in connection[0]:
				connectedDevice = connection[-2]
				connectedIntf = connection[-1]
			else:
				connectedDevice = connection[0]
				connectedIntf = connection[1]
			# pairprint('[INFO]  ' + reserved_stc_port, connection)
			for role in TopologyRoles.keys():
				if role in str(connection):
					if TopologyRoles[role] + str(count) in out.keys():
						count = count + 1
					out[TopologyRoles[role] + str(count)] = '/'.join(['','',_CHASSIS_IP,split_stc_port[1],split_stc_port[-1]])
	return(out)

def GetMapping(connection, L, V):
	for lepAwk in [1,-1]:
		if connection.split('_')[lepAwk] in L.INV['ports'].keys():
			mapping = sorted(list(L.INV['ports'][connection.split('_')[lepAwk]]['MAP'].keys()))
			if len(mapping) > 1:
				pairprint(reserved_stc_port, 'LEPTON HAS 3+ PORTS IN CURRENT MAPPING -- VELOCITY BUILT INVALID MAP')
				sys.exit(1)
			lepton_far_port = mapping[0]
			# pairprint('[INFO]  ' + reserved_stc_port, list(V.INV['lepton01']['ports'][lepton_far_port]['connections'].keys())[0].split('_'))
			# jd(list(V.INV['lepton01']['ports'].keys()))
			sLeptonPort = lepton_far_port.split('.')
			if len(sLeptonPort[-1]) == 1: sLeptonPort[-1] = '0' + sLeptonPort[-1]
			return(list(V.INV['lepton01']['ports']['.'.join(sLeptonPort)]['connections'].keys())[0])

def StcGetCSV(MH, iteration='', care=''):
	# MH logger
	try:
		data = exec2('find ./ -name *.csv')
		# MH._LOGGER('AllFiles: ' + data.replace('\n','  '))
		# pairprint('[INFO] exec', data.replace('\n','  '))
		for fname in str(data).split('\n'):
			MH._LOGGER('Filename: ' + fname + '  with careTag:"' + care + '" = ' + str(bool(care in fname)))
			if care != '':
				if care not in fname: continue; # fnames we dont care about
			localname = str(fname.split('/')[-1]).replace('+','').replace('-','').replace('_','')
			if iteration != '': 
				localname = ''.join(['log',str(iteration),'iter',localname])
			print(exec2('cp ' + fname + ' ./' + localname))
			MH._UPLOAD(localname)
			MH._LOGGER('http://' + MH.flaskIP + ":" + MH.flaskPort + '/download?fname=' + localname)
			rmf('./' + localname); # dont rename existing log1iter files
	except Exception as err1:
		pairprint('[INFO] StcGetCSV', str(err1))
	# MH._LOGGER('CSV Export Complete')

wait_start()
global current_time
current_time = time.time()

def header():
    global wcheader
    # current_time = time.localtime()
    return(echo_param(wcheader))

global wcheader
wcheader = {'Runtime': time.strftime(clock_format, time.localtime()), 'hostname': what_server(), 'whoami': whoami()}
wcheader['paths'] = {'pyVer': PyVersion(), 'pwd': what_path(), 'pyExec': sys.executable, 'runfile': sys.argv[0]}
wcheader['packages'] = add_pkgs() 
wcheader['platform'] = platform2()
load_argv()
load_env()
wcheader['InitializingTime'] = fullRuntime()
