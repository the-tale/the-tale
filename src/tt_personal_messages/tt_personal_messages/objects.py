

class Message(object):
    __slots__ = ('id', 'sender', 'recipients', 'created_at', 'body')

    def __init__(self, id, sender, recipients, created_at, body):
        self.id = id
        self.sender = sender
        self.recipients = recipients
        self.created_at = created_at
        self.body = body


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.sender == other.sender and
                self.recipients == other.recipients and
                self.created_at == other.created_at and
                self.body == other.body)


    def __ne__(self, other):
        return not self.__eq__(other)
