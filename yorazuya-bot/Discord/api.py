class Api:
    token = None
    URL = 'https://discordapp.com/api'

    async def api_call(path, method="GET", **kwargs):
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
                    return ApiResponse(await response.json())


class ApiResponse:

    def __init__(self, aiohttpResponse):
        self.rawResponse = aiohttpResponse