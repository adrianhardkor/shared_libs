#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
data = '''{"intfs": {"1": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "Ethernet CPE Interface", "ifType": "6", "ifIndex": "1", "ifMtu": "1500", "ifSpeed": "1000000000", "ifPhysAddress": "60:19:71:72:6b:d4", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "1462888", "ifInUcastPkts": "9688", "ifInDiscards": "9688", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "2723372", "ifOutUcastPkts": "42551", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "2": {"portGroup": "", "ipNetToMediaPhysAddress": "60:19:71:72:6b:d5 10.88.17.6", "ifDescr": "RF MAC Interface", "ifType": "127", "ifIndex": "2", "ifMtu": "1500", "ifSpeed": "0", "ifPhysAddress": "60:19:71:72:6b:d5", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "5869848", "ifInUcastPkts": "53746", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "4729302", "ifOutUcastPkts": "11203", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "3": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface", "ifType": "128", "ifIndex": "3", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "4287011637", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "4": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Upstream Interface", "ifType": "129", "ifIndex": "4", "ifMtu": "1764", "ifSpeed": "30720000", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "0", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "1612398", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "2"}, "48": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 1", "ifType": "128", "ifIndex": "48", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40945996", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "49": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 2", "ifType": "128", "ifIndex": "49", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40939868", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "50": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 3", "ifType": "128", "ifIndex": "50", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40911928", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "51": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 4", "ifType": "128", "ifIndex": "51", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40942751", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "52": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 5", "ifType": "128", "ifIndex": "52", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40994858", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "53": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 6", "ifType": "128", "ifIndex": "53", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40980466", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "54": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Downstream Interface 7", "ifType": "128", "ifIndex": "54", "ifMtu": "1764", "ifSpeed": "42884296", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "40939630", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "0", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "1"}, "82": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Upstream Interface 1", "ifType": "129", "ifIndex": "82", "ifMtu": "1764", "ifSpeed": "30720000", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "0", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "2012113", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "2"}, "83": {"portGroup": "", "ipNetToMediaPhysAddress": "", "ifDescr": "RF Upstream Interface 2", "ifType": "129", "ifIndex": "83", "ifMtu": "1764", "ifSpeed": "30720000", "ifPhysAddress": "", "ifAdminStatus": "1", "ifOperStatus": "1", "ifLastChange": "0", "ifInOctets": "0", "ifInUcastPkts": "0", "ifInDiscards": "0", "ifInErrors": "0", "ifInUnknownProtos": "0", "ifOutOctets": "1808910", "ifOutUcastPkts": "0", "ifOutDiscards": "0", "ifOutErrors": "0", "ifConnectorPresent": "1", "ifPromiscuousMode": "2"}}, "chassis": {}}'''

data = json.loads(data)
wc.jd(data)
