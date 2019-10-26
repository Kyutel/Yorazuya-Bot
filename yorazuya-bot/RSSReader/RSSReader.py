import feedparser
import time

class RSSReader:
    """Class built upon feedparser to get new items from an rss feed"""
    DATA_FILE = 'RSSData.txt'

    def __init__(self, rssLink):
        self.rssLink = rssLink

    DATA_FILE = 'RSSData.txt'

    def getDateOfLatestRead(self):
        dateOfLatestRead = None

        try:
            dataFile  = open(RSSReader.DATA_FILE,'r')
            dateOfLatestRead = dataFile.readline()
            dataFile.close()
        except FileNotFoundError:
            print("file not found, making file")
            dateOfLatestRead = 'Sat, 05 Aug 2017 19:34:59 +0000' #date this file was created
            dataFile  = open(RSSReader.DATA_FILE,'w+')
            dataFile.write(dateOfLatestRead)
            dataFile.close()

        dateOfLatestRead  = time.strptime(dateOfLatestRead, "%a, %d %b %Y %H:%M:%S %z") 

        return dateOfLatestRead


    def setDateOfLatestRead(self,dateToSet):
        dataFile  = open(RSSReader.DATA_FILE,'w+')
        dataFile.write(dateToSet)
        dataFile.close()


    def getNewItems(self,latestDateRead):
      

        feed = feedparser.parse(self.rssLink)
        newLatestDateReadParsed = feed.entries[0].published_parsed
        newLatestDateRead =  feed.entries[0].published

        newItems= []

        for item in feed.entries:
            #manual parsing because saved date has been manually parsed and has a -1
            #the is_dst value casuing the comparisons to be incorrect.
            item.parsedDate  = time.strptime(item.published, "%a, %d %b %Y %H:%M:%S %z") 
            if latestDateRead < item.parsedDate:
                newItems.insert(0,item)
            if  item.parsedDate> newLatestDateReadParsed:
                newLatestDateRead = item.published
                newLatestDateReadParsed = item.parsedDate

        self.setDateOfLatestRead(newLatestDateRead)
        return newItems

    def printToConsole(self):
        feed = feedparser.parse(RSS_LINK)
        RSS_LINK = 'http://euw.leagueoflegends.com/en/rss.xml'
         
        latestDateRead = getDateOfLatestRead()

        newItems = getNewItems(latestDateRead)
        if newItems != None:
            for item in newItems:
                print(item.title.encode('utf8'))
                print('\n')

        input()
