from collections.abc import Sequence

from ..common import (
    ActiveFilter,
    ActiveFilters,
    DateLike,
    Endpoints,
    ImageFormat,
    ImageFormats,
    Item,
    ItemTypeFilter,
    ItemTypeFilters,
    QueuedRequestResponse,
    RequestResult,
    TraderaClient,
    TraderaConnection,
    TraderaErrorResponse,
    Transaction,
)
from ._types import (
    FeedbackType,
    FeedbackTypes,
    ItemRequest,
    RestartItemResult,
    SetPricesNonShopItem,
    SetPricesOnNonShopItemsResult,
    TransactionFilter,
    TransactionFilters,
    UpdatedItemInfo,
    UpdateItemPriceResult,
    ValidateCampaignCodeResult,
)

ENDPOINT = Endpoints.LISTINGS.value


class ListingsPortal(TraderaClient):
    """
    The authenticated seller's non-shop listings (auctions and fixed-price items),
    their transactions and feedback. Every method needs a user connection.
    Shop items live in ``ShopPortal``.

    Writes are queued: ``add``, ``restart`` and the shop endpoints return ids to poll
    with ``request_results``.
    """

    @classmethod
    async def get(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, Item | TraderaErrorResponse]:
        """
        The seller's view of one of their items. 404 if it is not theirs.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/items/{item_id}",
            Item,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def seller_items(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        category_id: int | None = None,
        filter_active: ActiveFilter | ActiveFilters | None = None,
        min_end_date: DateLike | None = None,
        max_end_date: DateLike | None = None,
        filter_item_type: ItemTypeFilter | ItemTypeFilters | None = None,
        max_start_date: DateLike | None = None,
        identity: bool = False,
    ) -> tuple[int, list[Item] | TraderaErrorResponse]:
        """
        The seller's items. Items with a future start date are never returned.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/seller-items",
            list[Item],
            auth="user",
            identity=identity,
            params={
                "categoryId": category_id,
                "filterActive": filter_active,
                "minEndDate": min_end_date,
                "maxEndDate": max_end_date,
                "filterItemType": filter_item_type,
                "maxStartDate": max_start_date,
            },
        )

    @classmethod
    async def updated_seller_items(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        row_version: int | None = None,
        identity: bool = False,
    ) -> tuple[int, list[UpdatedItemInfo] | TraderaErrorResponse]:
        """
        Items changed since ``row_version``. Store the highest ``rowVersion`` seen and
        pass it on the next call to sync incrementally.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/updated-seller-items",
            list[UpdatedItemInfo],
            auth="user",
            identity=identity,
            params={"rowVersion": row_version},
        )

    @classmethod
    async def seller_transactions(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        min_transaction_date: DateLike | None = None,
        max_transaction_date: DateLike | None = None,
        filter: TransactionFilter | TransactionFilters | None = None,
        identity: bool = False,
    ) -> tuple[int, list[Transaction] | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/seller-transactions",
            list[Transaction],
            auth="user",
            identity=identity,
            params={
                "minTransactionDate": min_transaction_date,
                "maxTransactionDate": max_transaction_date,
                "filter": filter,
            },
        )

    @classmethod
    async def add(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item: ItemRequest,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        """
        Queues a new auction or fixed-price listing. See ``ItemRequest`` for item types
        and the ``autoCommit`` flow.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items",
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json=item,
        )

    @classmethod
    async def add_xml(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        xml: str,
        identity: bool = False,
    ) -> tuple[int, QueuedRequestResponse | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items/xml",
            QueuedRequestResponse,
            auth="user",
            identity=identity,
            json={"createItemRequestXml": xml},
        )

    @classmethod
    async def add_image(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        request_id: int,
        image: bytes,
        image_format: ImageFormat | ImageFormats,
        has_mega: bool = False,
    ) -> tuple[int, None | TraderaErrorResponse]:
        """
        Attaches an image to an uncommitted listing request.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items/{request_id}/images",
            type(None),
            auth="user",
            json={
                "imageData": cls._b64(image),
                "imageFormat": int(image_format),
                "hasMega": has_mega,
            },
        )

    @classmethod
    async def add_campaign_code(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        request_id: int,
        campaign_code: str,
    ) -> tuple[int, None | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items/{request_id}/campaign-code",
            type(None),
            auth="user",
            json={"campaignCode": campaign_code},
        )

    @classmethod
    async def commit(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        request_id: int,
    ) -> tuple[int, None | TraderaErrorResponse]:
        """
        Publishes a listing added with ``autoCommit`` False. Published items are live
        and sales are binding.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items/{request_id}/commit",
            type(None),
            auth="user",
        )

    @classmethod
    async def end(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item_id: int,
    ) -> tuple[int, bool | TraderaErrorResponse]:
        """
        Ends a non-shop listing.
        """
        return await cls._send(
            connection,
            "DELETE",
            f"{ENDPOINT}/items/{item_id}",
            bool,
            auth="user",
        )

    @classmethod
    async def restart(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item_id: int,
        identity: bool = False,
    ) -> tuple[int, RestartItemResult | TraderaErrorResponse]:
        """
        Relists an ended item as a new item. Items that are not ended, sold, already
        restarted, or out of restarts come back with ``isSuccessful`` False.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/items/{item_id}/restart",
            RestartItemResult,
            auth="user",
            identity=identity,
        )

    @classmethod
    async def set_prices(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item: SetPricesNonShopItem,
        identity: bool = False,
    ) -> tuple[int, SetPricesOnNonShopItemsResult | TraderaErrorResponse]:
        """
        Sets prices on an auction, deriving the item type from the prices given.
        See ``SetPricesNonShopItem``.
        """
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/items/prices",
            SetPricesOnNonShopItemsResult,
            auth="user",
            identity=identity,
            json=item,
        )

    @classmethod
    async def update_price(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        item_id: int,
        opening_price: int | None = None,
        bin_price: int | None = None,
        identity: bool = False,
    ) -> tuple[int, UpdateItemPriceResult | TraderaErrorResponse]:
        """
        Updates a non-shop item's price without changing its type. Pass the fields that
        apply: ``opening_price`` for auctions, ``bin_price`` for Buy Now.
        """
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/items/{item_id}/price",
            UpdateItemPriceResult,
            auth="user",
            identity=identity,
            json=cls._compact({"openingPrice": opening_price, "binPrice": bin_price}),
        )

    @classmethod
    async def request_results(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        request_ids: int | Sequence[int],
        identity: bool = False,
    ) -> tuple[int, list[RequestResult] | TraderaErrorResponse]:
        """
        Outcomes of queued listing and shop requests. Requests still being processed
        have no entry yet.
        """
        return await cls._send(
            connection,
            "GET",
            f"{ENDPOINT}/request-results",
            list[RequestResult],
            auth="user",
            identity=identity,
            params={
                "requestIds": (
                    [request_ids] if isinstance(request_ids, int) else request_ids
                )
            },
        )

    @classmethod
    async def leave_feedback(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        transaction_id: int,
        comment: str,
        feedback_type: FeedbackType | FeedbackTypes,
    ) -> tuple[int, bool | TraderaErrorResponse]:
        """
        Needs activation by Tradera.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/feedback/transaction/{transaction_id}",
            bool,
            auth="user",
            json={"comment": comment, "type": int(feedback_type)},
        )

    @classmethod
    async def leave_order_feedback(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        order_number: int,
        comment: str,
        feedback_type: FeedbackType | FeedbackTypes,
    ) -> tuple[int, None | TraderaErrorResponse]:
        """
        Leaves feedback to the buyer of an order. Needs activation by Tradera.
        """
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/feedback/order/{order_number}",
            type(None),
            auth="user",
            json={"comment": comment, "type": int(feedback_type)},
        )

    @classmethod
    async def validate_campaign_code(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        campaign_code: str,
        category_id: int,
        identity: bool = False,
    ) -> tuple[int, ValidateCampaignCodeResult | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "POST",
            f"{ENDPOINT}/validate-campaign-code",
            ValidateCampaignCodeResult,
            auth="user",
            identity=identity,
            json={"campaignCode": campaign_code, "categoryId": category_id},
        )

    @classmethod
    async def update_transaction_status(
        cls: type["ListingsPortal"],
        connection: TraderaConnection,
        transaction_id: int,
        mark_as_paid_confirmed: bool | None = None,
        marked_as_shipped: bool | None = None,
        mark_shipping_booked: bool | None = None,
        identity: bool = False,
    ) -> tuple[int, Transaction | TraderaErrorResponse]:
        return await cls._send(
            connection,
            "PUT",
            f"{ENDPOINT}/transaction-status",
            Transaction,
            auth="user",
            identity=identity,
            json=cls._compact(
                {
                    "transactionId": transaction_id,
                    "markAsPaidConfirmed": mark_as_paid_confirmed,
                    "markedAsShipped": marked_as_shipped,
                    "markShippingBooked": mark_shipping_booked,
                }
            ),
        )


__all__ = ("ListingsPortal",)
