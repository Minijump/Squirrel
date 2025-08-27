class MockUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content.encode() if isinstance(content, str) else content
        self.size = len(self.content)
    
    async def read(self):
        return self.content
