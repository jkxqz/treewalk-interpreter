class Return(RuntimeError):
    def __init__(self, value: object):
        self.value: object = value