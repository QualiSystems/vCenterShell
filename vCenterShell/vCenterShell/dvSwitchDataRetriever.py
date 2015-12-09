class dvSwitchDataRetriever:

    def Retrieve_dvSwitchData(host, user, pwd, port=443):
        vCenterConnection = SmartConnect(host=host, user=user, pwd=pwd, port=port)
        content = vCenterConnection.RetrieveContent()
        host = content.searchIndex.FindByDnsName(dnsName = vmhost, vmSearch = False)
        result = []
        for vs in host.config.network.vswitch:
            if vs.name == name:
                result.append({
                    "name" : vs.name,
                    "numOfPorts" : vs.numPorts,
                    "numPortsAvailable" : vs.numPortsAvailable,
                    "mtu" : vs.mtu,
                    "key" : vs.key
                })
        return json.dumps(result)


