
class TestException(Exception):
    """ base class for testing package exceptions """

class  PlayRoundException(TestException):
    """ 
    Raised if something goes wrong in the generation of mock rounds 
    """
