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

class UserUnauthorized(Unauthorized):
    message = "incorrect email/password"


# camera specific errors
class CameraAlreadyExists(Conflict):
    message = "Camera already exists"

class CameraNotFound(NotFound):
    message = "Camera not found"

class CameraShouldBeStopped(Conflict):
    message = "For this operation camera should be stopped"

# preset specific errors
class PresetAlreadyExists(Conflict):
    message = "Preset already exist"

class PresetDoesntExist(Conflict):
    message = "Preset doesn't exist"

class PresetIncorrectFormat(Conflict):
    message = "Incorrect format"
