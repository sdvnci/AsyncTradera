from enum import IntEnum
from typing import Literal

from ..common._types import Taggable

GetFeedbackRoles = Literal[0, 1, 2]


class GetFeedbackRole(IntEnum):
    """
    Which feedback to fetch: all, feedback received as a seller, or as a buyer.
    """

    ALL = 0
    SELLER = 1
    BUYER = 2


FeedbackRoles = Literal[0, 1]


class FeedbackRole(IntEnum):
    BUYER = 0
    SELLER = 1


FeedbackRatings = Literal[0, 1, 3]


class FeedbackRating(IntEnum):
    NONE = 0
    NEGATIVE = 1
    POSITIVE = 3


class GetFeedback(Taggable):
    feedbackRole: FeedbackRoles
    feedbackRating: FeedbackRatings
    alias: str | None
    comment: str | None
    created: str
    totalRating: int


class FeedbackSummaryItem(Taggable):
    totalPositive: int
    totalNegative: int


class GetFeedbackSummaryResponse(Taggable):
    userId: int
    lastMonth: FeedbackSummaryItem
    lastSixMonth: FeedbackSummaryItem
    lastTwelveMonth: FeedbackSummaryItem


class DetailedSellerRating(Taggable):
    itemAsDescribedCount: int | None
    itemAsDescribedAverage: float | None
    commResponsivenessCount: int | None
    commResponsivenessAverage: float | None
    shippingTimeCount: int | None
    shippingTimeAverage: float | None
    shippingHandlingChargesCount: int | None
    shippingHandlingChargesAverage: float | None


class SellerInfo(Taggable):
    detailedSellerRating: DetailedSellerRating
    totalRating: int
    positiveFeedbackPercent: int | None
    personalMessage: str | None
    isCompany: bool
    hasShop: bool


class UserInfo(Taggable):
    id: int
    alias: str | None
    firstName: str | None
    lastName: str | None
    email: str | None
    phoneNumber: str | None
    address: str | None
    zipCode: str | None
    city: str | None
    countryName: str | None
    personalNumber: str | None
    currencyCode: str | None
    languageCodeIso2: str | None


class MemberPaymentOption(Taggable):
    name: str | None
    description: str | None
    displayName: str | None


class GetMemberPaymentOptionsResult(Taggable):
    paymentOptions: list[MemberPaymentOption] | None


__all__ = (
    "GetFeedbackRoles",
    "GetFeedbackRole",
    "FeedbackRoles",
    "FeedbackRole",
    "FeedbackRatings",
    "FeedbackRating",
    "GetFeedback",
    "FeedbackSummaryItem",
    "GetFeedbackSummaryResponse",
    "DetailedSellerRating",
    "SellerInfo",
    "UserInfo",
    "MemberPaymentOption",
    "GetMemberPaymentOptionsResult",
)
