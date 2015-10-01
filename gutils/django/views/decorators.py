def servicemethod(func):
    def service(self):
        return func(self)
    service.servicemethod = True
    return service