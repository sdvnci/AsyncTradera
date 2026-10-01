from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Literal, NotRequired, Sequence, TypedDict

DateLike = datetime | date | str
QueryScalar = str | int | float | bool | datetime | date | None
QueryValue = QueryScalar | Sequence[QueryScalar]
AuthLevels = Literal["app", "user"]


class Taggable(TypedDict, total=False):
    __kind__: NotRequired[str]


class Endpoints(Enum):
    AUTH = "auth"
    BUYER = "buyer"
    CATEGORIES = "categories"
    ITEMS = "items"
    LISTINGS = "listings"
    ORDERS = "orders"
    REFERENCE_DATA = "reference-data"
    SEARCH = "search"
    USERS = "users"


TraderaStatusStates = Literal[
    "BadRequest",
    "Unauthorized",
    "Forbidden",
    "NotFound",
    "TooManyRequests",
    "InternalServerError",
]


class TraderaStatusCode(IntEnum):
    BADREQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOTFOUND = 404
    TOOMANYREQUESTS = 429
    INTERNALSERVERERROR = 500

    def string(self: "TraderaStatusCode") -> TraderaStatusStates:
        match self:
            case TraderaStatusCode.BADREQUEST:
                return "BadRequest"
            case TraderaStatusCode.UNAUTHORIZED:
                return "Unauthorized"
            case TraderaStatusCode.FORBIDDEN:
                return "Forbidden"
            case TraderaStatusCode.NOTFOUND:
                return "NotFound"
            case TraderaStatusCode.TOOMANYREQUESTS:
                return "TooManyRequests"
            case TraderaStatusCode.INTERNALSERVERERROR:
                return "InternalServerError"

    @classmethod
    def label(cls: type["TraderaStatusCode"], status: int) -> str:
        """
        The Tradera error code string for an HTTP status, or the bare number for
        statuses Tradera does not document.
        """
        try:
            return cls(status).string()
        except ValueError:
            return str(status)


class TraderaError(TypedDict):
    code: str
    message: str


class TraderaErrorResponse(Taggable):
    """
    The error body Tradera returns for every non-2xx response. Locally generated
    errors (missing user auth, transport failures, undecodable bodies) use the same shape.
    """

    error: TraderaError


ActiveFilters = Literal[0, 1, 2]


class ActiveFilter(IntEnum):
    ALL = 0
    ACTIVE = 1
    INACTIVE = 2


ApiItemTypes = Literal[1, 3, 4, 5]


class ApiItemType(IntEnum):
    AUCTION = 1
    PURE_BUY_IT_NOW = 3
    SHOP_ITEM = 4
    CONTACT_ONLY = 5


ItemTypeFilters = Literal[0, 1, 2, 3]


class ItemTypeFilter(IntEnum):
    ALL = 0
    AUCTION = 1
    PURE_BUY_IT_NOW = 2
    SHOP_ITEM = 3


ImageFormats = Literal[0, 1, 2]


class ImageFormat(IntEnum):
    GIF = 0
    JPEG = 1
    PNG = 2


ResultCodes = Literal[1, 2, 4, 8, 16, 32, 64, 128, 256]


class ResultCode(IntEnum):
    OK = 1
    IMAGE_PROCESSING_ERROR = 2
    ERROR = 4
    TIMEOUT = 8
    TRY_AGAIN = 16
    UPDATE_NOT_ALLOWED = 32
    REACHED_MAXIMUM_ACTIVE_ITEMS_THRESHOLD = 64
    WAITING_TO_BE_PROCESSED = 128
    UNCOMMITED = 256


