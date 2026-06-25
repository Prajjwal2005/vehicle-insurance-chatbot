"""Domain-level service errors, mapped to HTTP status codes by the routers."""


class ServiceError(Exception):
    """Base class for service-layer errors."""


class NotFoundError(ServiceError):
    """A requested entity does not exist (-> HTTP 404)."""


class ConflictError(ServiceError):
    """The operation is not valid for the entity's current state (-> HTTP 409)."""
