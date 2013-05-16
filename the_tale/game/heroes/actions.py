# coding: utf-8


class Action(object):

    __slots__ = ('_container', '_percents', 'description', 'info_link')

    def __init__(self, percents, description, info_link=None):
        self._container = None
        self._percents = percents
        self.description = description
        self.info_link = info_link

    def get_percents(self): return self._percents
    def set_percents(self, value):
        self._container.updated = True
        self._percents = value
    percents = property(get_percents, set_percents)

    def serialize(self):
        return {'percents': self.percents,
                'description': self.description,
                'info_link': self.info_link}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def ui_info(self):
        return {'percents': self.percents,
                'description': self.description,
                'info_link': self.info_link}


class ActionsContainer(object):

    __slots__ = ('updated', '_actions')

    def __init__(self):
        self.updated = False
        self._actions = []

    def serialize(self):
        return {'actions': [action.serialize() for action in self._actions]}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj._actions = [Action.deserialize(action_data) for action_data in data.get('actions', [])]
        for action in obj._actions:
            action._container = obj
        return obj

    def ui_info(self):
        return {'actions': [action.ui_info() for action in self._actions]}

    def push_action(self, action):
        self.updated = True
        action._container = self
        self._actions.append(action)

    def pop_action(self):
        self.updated = True
        action = self._actions.pop()
        action._container = None
        return action

    @property
    def current_action(self): return self._actions[-1]
