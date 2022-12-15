import aiohttp


class Client:
    def __init__(self, auth_token):
        self.TOKEN = auth_token
        self.CLIENT = aiohttp.ClientSession

    async def request(self, url, query):
        header = {
            'Authorization': f'bearer {self.TOKEN}'
        }

        async with self.CLIENT() as session:
            async with session.post(
                    url,
                    headers=header,
                    json={'query': query}) as response:
                return await response.json()
