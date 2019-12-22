
class Logger:
	def __init__(self, filepath):
		self.logFile = open(filepath,'w')

	def write(self,string):
		self.logFile.write(string)

	def writeLine(self,string):
		self.logFile.write(string + "\n")