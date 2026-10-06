class UserNotFoundException(Exception):
    pass

class UserAlreadyExistsException(Exception):
    pass

class InvalidPasswordException(Exception):
    pass

class SamePasswordException(Exception):
    pass