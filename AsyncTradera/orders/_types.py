from enum import IntEnum
from typing import Literal

from ..common._types import ApiItemTypes, Taggable

SellerOrderQueryDateModes = Literal[0, 1]


class SellerOrderQueryDateMode(IntEnum):
    """
    Which date ``OrdersPortal.where`` filters on. Poll with ``LAST_UPDATED_DATE`` to
    pick up orders that changed since the last run.
    """

    CREATED_DATE = 0
    LAST_UPDATED_DATE = 1


class SellerOrderUser(Taggable):
    userId: int
    firstName: str | None
    lastName: str | None
    addressLine1: str | None
    addressLine2: str | None
    zipCode: str | None
    city: str | None
    countryName: str | None
    email: str | None
    phone: str | None
    alias: str | None


class SellerOrderAddress(Taggable):
    name: str | None
    addressLine1: str | None
    addressLine2: str | None
    zipCode: str | None
    city: str | None
    countryName: str | None


class SellerOrderItem(Taggable):
    itemId: int
    type: ApiItemTypes
    title: str | None
    quantity: int
    unitPrice: int
    vatRate: int
    ownReferences: list[str] | None
    merchantPartNumber: str | None


class SellerOrderKeyValuePair(Taggable):
    key: str | None
    value: str | None


class SellerOrderPayment(Taggable):
    paymentType: str | None
    reference: str | None
    additionalInfo: list[SellerOrderKeyValuePair] | None
    amount: int
    paidDate: str
    paymentCost: int


class SellerOrder(Taggable):
    orderId: int
    createdDate: str
    expiresDate: str | None
    lastUpdatedDate: str
    subTotal: int
    seller: SellerOrderUser
    buyer: SellerOrderUser
    shipTo: SellerOrderAddress
    items: list[SellerOrderItem] | None
    sellerOrderPayments: list[SellerOrderPayment] | None
    shippingType: str | None
    shippingCost: int
    shippingWeight: float | None
    purchaseOrderId: str


class SetSellerOrderAsShippedResponse(Taggable):
    orderId: int


class FreightLabel(Taggable):
    orderId: int
    freightLabelContent: str | None


class ShippingCode(Taggable):
    """
    How to hand over a shipment that has no printable label (e.g. Instabox):
    write ``labellessShippingCode`` on the parcel and show ``qrCodeImageUrl`` at drop-off.
    """

    orderId: int
    shippingProvider: str | None
    labellessShippingCode: str | None
    qrCodeImageUrl: str | None
    shipmentNo: str | None
    hasFreightLabel: bool


__all__ = (
    "SellerOrderQueryDateModes",
    "SellerOrderQueryDateMode",
    "SellerOrderUser",
    "SellerOrderAddress",
    "SellerOrderItem",
    "SellerOrderKeyValuePair",
    "SellerOrderPayment",
    "SellerOrder",
    "SetSellerOrderAsShippedResponse",
    "FreightLabel",
    "ShippingCode",
)
