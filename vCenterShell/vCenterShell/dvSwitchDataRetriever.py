class dvSwitchDataRetriever:

    def Retrieve_dvSwitchData(host, user, pwd, port=443):
        vCenterConnection = SmartConnect(host=host, user=user,pwd=pwd,port=port)
        content = vCenterConnection.RetrieveContent()


