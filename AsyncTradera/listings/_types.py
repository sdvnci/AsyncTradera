from enum import IntEnum
from typing import Literal, Required, TypedDict

from ..common._types import (
    ApiItemTypes,
    ItemAttributeValues,
    ItemShipping,
    Taggable,
)

TransactionFilters = Literal[2, 4]


class TransactionFilter(IntEnum):
    NEW = 2
    NEW_AND_UPDATED = 4


FeedbackTypes = Literal[0, 1]


class FeedbackType(IntEnum):
    POSITIVE = 0
    NEGATIVE = 1


class ItemRequest(TypedDict, total=False):
    """
    Body for ``ListingsPortal.add``.

    ``itemType`` 1 is an auction (add ``buyItNowPrice`` to also offer Buy Now) and
    ``itemType`` 3 is fixed-price "Endast Köp Nu" (fixed 30 day duration). Restricted
    sellers may only list plain auctions ending at least 7 days out.

    With ``autoCommit`` False nothing is published until ``ListingsPortal.commit``;
    use that to add images, or to test without listing anything.
    """

    title: str
    ownReferences: list[str]
    categoryId: int
    duration: int
    restarts: int
    startPrice: int
    reservePrice: int
    buyItNowPrice: int
    description: str
    paymentOptionIds: list[int]
    shippingOptions: list[ItemShipping]
    acceptedBidderId: int
    expoItemIds: list[int]
    customEndDate: str | None
    itemAttributes: list[int]
    itemType: ApiItemTypes
    autoCommit: bool
    vat: int | None
    shippingCondition: str
    paymentCondition: str
    campaignCode: str
    descriptionLanguageCodeIso2: str
    attributeValues: ItemAttributeValues
    restartedFromItemId: int | None


class UpdatedItemInfo(Taggable):
    id: int
    rowVersion: int
    itemType: ApiItemTypes


class RestartItemResult(Taggable):
    """
    ``isSuccessful`` means the restart was queued; the new item appears under
    ``newItemId`` once it is processed.
    """

    isSuccessful: bool
    oldItemId: int
    newItemId: int | None
    validationError: str | None


class ReservedPrice(TypedDict):
    price: int


class BinPrice(TypedDict):
    price: int


class SetPricesNonShopItem(TypedDict, total=False):
    """
    New prices for an auction. Supplying ``binPrice`` adds Buy Now and omitting it
    removes Buy Now, so this can change the item type. To keep the type, use
    ``ListingsPortal.update_price``.
    """

    id: Required[int]
    openingPrice: int
    reservedPrice: ReservedPrice
    binPrice: BinPrice


class SetPricesOnNonShopItemsError(Taggable):
    item: SetPricesNonShopItem
    errorMessage: str | None


class SetPricesOnNonShopItemsResult(Taggable):
    isSuccessful: bool
    validationErrors: list[SetPricesOnNonShopItemsError] | None


class UpdateItemPriceError(Taggable):
    itemId: int
    errorMessage: str | None


class UpdateItemPriceResult(Taggable):
    isSuccessful: bool
    validationErrors: list[UpdateItemPriceError] | None


class ValidateCampaignCodeResult(Taggable):
    isValid: bool
    isInvalidBecauseDoesNotExist: bool
    isInvalidBecauseHasNotStarted: bool
    isInvalidBecauseHasEnded: bool
    isInvalidBecauseCategoryIsNotAllowed: bool
    isInvalidBecauseAlreadyUsed: bool
    isInvalidBecauseUserIsNotAllowed: bool
    description: str | None
    discountFactor: float | None
    provisionFactor: float | None
    maxFeeCap: float | None
    isCustomLengthFeeFree: bool
    isUnsoldFeeFree: bool


__all__ = (
    "TransactionFilters",
    "TransactionFilter",
    "FeedbackTypes",
    "FeedbackType",
    "ItemRequest",
    "UpdatedItemInfo",
    "RestartItemResult",
    "ReservedPrice",
    "BinPrice",
    "SetPricesNonShopItem",
    "SetPricesOnNonShopItemsError",
    "SetPricesOnNonShopItemsResult",
    "UpdateItemPriceError",
    "UpdateItemPriceResult",
    "ValidateCampaignCodeResult",
)
