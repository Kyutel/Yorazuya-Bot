import asyncio
import aiohttp
import json
import urllib.parse
import logging
from datetime import datetime
import pprint

from RSSReader import RSSReader
from Config import Config
# from lxml import etree
from DiscordMessage import DiscordMessage

messageLog = None
botClosing = False
hbLog = None
hbid = 0
class YorazuyaBot:

    """Main Bot Program"""
    # self.loop = None

    CHANNEL_ID = 147031379438338048
    NEWS_CHANNEL_ID = 156859545916801024
    URL = 'https://discordapp.com/api'
    RSS_LINK = 'http://euw.leagueoflegends.com/en/rss.xml'
    GUILD_ID = 147031379438338048
    DEV_ROLE = '352546718782586881'

    def __init__(self):
        self.loop = asyncio.get_event_loop()

        #get bot token from config file
        config = Config('config.ini')
        self.token = config.token
        # self.malToken = config.malToken
        self.last_sequence = None

        #get gateway from cache here
        #TODO
        self.ws = None
        self.heartbeatCourotine = None
        self.heartbeatAcked = True
        self.running = True
        self.resuming = False
        self.fresh = False
        self.session_id = None

    async def api_call(self,path, method="GET", **kwargs):
        """Return the JSON body of a call to Discord REST API."""
        defaults = {
            "headers": {
                "Authorization": f"Bot {self.token}",
                "User-Agent": "dBot Patel347"
            }
        }
        kwargs = dict(defaults, **kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.request(method, f"{self.URL}{path}",**kwargs) as response:
                assert 200 == response.status, response.reason
                return await response.json()

    async def heartbeat(self, interval,ida):
        selfid = ida
        """Send every interval ms the heatbeat message."""
        while True:
            # await asyncio.sleep(1)  # seconds
            await asyncio.sleep(interval / 1000)  # seconds
            if self.heartbeatAcked == False:
                print("hb not acked since last sleep")
                messageLog.write("heartbeat was not acked, will attempt to reconnect \n")
                self.loop.stop()
                return -1
            await self.ws.send_json({
                "op": 1,  # Heartbeat
                "d": self.last_sequence
            })
            print("hb sent: " + str(selfid))
            messageLog.write("hb sent")
            self.heartbeatAcked = False
            

    async def sendSingleHB(self):
        await self.ws.send_json({
            "op": 1,  # Heartbeat
            "d": self.last_sequence
        })

    async def getLeagueNews(self):
        while True:
            LeagueNewsReader = RSSReader(self.RSS_LINK)
            latestDateRead = LeagueNewsReader.getDateOfLatestRead()
            newItems = LeagueNewsReader.getNewItems(latestDateRead)
            print('checked for league news')
            if newItems != None:
                for item in newItems:
                     await self.send_message(item.title + ' ' + item.link,self.NEWS_CHANNEL_ID)
                     await asyncio.sleep(1)  # seconds
            await asyncio.sleep(60 * 60)

    async def getGuildMember(self,userId):
        #guilds/{guild.id}/members/{user.id}
        return await self.api_call(f"/guilds/{self.GUILD_ID}/members/{userId}")


    async def send_message(self,content,channelID):
        """Send a message with content to the recipient_id."""
        # channel = await api_call("/users/@me/channels", "POST",json={"recipient_id": recipient_id})
        return await self.api_call(f"/channels/{channelID}/messages", "POST",json={"content": content})

    async def handshake(self):
        await self.ws.send_json(
            {
               "op": 2,  # Identify
               "d": {
                   "token": self.token,
                   "properties": {},
                   "compress": False,
                   "large_threshold": 250
               }
            }
        )
        print('sent handshake')

    # async def searchMal(self,searchTerm,channelID):
    #     defaults = {
    #         "headers": {
    #             "Authorization": f"Basic {self.malToken}",
    #             "User-Agent": "dBot Patel347"
    #         }
    #     }
    #     headers ={"Authorization": f"Basic {self.malToken}","Accept":'text/xml, text/*'}
    #     async with aiohttp.ClientSession() as session:
    #         searchTerm = urllib.parse.quote_plus(searchTerm)
    #         async with session.get('https://myanimelist.net/api/anime/search.xml?q='+searchTerm,headers=headers ) as response:
    #             assert 200 == response.status, response.reason
    #             root = etree.fromstring(await response.read())
    #             # print(etree.tostring(root, pretty_print=True))
    #             # logging.debug(etree.tostring(root))
    #             animeId = root[0][0].text
    #             message = 'Link: <https://myanimelist.net/anime/'+animeId+'>'
    #             message += '\nTitle: '+ root[0][2].text
    #             message += '\nMAL Score: '+ root[0][5].text
    #             message += '\nImage: '+ root[0][11].text
    #             asyncio.ensure_future(self.send_message(message,channelID))


    

    async def parseCommand(self,message,channelID):

        splitMessage = message.split(' ', 1)
        
        command = splitMessage[0][1:]
        #check if command exist in list
        #TODO
        if(len(splitMessage) == 2):
            text = splitMessage[1]
        else:
            text = ''

        # print(self.COMMAND_LIST[command])

        method = self.COMMAND_LIST[command]['method']
        #check permissions here
        #todo
               
        return await method(self,text,channelID)


    async def echo(self,text,channelID):
        task = asyncio.ensure_future(self.send_message(text,channelID))
        await asyncio.wait([task])
        return

    async def stopBot(self,text,channelID):
        task = asyncio.ensure_future(self.send_message('Bye :wave:',channelID))
        print('Bye bye!')
        await asyncio.wait([task])
        print("stopping loop,")
        self.loop.stop()
        return -1

    async def printHelp(self,text,channelID):
        message = "These are the current commands \n"
        for key, value in self.COMMAND_LIST.items():
            message += '**!'+key + (value['params'] if 'params' in value else '')+'**: ' + value['description'] + '\n'
        task = asyncio.ensure_future(self.send_message(message,channelID))
        return

    COMMAND_LIST = {
        'echo':{
            'method':echo,
            'params':'[text]', 
            'description':'this command repeats what was said'
        },
        'quit':{
            'method':stopBot,
            'description':'this command stops the bot'
        },
        'help':{
            'method':printHelp,
            'description': 'displays this message'
        }
    }


    async def messageCreatedEvent(self,messageData):
        '''when functions from another file pythonfunctions from another file pythona message is sent'''
        
        for key, val in messageData.items():
            messageLog.write(str(key) + " - \t "+str(val))
            messageLog.write("\n")
        messageLog.write("\n")

        user = messageData['author']['username']
        messageObj = DiscordMessage(messageData)
        message = messageObj.content
        guildMember = await self.getGuildMember(messageData['author']['id'])
        # print (guildMember['roles'])

        channelID = messageData['channel_id']
        if message.startswith('!'):
            if self.DEV_ROLE not in guildMember['roles']:
                task = asyncio.ensure_future(self.send_message('You dont have permission to do this',channelID))
                return

            return await self.parseCommand(message,channelID)

    async def parseEvent(self,data):
        event = data['t']
        if event == "MESSAGE_CREATE":
            # print(data['d'])
            return await self.messageCreatedEvent(data['d'])
                        

    async def run(self):
        #temp get gateway address
        # if isResuming:
        #     await asyncio.sleep(5)
        global hbid
        response = await self.api_call("/gateway") 
        self.gateway = response['url']

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{self.gateway}?v=6&encoding=json") as ws:
                self.ws = ws
                async for msg in ws:
                    data = json.loads(msg.data)
                    
                    
                    print(data["op"])
                    if self.resuming:
                        print("trying to resume")
                        messageLog.write("attempting a resume\n")
                        print("sessionid " + self.session_id)
                        await self.ws.send_json(
                            {
                               "op": 6,  # resume
                               "d": {
                                   "token": self.token,
                                   "session_id": self.session_id,
                                   "seq":self.last_sequence
                               }
                            }
                        )
                        
                        self.heartbeatCourotine = asyncio.ensure_future(self.heartbeat(data['d']['heartbeat_interval'],hbid))
                        hbid +=1
                        asyncio.ensure_future(self.getLeagueNews()) # start scheduling rgular news retrievals
                        # print("")
                        self.resuming = False
                    elif data["op"] == 10:  # Hello#
                        self.heartbeatCourotine = asyncio.ensure_future(self.heartbeat(data['d']['heartbeat_interval'],hbid))
                        hbid +=1
                        asyncio.ensure_future(self.getLeagueNews()) # start scheduling rgular news retrievals
                        await self.handshake()
                    elif data["op"] == 9:
                            print("error code 9")
                            messageLog.write("session could not be resumed attempting fresh connection")
                            self.fresh = True
                            await asyncio.sleep(5)
                            self.loop.stop()
                            break
                    elif data["op"] == 1:
                        await self.sendSingleHB()
                    elif data["op"] == 11:  # Heartbeat ACK
                        self.heartbeatAcked = True
                        print("heartbeat achnkowleged")
                        messageLog.write("hb acked \n")
                    elif data["op"] == 0:  # Dispatch
                        if data['t'] == 'READY':
                            self.session_id = data['d']['session_id']
                            print(self.session_id)
                        # print(data)
                        self.last_sequence = data['s'] #Update sequence for HB
                        # pass #temp thing to stop bot responding and crashing to responses
                        if(await self.parseEvent(data) == -1):
                            print("bot was closed by command")
                            self.running = False
                            break
                    elif data["op"] >= 4000:
                        print("discord error code " + str(data["op"]))
                        messageLog.write("discord error code: " + str(data["op"]))
                    else:
                        print("something unexpected")
                        print("op code was: " + str(data["op"]))
                        messageLog.write("something unexpected happened")


    def start(self):
        while self.running:
            asyncio.ensure_future(self.run())
            # self.resuming = False
            try:
                self.loop.run_forever()
            finally:
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            if self.running == False:
                print("proper closedown")
                messageLog.write("the bot is closing properly at time:")
                messageLog.write(str(datetime.now()))
            elif self.fresh:
                print("bot ending without ending and not resuming")
                print("attempting fresh connection")
                self.fresh = False
                self.heartbeatAcked = True
            else:
                print("bot ended without ending")
                messageLog.write("bot has ended without ending properly\n")
                messageLog.write("attempting to now resume at ")
                messageLog.write(str(datetime.now()) + "\n")
                self.resuming = True
                self.heartbeatAcked = True
            
        self.loop.close()


def main():
    print('Starting Bot')
    global messageLog
    messageLog = open("message.log","w")
    messageLog.write("messaging log is starting\n")
    bot = YorazuyaBot()
    bot.start()

if __name__ == "__main__":
    main()
