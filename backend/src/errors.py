from bottle import HTTPError

# base errors
class BadRequest(HTTPError):
    default_status = 400

class Unauthorized(BadRequest):
    default_status = 401


class PaymentRequired(BadRequest):
    default_status = 402


class Forbidden(BadRequest):
    default_status = 403

class NotFound(BadRequest):
    default_status = 404


class MethodNotAllowed(BadRequest):
    default_status = 405


class NotAcceptable(BadRequest):
    default_status = 406


class Conflict(BadRequest):
    default_status = 409


# user specific errors
class UserAlreadyExists(Conflict):
    message = "User already exists"

class UserDoesNotFound(Conflict):
    message = "User does not found"

class UserUnauthorized(Unauthorized):
    message = "incorrect email/password"
