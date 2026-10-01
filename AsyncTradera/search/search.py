from ..common import Endpoints, TraderaClient, TraderaConnection, TraderaErrorResponse
from ._types import (
    CategoryCountRequest,
    CategoryCountResult,
    SearchAdvancedRequest,
    SearchItemTypes,
    SearchOrderBys,
    SearchResult,
)

ENDPOINT = Endpoints.SEARCH.value


class SearchPortal(TraderaClient):
    """
    Item search. App auth only.

    Invalid search parameters come back as ``SearchResult.errors`` on a 200 response,
    so check that list as well as the status.
    """

    @classmethod
    async def search(
        cls: type["SearchPortal"],
        connection: TraderaConnection,
        query: str | None = None,
        category_id: int | None = None,
        page_number: int | None = None,
        order_by: SearchOrderBys | None = None,
        identity: bool = False,
    ) -> tuple[int, SearchResult | TraderaErrorResponse]:
        """
        Simple keyword search. ``category_id`` 0 (or None) searches all categories;
        ``page_number`` starts at 1.
        """
        return await cls._send(
            connection,
            "GET",
            ENDPOINT,
            SearchResult,
            identity=identity,
            params={
                "query": query,
                "categoryId": category_id,
                "pageNumber": page_number,
                "orderBy": order_by,
            },
        )

    @classmethod
    async def advanced(
        cls: type["SearchPortal"],
        connection: TraderaConnection,
        request: SearchAdvancedRequest,
        identity: bool = False,
    ) -> tuple[int, SearchResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/advanced",
            SearchResult,
            identity=identity,
            json=request,
        )

    @classmethod
    async def category_count(
        cls: type["SearchPortal"],
        connection: TraderaConnection,
        request: CategoryCountRequest,
        identity: bool = False,
    ) -> tuple[int, CategoryCountResult | TraderaErrorResponse]:
        """
        Hit counts per category for a search.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/category-count",
            CategoryCountResult,
            identity=identity,
            json=request,
        )

    @classmethod
    async def by_zip_code(
        cls: type["SearchPortal"],
        connection: TraderaConnection,
        zip_code: str,
        page_number: int = 1,
        order_by: SearchOrderBys | None = None,
        identity: bool = False,
    ) -> tuple[int, SearchResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/by-zip-code",
            SearchResult,
            identity=identity,
            json=cls._compact(
                {"zipCode": zip_code, "pageNumber": page_number, "orderBy": order_by}
            ),
        )

    @classmethod
    async def by_fixed_criteria(
        cls: type["SearchPortal"],
        connection: TraderaConnection,
        name: str,
        page_number: int = 1,
        item_type: SearchItemTypes | None = None,
        order_by: SearchOrderBys | None = None,
        identity: bool = False,
    ) -> tuple[int, SearchResult | TraderaErrorResponse]:
        """
        Searches one of Tradera's predefined lists (e.g. ending soon, newly listed),
        selected by ``name``. Tradera does not publish the list names.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/by-fixed-criteria",
            SearchResult,
            identity=identity,
            json=cls._compact(
                {
                    "name": name,
                    "pageNumber": page_number,
                    "itemType": item_type,
                    "orderBy": order_by,
                }
            ),
        )


__all__ = ("SearchPortal",)
