import json


class Character:
    def __init__(self, name, patrol, events, like=0):
        self._name = name
        self._patrol = patrol
        self._events = events
        self._like = like
        self._tired = 100

    @property
    def name(self):
        return self._name

    @property
    def patrol(self):
        return self._patrol

    @property
    def like(self):
        return self._like

    @property
    def tired(self):
        return self._tired

    @property
    def events(self):
        return self._events

    def __repr__(self):
        return u'<신기사: {}>'.format(self._name)

    def __str__(self):
        return u'<신기사: {}>'.format(self._name)


def load_characters():
    # read data file
    with open('characters.json') as f:
        data = json.load(f)
    character_dict = dict()
    for char_data in data:
        character_dict[char_data['name']] = Character(char_data['name'], char_data['patrol'], char_data['events'])
    return character_dict
