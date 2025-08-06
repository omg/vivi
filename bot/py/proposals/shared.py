from enum import Enum

class ProposalType(Enum):
    ADDITION = 1
    REMOVAL  = 2
    EDIT     = 3
    FORK     = 4
