import configparser

class Config:
    def __init__(self, config_file):
        # self.config_file = config_file
        self.config = configparser.ConfigParser()

        # self.config = config.read(config_file)

        # self.token = config.get('Credentials', 'Token', fallback='')
        # self.malToken = config.get('Credentials', 'MAL_Token',fallback='')
        # self.newsChannelID  = config.get('ChannelIds', 'News_Channel',fallback='')

        # self.APITokens  = self.getAPITokens()

    # def getAPITokens(self):
    	# configHeader = 'Credentials'
    	# APITokens = []
    	# APITokens += config.get('Credentials', 'Token', fallback='')
    	# APITokens += config.get()

    def getBotToken(self):
        return self.config.get('Credentials', 'Token', fallback = '')
        