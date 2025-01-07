class RollException(BaseException):
    def __init__(self, information):
        super().__init__()
        self.information = information

class RollplayerLibraryException(Exception):
    pass

class SplitFailException(RollplayerLibraryException):
    pass

class BonusParseException(RollplayerLibraryException):
    pass