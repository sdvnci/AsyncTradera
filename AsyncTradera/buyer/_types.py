from enum import IntEnum
from typing import Literal

from ..common._types import Taggable, Transaction, User

BuyStatuses = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class BuyStatus(IntEnum):
    BOUGHT = 0
    ENDED = 1
    NOT_STARTED = 2
    NOT_ALLOWED = 3
    PURCHASE_OWN_ITEM = 4
    REGION_NOT_ACCEPTED = 5
    UNEXPECTED_ERROR = 6
    BUY_IT_NOW_NO_LONGER_AVAILABLE = 7
    PRICE_CHANGED = 8
    ITEM_NOT_FOUND = 9
    NUMBER_OF_BUYS_LIMIT_REACHED = 10
    BUY_NOT_AVAILABLE_ON_ITEM = 11


class BuyResult(Taggable):
    nextBid: int
    status: BuyStatuses


class BuyerTransaction(Transaction):
    seller: User
    isMarkedAsPaid: bool


__all__ = ("BuyStatuses", "BuyStatus", "BuyResult", "BuyerTransaction")
