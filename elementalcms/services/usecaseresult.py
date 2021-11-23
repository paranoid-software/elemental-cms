class UseCaseResult(object):
    def is_failure(self):
        raise Exception("is_failure method needs to be implemented")

    def value(self):
        raise Exception("is_failure method needs to be implemented")


class Failure(UseCaseResult):
    def __init__(self, v): self.v = v
    def is_failure(self): return True
    def value(self): return self.v


class AccessDenied(Failure):
    def __init__(self):
        super().__init__(None)


class NoResult(Failure):
    def __init__(self):
        super().__init__(None)


class Success(UseCaseResult):
    def __init__(self, v): self.v = v
    def is_failure(self): return False
    def value(self): return self.v
