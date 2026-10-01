from asyncio import run as asyncrun
from datetime import datetime, timedelta
from json import dumps
from os import getenv

from dotenv import load_dotenv

from AsyncTradera import (
    CategoriesPortal,
    OrdersPortal,
    ReferenceDataPortal,
    SellerOrderQueryDateMode,
    TraderaClient,
)

load_dotenv()
APP_ID: str | None = getenv("TRADERA_APP_ID")
APP_KEY: str | None = getenv("TRADERA_APP_KEY")
USER_ID: str | None = getenv("TRADERA_USER_ID")
USER_TOKEN: str | None = getenv("TRADERA_USER_TOKEN")


async def main() -> None:
    if not APP_ID:
        raise ValueError("TRADERA_APP_ID environment variable not set")
    if not APP_KEY:
        raise ValueError("TRADERA_APP_KEY environment variable not set")

    async with TraderaClient.scoped_client(
        app_id=int(APP_ID), app_key=APP_KEY
    ) as connection:
        status, time = await ReferenceDataPortal.time(connection)
        print(status, time)

        status, categories = await CategoriesPortal.all(connection, identity=True)
        print(status, f"{len(categories)} top-level categories")

        if USER_ID and USER_TOKEN:
            seller = await TraderaClient.connect_user(
                connection, int(USER_ID), USER_TOKEN
            )
            status, orders = await OrdersPortal.where(
                seller,
                from_date=datetime.now() - timedelta(days=7),
                query_date_mode=SellerOrderQueryDateMode.LAST_UPDATED_DATE,
                identity=True,
            )
            print(status, dumps(orders, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    asyncrun(main())
