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
    def __init__(self):
        super().__init__("El evento no tiene cupos disponibles.")


class AlreadyRegistered(MisEventosException):
    def __init__(self):
        super().__init__("El usuario ya está registrado en este evento.")


class SessionOverlap(MisEventosException):
    def __init__(self):
        super().__init__("El horario se solapa con una sesión existente.")


class Unauthorized(MisEventosException):
    def __init__(self):
        super().__init__("No tienes permiso para realizar esta acción.")


class InvalidEventDate(MisEventosException):
    def __init__(self):
        super().__init__("La fecha del evento debe ser futura.")