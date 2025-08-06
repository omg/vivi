class ProposalBotError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return self.__class__.__name__ + ": " + self.message

####### PROPOSAL ERRORS #######


class ProposalValidationError(ProposalBotError):
    def __init__(self, message):
        super().__init__(message)

class ProposalParsingError(ProposalBotError):
    def __init__(self, message):
        super().__init__(message)


####### COMMAND RELATED ERRORS #######


class GeneralCommandError(ProposalBotError):
    def __init__(self, message):
        super().__init__(message)