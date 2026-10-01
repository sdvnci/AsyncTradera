from typing import Literal, TypedDict

from ..common._types import AttributeValues, ImageLink, Taggable

SearchOrderBys = Literal[
    "Relevance",
    "BidsAscending",
    "BidsDescending",
    "PriceAscending",
    "PriceDescending",
    "EndDateAscending",
    "EndDateDescending",
]
SearchModes = Literal["AllWords", "AnyWords"]
SearchItemStatuses = Literal["Active", "Ended"]
SearchItemTypes = Literal["All", "Auction", "FixedPrice"]
SearchItemConditions = Literal["All", "OnlyNew", "OnlySecondHand"]
SearchSellerTypes = Literal["All", "OnlyPrivate", "OnlyBusiness"]


class SearchError(Taggable, total=False):
    """
    A per-search validation error, e.g. ``OrderByValidationError``. Searches report
    these inside a successful response rather than as an HTTP error.
    """

    code: str | None
    message: str | None


class SearchItem(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    id: int
    shortDescription: str | None
    buyItNowPrice: int | None
    sellerId: int
    sellerAlias: str | None
    maxBid: int | None
    thumbnailLink: str | None
    sellerDsrAverage: float
    endDate: str
    nextBid: int | None
    hasBids: bool
    isEnded: bool
    itemType: str | None
    itemUrl: str | None
    categoryId: int
    bidCount: int
    imageLinks: list[ImageLink] | None
    attributeValues: AttributeValues | None
    longDescription: str | None


class SearchResult(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    totalNumberOfItems: int
    totalNumberOfPages: int
    items: list[SearchItem]
    errors: list[SearchError]


class AttributeFilter(TypedDict, total=False):
    key: str
    values: list[str]


class NumberAttributeFilter(TypedDict, total=False):
    key: str
    filterFrom: float | None
    filterTo: float | None


class SearchAdvancedRequest(TypedDict, total=False):
    """
    Body for ``SearchPortal.advanced``. Every field is optional; ``categoryId`` 0
    searches all categories and ``pageNumber`` starts at 1.
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    searchWords: str
    categoryId: int
    searchInDescription: bool
    mode: SearchModes
    priceMinimum: int | None
    priceMaximum: int | None
    bidsMinimum: int | None
    bidsMaximum: int | None
    zipCode: str
    countyId: int
    alias: str
    orderBy: SearchOrderBys
    itemStatus: SearchItemStatuses
    itemType: SearchItemTypes
    onlyAuctionsWithBuyNow: bool
    onlyItemsWithThumbnail: bool
    itemsPerPage: int
    pageNumber: int
    itemCondition: SearchItemConditions
    sellerType: SearchSellerTypes
    brands: list[str]
    campaignCodeIds: list[int]
    attributes: list[AttributeFilter]
    numberAttributes: list[NumberAttributeFilter]


class CategoryCountRequest(TypedDict, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    categoryId: int
    alias: str
    countyId: int
    searchInDescription: bool
    itemCondition: SearchItemConditions
    zipCode: str
    searchWords: str
    pageNumber: int
    onlyItemsWithThumbnail: bool
    onlyAuctionsWithBuyNow: bool
    mode: SearchModes
    priceMinimum: int | None
    priceMaximum: int | None
    bidsMinimum: int | None
    bidsMaximum: int | None
    itemStatus: SearchItemStatuses
    itemType: SearchItemTypes
    sellerType: SearchSellerTypes


class SearchCategory(Taggable, total=False):
    id: int
    name: str | None
    noOfItemsInCategory: int
    noOfItemsInCategoryIncludingChildren: int
    childCategories: list["SearchCategory"]


class CategoryCountResult(Taggable, total=False):
    """
    Shape taken from the v3 WSDL; the v4 OpenAPI spec leaves this schema empty.
    """

    categories: list[SearchCategory]
    errors: list[SearchError]


__all__ = (
    "SearchOrderBys",
    "SearchModes",
    "SearchItemStatuses",
    "SearchItemTypes",
    "SearchItemConditions",
    "SearchSellerTypes",
    "SearchError",
    "SearchItem",
    "SearchResult",
    "AttributeFilter",
    "NumberAttributeFilter",
    "SearchAdvancedRequest",
    "CategoryCountRequest",
    "SearchCategory",
    "CategoryCountResult",
)
