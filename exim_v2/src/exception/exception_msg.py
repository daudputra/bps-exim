class CantLoadWebPage(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg        
    def __str__(self) -> str:
        return self.msg


class FailedInputCategory(Exception):
    def __init__(self, msg) -> str:
        super().__init__(msg)
        self.msg = msg
    def __str__(self) -> str:
        return self.msg


class CantFoundOption(Exception):
    def __str__(self) -> str:
        return "Cant found option, try again!"
    
class CantDownloadFiles(Exception):
    def __str__(self) -> str:
        return "Cant Download Files!"