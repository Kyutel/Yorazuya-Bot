
class Gateway:

    apiVersion = '6'

    def __init__(self,token,session_id = None):
        self.token = token
        # self.getGatewayUrl()


    async def getGatewayUrl(self):
        response = await self.api_call("/gateway") 
        self.gatewayURL = response.getField('url')

    async def connect():
        #TODO check to see if gateway url is allready been grabbed first
        self.getGatewayUrl()

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{self.gatewayURL}?v={self.apiVersion}&encoding=json") as webSocket:
                self.webSocket = webSocket
                self.handleConnection()

    async def handleConnection():
        async for message in self.webSocket:
            messageData = json.loads(message.data)

            if self.resuming:
                self.handleResuming()
                self.heartbeatCourotine = asyncio.ensure_future(self.heartbeat(data['d']['heartbeat_interval'],hbid))
                asyncio.ensure_future(self.getLeagueNews())
                self.resuming = False
            elif


    async def resumeConnectionToGateway():

        opCode = 6
        data =  {
                   "token": self.token,
                   "session_id": self.session_id,
                   "seq":self.last_sequence
                }

        payload = Payload(opCode,data)


        await self.webSocket.send_json(
            payload.get()
        )


class Payload:
    def __init__(self,opCode,data):
        self.opCode = opCode
        self.data = data

    def setOpCode(opCode):
        self.opCode = opCode
    def setData():
    def setToken():
    def get():
        return {
            "op": self.opCode,
            "d": self.data
        }