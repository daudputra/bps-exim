class CantLoadWebPage(Exception):
    def __str__(self) -> str:
        return "Cant load web page"


class FailedInputCategory(Exception):
    def __init__(self, msg) -> str:
        super().__init__(msg)
        self.msg = msg
    def __str__(self) -> str:
        return self.msg