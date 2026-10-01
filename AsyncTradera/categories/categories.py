from ..common import Endpoints, TraderaClient, TraderaConnection, TraderaErrorResponse
from ._types import AttributeDefinition, Category

ENDPOINT = Endpoints.CATEGORIES.value


class CategoriesPortal(TraderaClient):
    """
    The category tree and per-category attribute definitions. App auth only.
    """

    @classmethod
    async def all(
        cls: type["CategoriesPortal"],
        connection: TraderaConnection,
        identity: bool = False,
    ) -> tuple[int, list[Category] | TraderaErrorResponse]:
        """
        The full category hierarchy.
        """
        return await cls._send(
            connection, "GET", ENDPOINT, list[Category], identity=identity
        )

    @classmethod
    async def attribute_definitions(
        cls: type["CategoriesPortal"],
        connection: TraderaConnection,
        category_id: int,
        identity: bool = False,
    ) -> tuple[int, list[AttributeDefinition] | TraderaErrorResponse]:
        """
        Attribute definitions for a category, including "Skick" (condition) and its
        ``possibleTermValues``.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/{category_id}/attribute-definitions",
            list[AttributeDefinition],
            identity=identity,
        )


__all__ = ("CategoriesPortal",)
