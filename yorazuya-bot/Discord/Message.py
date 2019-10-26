#self.id
#self.channel_id
#self.author
#self.content
#self.timestamp
#self.edited_timestamp
#
#SOME OTHER STUFF



#ideas

#is command
#sent by object?

from .User import User

class Message:


	def __init__(self,messageArray):
		self.content = messageArray['content']
		#create user object
		self.author = User(messageArray['author'])

	def isValidCommand():
		if message.startswith('!'):
			return True