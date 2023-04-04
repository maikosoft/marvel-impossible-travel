class Comic:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.characters = []