
class Gateway:

    apiVersion = '6'

    def __init__(self,token,session_id = None):
        self.token = token
        self.resuming = False
        # self.getGatewayUrl()


    async def getGatewayUrl(self):
        response = await self.api_call("/gateway") 
        self.gatewayURL = response.getField('url')

    async def connect(self):
        #TODO check to see if gateway url is allready been grabbed first
        self.getGatewayUrl()

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{self.gatewayURL}?v={self.apiVersion}&encoding=json") as webSocket:
                self.webSocket = webSocket
                self.handleConnection()




    async def handleConnection(self):
        async for message in self.webSocket:
            
            recievedPayload = getPayloadFromMessage(message)
            if self.resuming:
                self.handleResuming()




    async def handleResuming(self):
        await self.resumeConnectionToGateway()
        # self.heartbeatCourotine = asyncio.ensure_future(self.heartbeat(data['d']['heartbeat_interval'],hbid))
        # asyncio.ensure_future(self.getLeagueNews())
        self.resuming = False


    def getPayloadFromMessage(self):
        messageData = json.loads(message.data)
        print(messageData)


    async def sendToGateway(payload):
        await self.webSocket.send_json(payload.get())


    async def resumeConnectionToGateway(self):

        payload = PayloadFactory.resumePayload(self.token,self.session_id,self.last_sequence)

        await sendToGateway(payload)

class Payload:
    def __init__(self,opCode,data):
        self.opCode = opCode
        self.data = data

    def setOpCode(self,opCode):
        self.opCode = opCode
    def setData(self,data):
        self.data = data
    def setToken(self,token):
        self.token = token
    def get():
        return {
            "op": self.opCode,
            "d": self.data
        }

class PayloadFactory:

    def resumePayload(token,session_id,last_sequence):
        opCode = 6
        data =  {
                   "token": token,
                   "session_id": session_id,
                   "seq":last_sequence
                }
        return Payload(opCode,data).get()