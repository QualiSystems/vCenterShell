import ConfigParser, os

class testCredentials:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open('config.ini'))
        self.host = config.get('Credentials', 'host')
        self.username = config.get('Credentials', 'username')
        self.password = config.get('Credentials', 'password')
