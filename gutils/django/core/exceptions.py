class JsonNotFound(Exception):

    def __init__(self):

        Exception.__init__(self, 'Record not found')
