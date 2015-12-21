import ConfigParser, os


class TestCredentials:

    def __init__(self):
        config = ConfigParser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.readfp(open(config_path))
        self.host = config.get('Credentials', 'host')
        self.username = config.get('Credentials', 'username')
        self.password = config.get('Credentials', 'password')
        self.port = config.get('Credentials', 'port')
