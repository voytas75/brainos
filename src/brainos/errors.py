class BrainOSError(Exception):
    pass


class ValidationError(BrainOSError):
    pass


class PromotionError(BrainOSError):
    pass


class NotFoundError(BrainOSError):
    pass


class EmbeddingProviderNotConfiguredError(BrainOSError):
    pass


class EmbeddingRuntimeError(BrainOSError):
    pass


class VectorIndexContractError(BrainOSError):
    pass


class SqliteVecReadinessError(BrainOSError):
    def __init__(self, message: str, *, error_kind: str, detail: str | None = None):
        super().__init__(message)
        self.error_kind = error_kind
        self.detail = detail or message
