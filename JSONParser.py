import json

# For now just retrieve a mapping of set to chrome sheet ID
class JSONParser:
    def GetPages(filepath):

        with open(filepath, 'r') as file:
            file_contents = file.read()

        pages = json.loads(file_contents)  

        return pages

    