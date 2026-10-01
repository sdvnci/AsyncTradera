from ..common._types import Taggable


class Category(Taggable, total=False):
    """
    A node in the category tree. The v4 OpenAPI spec leaves this schema empty;
    the shape here was checked against a live response.
    """

    id: int
    name: str
    childCategories: list["Category"]


class AttributeDefinition(Taggable):
    """
    A category attribute such as "Skick" (condition). Submit a chosen value as
    ``{"id": definition["id"], "values": [...]}`` in ``ItemAttributeValues.terms``.
    """

    id: int
    name: str | None
    description: str | None
    maxNumberOfValues: int
    minNumberOfValues: int
    possibleTermValues: list[str] | None
    key: str | None
    attributeType: str | None
    valueFormatting: str | None


__all__ = ("Category", "AttributeDefinition")
