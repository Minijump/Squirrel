import json


class FileManager:
    async def load_file_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
    async def write_file_json(file_path, file_content):
        with open(file_path, 'w') as file:
            json.dump(file_content, file, indent=4)

    async def update_file_json(file_path, update_method):
        data = await FileManager.load_file_json(file_path)
        await update_method(data)
        await FileManager.write_file_json(file_path, data)

class FileObject():
    def __init__(self, manifest_path=None):
        self.manifest_path = manifest_path

    async def load_manifest(self):
        return await FileManager.load_file_json(self.manifest_path)
    
    async def write_manifest(self, manifest_content):
        await FileManager.write_file_json(self.manifest_path, manifest_content)

    async def update_manifest(self, update_method):
        await FileManager.update_file_json(self.manifest_path, update_method)