from typing import TypedDict

from ..common._types import (
    ImageFormats,
    ItemAttributeValues,
    ItemImageData,
    ItemShipping,
    QueuedRequestResponse,
    Taggable,
)


class ShopItemData(TypedDict, total=False):
    """
    Body for adding or updating a shop item.

    ``quantity`` is a delta added to the current stock; ``absoluteQuantity`` sets it
    outright. Supply at most one. Text limits: title 80, description 7000,
    conditions 500, each own reference 60 characters. At most 40 images of 4MB.
    """

    activateDate: str | None
    acceptedBuyerId: int | None
    categoryId: int | None
    deactivateDate: str | None
    itemAttributes: list[int]
    description: str
    paymentCondition: str
    price: int | None
    quantity: int | None
    absoluteQuantity: int | None
    shippingCondition: str
    title: str
    vat: int | None
    shippingOptions: list[ItemShipping]
    paymentOptionIds: list[int]
    ownReferences: list[str]
    itemImages: list[ItemImageData]
    externalId: int | None
    attributeValues: ItemAttributeValues
    descriptionLanguageCodeIso2: str


class VariantAttribute(TypedDict):
    name: str
    value: str


class VariantData(TypedDict, total=False):
    variantGroupId: str
    variantAttributes: list[VariantAttribute]


class ShopItemVariantData(ShopItemData, total=False):
    """
    A shop item that is one variant of a group, e.g. one size of a shirt.
    ``sellerPartNo`` is required by Tradera.
    """

    sellerPartNo: str
    variantData: VariantData


class SetPriceShopItem(TypedDict):
    id: int
    price: int


class SetPriceOnShopItemsError(Taggable):
    item: SetPriceShopItem
    errorMessage: str | None


class SetPriceOnShopItemsResult(Taggable):
    queuedRequestResponses: list[QueuedRequestResponse] | None
    validationErrors: list[SetPriceOnShopItemsError] | None


class SetQuantityShopItem(TypedDict):
    id: int
    quantity: int


class SetQuantityOnShopItemError(Taggable):
    item: SetQuantityShopItem
    errorMessage: str | None


class SetQuantityOnShopItemsResult(Taggable):
    successfulUpdates: int
    validationErrors: list[SetQuantityOnShopItemError] | None


class SetActivateDateShopItem(TypedDict):
    id: int
    activateDate: str


class SetActivateDateOnShopItemsError(Taggable):
    item: SetActivateDateShopItem
    errorMessage: str | None


class SetActivateDateOnShopItemsResult(Taggable):
    queuedRequestResponses: list[QueuedRequestResponse] | None
    validationErrors: list[SetActivateDateOnShopItemsError] | None


class ShopLogoData(TypedDict, total=False):
    imageFormat: ImageFormats
    imageData: str | None
    removeLogo: bool | None


class ShopSettingsData(Taggable, total=False):
    companyInformation: str | None
    purchaseTerms: str | None
    showGalleryMode: bool | None
    showAuctionView: bool | None
    logoInformation: ShopLogoData
    bannerColor: str | None
    isTemporaryClosed: bool | None
    temporaryClosedMessage: str | None
    contactInformation: str | None
    logoImageUrl: str | None
    maxActiveItems: int
    maxInventoryItems: int


__all__ = (
    "ShopItemData",
    "VariantAttribute",
    "VariantData",
    "ShopItemVariantData",
    "SetPriceShopItem",
    "SetPriceOnShopItemsError",
    "SetPriceOnShopItemsResult",
    "SetQuantityShopItem",
    "SetQuantityOnShopItemError",
    "SetQuantityOnShopItemsResult",
    "SetActivateDateShopItem",
    "SetActivateDateOnShopItemsError",
    "SetActivateDateOnShopItemsResult",
    "ShopLogoData",
    "ShopSettingsData",
)
