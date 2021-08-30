########################
## SOME CUSTOM ERRORS ##
########################


class MyBaseException(Exception):
    def __init__(self, msg=None):
        self.message = msg
        super().__init__(self.message)


class HunterError(MyBaseException):
    pass


class AutoBotError(MyBaseException):
    pass


class UserLoginError(MyBaseException):
    pass


class MakePostError(MyBaseException):
    pass

##########################
######### END ############
##########################