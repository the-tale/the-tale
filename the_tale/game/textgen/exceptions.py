# coding: utf-8

class TextgenException(Exception): 

    def __str__(self): 
        return (u'%s' % (self.args[0],)).encode('utf-8')

