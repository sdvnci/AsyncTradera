from ..common._types import ApiItemTypes, Taggable


class ItemAddedDescription(Taggable):
    description: str | None
    createdDate: str


class RestartedItem(Taggable):
    restartedItemId: int
    restartedAsItemId: int
    restartedDate: str


class ItemRestarts(Taggable):
    lastRestartedItemId: int
    ancestorItemId: int
    restartedItems: list[RestartedItem] | None


class ItemQuickInfo(Taggable):
    creationDate: str
    itemType: ApiItemTypes
    id: int


__all__ = ("ItemAddedDescription", "RestartedItem", "ItemRestarts", "ItemQuickInfo")
