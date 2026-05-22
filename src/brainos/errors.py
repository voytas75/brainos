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


class VectorIndexContractError(BrainOSError):
    pass
