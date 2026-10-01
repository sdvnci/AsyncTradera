from ..common._types import Taggable


class Token(Taggable):
    """
    A user token. Store it like a password and watch ``hardExpirationTime``.
    """

    authToken: str | None
    hardExpirationTime: str


class BeginBankIdVerificationResult(Taggable):
    bankIdOrderRef: str | None
    error: str | None
    qrData: str | None
    autoStartToken: str | None


class BeginBankIdOnFileVerificationResult(Taggable):
    bankIdOrderRef: str | None
    error: str | None
    autoStartToken: str | None


class GetBankIdVerificationProgressResult(Taggable):
    isCompleted: bool
    progress: str | None
    error: str | None
    qrData: str | None


__all__ = (
    "Token",
    "BeginBankIdVerificationResult",
    "BeginBankIdOnFileVerificationResult",
    "GetBankIdVerificationProgressResult",
)
