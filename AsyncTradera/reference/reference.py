from collections.abc import Sequence
from typing import cast

from ..common import (
    SUCCESS_STATUSES,
    APIError,
    Endpoints,
    IdDescriptionPair,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
)
from ._types import GetShippingOptionsResponse, ItemFieldsResponse

ENDPOINT = Endpoints.REFERENCE_DATA.value


class ReferenceDataPortal(TraderaClient):
    """
    Static reference data. App auth only.
    https://api.tradera.com/documentation
    """

    @classmethod
    async def time(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
    ) -> tuple[int, str | TraderaErrorResponse]:
        """
        The official Tradera time as an ISO 8601 string.

        The OpenAPI spec declares a bare string while the guide shows ``{"time": ...}``;
        both shapes are accepted and reduced to the string.
        """
        status, payload = await cls._send(connection, "GET", f"{ENDPOINT}/time", object)
        if status not in SUCCESS_STATUSES:
            return status, cast(TraderaErrorResponse, payload)
        if isinstance(payload, dict):
            payload = payload.get("time")
        if isinstance(payload, str):
            return status, payload
        return cls.parse_unknown_exception(
            APIError(500, f"Unexpected time payload: {payload!r}")
        )

    @classmethod
    async def accepted_bidder_types(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, list[IdDescriptionPair] | TraderaErrorResponse]:
        """
        The buyer regions an item can accept: 1 = Sweden, 3 = International, 4 = EU.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/accepted-bidder-types",
            list[IdDescriptionPair],
            identity=identity,
        )

    @classmethod
    async def expo_item_types(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, list[IdDescriptionPair] | TraderaErrorResponse]:
        """
        Expo (promotion) item types with their current fees.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/expo-item-types",
            list[IdDescriptionPair],
            identity=identity,
        )

    @classmethod
    async def item_types(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, list[IdDescriptionPair] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/item-types",
            list[IdDescriptionPair],
            identity=identity,
        )

    @classmethod
    async def counties(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, list[IdDescriptionPair] | TraderaErrorResponse]:
        """
        Swedish counties, used as ``countyId`` in searches.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/counties",
            list[IdDescriptionPair],
            identity=identity,
        )

    @classmethod
    async def item_field_values(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, ItemFieldsResponse | TraderaErrorResponse]:
        """
        VAT rates, payment types, shipping types and the coarse new/used flag needed
        when building an ``ItemRequest`` or ``ShopItemData``.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/item-field-values",
            ItemFieldsResponse,
            identity=identity,
        )

    @classmethod
    async def shipping_options(
        cls: type["ReferenceDataPortal"],
        connection: TraderaConnection,
        from_country_codes: Sequence[str] | None = None,
        category_ids: Sequence[int] | None = None,
        identity: bool = False,
    ) -> tuple[int, GetShippingOptionsResponse | TraderaErrorResponse]:
        """
        The shipping products a seller can offer. Each product's ``shippingProviderId``
        is what goes into ``ItemShipping.shippingProviderId``. The set changes over time,
        so read it from here rather than hard-coding ids.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/shipping-options",
            GetShippingOptionsResponse,
            identity=identity,
            params={
                "fromCountryCodes": from_country_codes,
                "categoryIds": category_ids,
            },
        )


__all__ = ("ReferenceDataPortal",)
