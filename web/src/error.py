class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def check_crawling_correct(value):
    if value == 0:
        raise CustomError("you didn't crawl anything you want!!")

