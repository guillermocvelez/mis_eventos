class MisEventosException(Exception):
    """Base de todas las excepciones del dominio."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EventNotFound(MisEventosException):
    def __init__(self, event_id=None):
        msg = f"Evento {event_id} no encontrado." if event_id else "Evento no encontrado."
        super().__init__(msg)


class CapacityExceeded(MisEventosException):
    def __init__(self, message: str = "El evento no tiene cupos disponibles."):
        super().__init__(message)


class AlreadyRegistered(MisEventosException):
    def __init__(self, message: str = "El usuario ya está registrado en este evento."):
        super().__init__(message)


class SessionOverlap(MisEventosException):
    def __init__(self, message = "El horario se solapa con una sesión existente."):
        super().__init__(message)


class Unauthorized(MisEventosException):
    def __init__(self):
        super().__init__("No tienes permiso para realizar esta acción.")


class InvalidEventDate(MisEventosException):
    def __init__(self, message: str = "La fecha del evento debe ser futura."):
        super().__init__(message)

class SessionOutOfRange(MisEventosException):
    def __init__(self, message: str = "La sesión está fuera del rango de fechas del evento."):
        super().__init__(message)

class RegistrationNotFound(MisEventosException):
    def __init__(self, message: str = "El usuario no esta registrado a esta sesión"):
        super().__init__(message)

class EventNotOpenForRegistration(MisEventosException):
    def __init__(self, message: str = "No puedes registrarte a un evento en borrador"):
        super().__init__(message)

class UserNotFound(MisEventosException):
    def __init__(self, message: str = "Usuario no encontrado"):
            super().__init__(message)

class EmailAlreadyExists(MisEventosException):
    def __init__(self, message: str = "El usuario ya se encuentra registrado"):
                super().__init__(message)

class CannotDeleteSelf(MisEventosException):
    def __init__(self, message: str = "El usuario no se puede borrar"):
        super().__init__(message)