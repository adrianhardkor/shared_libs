class pingSession:

    def __init__(self):
        pass

    def getPorts(self):
        # determine if the system is reachable via ICMP echo request
        if os.name == 'posix':
            ping = subprocess.call(["ping", "-c", "1", ipAddress], stdout=subprocess.PIPE)
        else:
            ping = subprocess.call(["ping", "-n", "1", ipAddress], stdout=subprocess.PIPE)

        if ping == 0:
            returnDictionary = {"ports": []}
        else:
            sys.exit("unreachable")

        return returnDictionary


    def getProperties(self, args):
        # create resource properties dictionary
        resourceProperties = {}

        # create properties dictionary
        returnDictionary = { "properties" : resourceProperties }

        # include ports in response if argument is true
        if args[0] == 'true':
            portList = self.getPorts()
            if portList.has_key('ports'):
                returnDictionary['ports'] = portList['ports']
            else:
                returnDictionary = { "status" : "unreachable"}

        return returnDictionary