class IdDescriptionPair(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    id: int
    description: str | None
    value: str | None


class User(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    id: int
    alias: str | None
    firstName: str | None
    lastName: str | None
    email: str | None
    totalRating: int | None
    phoneNumber: str | None
    mobilePhoneNumber: str | None
    address: str | None
    zipCode: str | None
    city: str | None
    countryName: str | None
    personalNumber: str | None
    transactionId: int | None


class ItemStatus(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    ended: bool
    gotBidders: bool
    gotWinner: bool


class ImageLink(Taggable):
    url: str | None
    format: str | None


class TermAttributeValue(Taggable):
    id: int
    name: str | None
    values: list[str] | None


class NumberAttributeValue(Taggable):
    id: int
    name: str | None
    values: list[float] | None


class AttributeValues(Taggable):
    termAttributeValues: list[TermAttributeValue] | None
    numberAttributeValues: list[NumberAttributeValue] | None


class TermValues(TypedDict):
    """
    A chosen value for a category attribute, e.g. ``{"id": skick_id, "values": ["Mycket gott skick"]}``.
    """

    id: int
    values: list[str]


class NumberValues(TypedDict):
    id: int
    values: list[float]


class ItemAttributeValues(TypedDict, total=False):
    terms: list[TermValues]
    numbers: list[NumberValues]


class ItemShipping(Taggable, total=False):
    """
    A shipping option on an item. Set exactly one of ``shippingProviderId`` or the
    obsolete ``shippingOptionId``; valid ids come from ``ReferenceDataPortal.shipping_options``.
    """

    shippingOptionId: int | None
    cost: int
    shippingWeight: float | None
    shippingWeightSpecified: bool
    shippingProductId: int | None
    shippingProductIdSpecified: bool
    shippingProviderId: int | None
    sellerSurcharge: int | None
    sellerSurchargeSpecified: bool
    sellerDiscount: int | None
    sellerDiscountSpecified: bool


class ItemImageData(TypedDict, total=False):
    """
    An image attached to a shop item. ``data`` is the base64-encoded image (max 4MB).
    """

    hasMega: bool
    format: ImageFormats
    data: str
    name: str


class Item(Taggable):
    shippingOptions: list[ItemShipping] | None
    paymentOptions: list[int] | None
    imageLinks: list[str] | None
    buyerList: list[User] | None
    status: ItemStatus
    startQuantity: int
    remainingQuantity: int
    itemType: ApiItemTypes
    detailedImageLinks: list[ImageLink] | None
    id: int
    vat: int
    vatSpecified: bool
    shortDescription: str | None
    ownReferences: list[str] | None
    attributeValues: AttributeValues
    itemAttributes: list[int] | None
    longDescription: str | None
    startDate: str
    endDate: str
    categoryId: int
    openingBid: int
    openingBidSpecified: bool
    reservePrice: int
    reservePriceSpecified: bool
    reservePriceReached: bool | None
    buyItNowPrice: int
    buyItNowPriceSpecified: bool
    nextBid: int
    nextBidSpecified: bool
    paymentCondition: str | None
    shippingCondition: str | None
    acceptsPickup: bool
    totalBids: int
    maxBid: int
    maxBidSpecified: bool
    statusId: int
    bold: bool
    thumbnail: bool
    highlight: bool
    featuredItem: bool
    itemLink: str | None
    thumbnailLink: str | None
    acceptedBuyerId: int
    paypal: bool
    paymentTypeId: int
    seller: User
    maxBidder: User
    userSelectedEndDate: bool
    restarts: int
    duration: int
    reservePriceManuallySet: bool


class TransactionItem(Taggable):
    id: int
    type: ApiItemTypes
    title: str | None
    ownReferences: list[str] | None


class Transaction(Taggable):
    id: int
    date: str
    amount: int
    lastUpdatedDate: str
    isMarkedAsPaidConfirmed: bool
    isMarkedAsShipped: bool
    isShippingBooked: bool
    isFeedbackLeftBySeller: bool
    isFeedbackLeftByBuyer: bool
    buyer: User
    item: TransactionItem


class QueuedRequestResponse(Taggable):
    """
    Listing writes are queued. Poll ``ListingsPortal.request_results`` with ``requestId``
    to learn whether the request was applied.
    """

    requestId: int
    itemId: int


class RequestResult(Taggable):
    requestId: int
    resultCode: ResultCodes
    message: str | None


__all__ = (
    "DateLike",
    "QueryScalar",
    "QueryValue",
    "AuthLevels",
    "Taggable",
    "Endpoints",
    "TraderaStatusStates",
    "TraderaStatusCode",
    "TraderaError",
    "TraderaErrorResponse",
    "ActiveFilters",
    "ActiveFilter",
    "ApiItemTypes",
    "ApiItemType",
    "ItemTypeFilters",
    "ItemTypeFilter",
    "ImageFormats",
    "ImageFormat",
    "ResultCodes",
    "ResultCode",
    "IdDescriptionPair",
    "User",
    "ItemStatus",
    "ImageLink",
    "TermAttributeValue",
    "NumberAttributeValue",
    "AttributeValues",
    "TermValues",
    "NumberValues",
    "ItemAttributeValues",
    "ItemShipping",
    "ItemImageData",
    "Item",
    "TransactionItem",
    "Transaction",
    "QueuedRequestResponse",
    "RequestResult",
)
