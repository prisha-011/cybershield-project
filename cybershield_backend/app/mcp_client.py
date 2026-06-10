class MCPClient:
    def __init__(self):
        self.connected = False

    async def connect(self):
        self.connected = True
        return True

    async def close(self):
        self.connected = False
        return True


mcp_client = MCPClient()