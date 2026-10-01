from ..common._types import IdDescriptionPair, Taggable


class ItemFieldsResponse(Taggable):
    """
    ``itemAttributes`` holds only the coarse condition flag (1 = Ny, 2 = Begagnad).
    The finer "Skick" values come from ``CategoriesPortal.attribute_definitions``.
    """

    vat: list[int] | None
    itemAttributes: list[IdDescriptionPair] | None
    paymentTypes: list[IdDescriptionPair] | None
    shippingTypes: list[IdDescriptionPair] | None


class ShippingPackageRequirements(Taggable):
    maxWeight: float | None
    minWeight: float | None
    maxSumOfAllSides: float | None
    maxSumOfLengthAndHeight: float | None
    maxLengthPlusCircumference: float | None
    maxLength: float | None
    maxWidth: float | None
    maxHeight: float | None
    maxVolume: float | None
    minLength: float | None
    minWidth: float | None
    minHeight: float | None
    restrictions: list[str] | None


class ShippingEstimatedDeliveryTime(Taggable):
    minWeekdays: int
    maxWeekdays: int | None


class ShippingInsurance(Taggable):
    totalAmount: float | None
    totalAmountUpToItemValue: float | None
    amountPerKilogram: float | None
    hasReimbursementUpToPackageCost: bool


class ShippingDeliveryInformation(Taggable):
    mailBoxWithServicePointBackup: bool
    servicePoint: bool
    canChangeServicePoint: bool
    isTraceable: bool
    isParcelBoxDeliveryPossible: bool
    estimatedDeliveryTime: ShippingEstimatedDeliveryTime
    insurance: ShippingInsurance


class ShippingTermsAndConditions(Taggable):
    termsAndConditionUrl: str | None
    general: str | None
    termsOfService: str | None
    termsOfPurchase: str | None


class ShippingProduct(Taggable):
    id: int
    shippingProvider: str | None
    shippingProviderId: int
    name: str | None
    weight: float
    price: int
    vatPercent: int | None
    toCountry: str | None
    fromCountry: str | None
    packageRequirements: ShippingPackageRequirements
    dimensionsExceededPenalty: int
    weightExceededPenalty: int
    displayPenaltyWarning: bool
    deliveryInformation: ShippingDeliveryInformation
    termsAndConditions: ShippingTermsAndConditions


class ProductsPerWeightSpan(Taggable):
    weight: float
    products: list[ShippingProduct] | None


class GetShippingOptionsResponse(Taggable):
    productsPerWeightSpan: list[ProductsPerWeightSpan] | None


__all__ = (
    "ItemFieldsResponse",
    "ShippingPackageRequirements",
    "ShippingEstimatedDeliveryTime",
    "ShippingInsurance",
    "ShippingDeliveryInformation",
    "ShippingTermsAndConditions",
    "ShippingProduct",
    "ProductsPerWeightSpan",
    "GetShippingOptionsResponse",
)
