class Character:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.picture = data['thumbnail']['path'] + '.' + data['thumbnail']['extension']
        self.comics = []
        self.related_characters = []

