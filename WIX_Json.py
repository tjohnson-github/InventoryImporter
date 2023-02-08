# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = temperatures_from_dict(json.loads(json_string))

from typing import Optional, Any, List, TypeVar, Callable, Type, cast
from uuid import UUID
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


class Collection:
    id: Optional[UUID]
    name: Optional[str]
    main_media: Optional[str]

    def __init__(self, id: Optional[UUID], name: Optional[str], main_media: Optional[str]) -> None:
        self.id = id
        self.name = name
        self.main_media = main_media

    @staticmethod
    def from_dict(obj: Any) -> 'Collection':
        assert isinstance(obj, dict)
        id = from_union([lambda x: UUID(x), from_none], obj.get("_id"))
        name = from_union([from_str, from_none], obj.get("name"))
        main_media = from_union([from_str, from_none], obj.get("mainMedia"))
        return Collection(id, name, main_media)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"] = from_union([lambda x: str(x), from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["mainMedia"] = from_union([from_str, from_none], self.main_media)
        return result


class Discount:
    type: Optional[str]
    value: Optional[int]

    def __init__(self, type: Optional[str], value: Optional[int]) -> None:
        self.type = type
        self.value = value

    @staticmethod
    def from_dict(obj: Any) -> 'Discount':
        assert isinstance(obj, dict)
        type = from_union([from_str, from_none], obj.get("type"))
        value = from_union([from_int, from_none], obj.get("value"))
        return Discount(type, value)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_union([from_str, from_none], self.type)
        result["value"] = from_union([from_int, from_none], self.value)
        return result


class MediaItem:
    id: Optional[str]
    src: Optional[str]
    description: Optional[str]
    title: Optional[str]
    type: Optional[str]

    def __init__(self, id: Optional[str], src: Optional[str], description: Optional[str], title: Optional[str], type: Optional[str]) -> None:
        self.id = id
        self.src = src
        self.description = description
        self.title = title
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> 'MediaItem':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        src = from_union([from_str, from_none], obj.get("src"))
        description = from_union([from_str, from_none], obj.get("description"))
        title = from_union([from_str, from_none], obj.get("title"))
        type = from_union([from_str, from_none], obj.get("type"))
        return MediaItem(id, src, description, title, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        result["src"] = from_union([from_str, from_none], self.src)
        result["description"] = from_union([from_str, from_none], self.description)
        result["title"] = from_union([from_str, from_none], self.title)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


class ProductOptions:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'ProductOptions':
        assert isinstance(obj, dict)
        return ProductOptions()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class Products:
    id:                         Optional[UUID]
    updated_date:               Optional[datetime]
    name:                       Optional[str]
    description:                Optional[str]
    main_media:                 Optional[str]
    media_items:                Optional[List[MediaItem]]
    sku:                        Optional[str]
    ribbons:                    Optional[List[Any]]
    currency:                   Optional[str]
    price:                      Optional[float]
    discounted_price:           Optional[float]
    formatted_price:            Optional[str]
    formatted_discounted_price: Optional[str]
    discount:                   Optional[Discount]
    track_inventory:            Optional[bool]
    in_stock:                   Optional[bool]
    additional_info_sections:   Optional[List[Any]]
    product_options:            Optional[ProductOptions]
    product_page_url:           Optional[str]
    custom_text_fields:         Optional[List[Any]]
    manage_variants:            Optional[bool]
    product_type:               Optional[str]
    slug:                       Optional[str]
    weight:                     Optional[int]
    collections:                Optional[List[Collection]]
    ribbon:                     Optional[str]
    inventory_item:             Optional[UUID]

    def __init__(self, id: Optional[UUID], updated_date: Optional[datetime], name: Optional[str], description: Optional[str], main_media: Optional[str], media_items: Optional[List[MediaItem]], sku: Optional[str], ribbons: Optional[List[Any]], currency: Optional[str], price: Optional[float], discounted_price: Optional[float], formatted_price: Optional[str], formatted_discounted_price: Optional[str], discount: Optional[Discount], track_inventory: Optional[bool], in_stock: Optional[bool], additional_info_sections: Optional[List[Any]], product_options: Optional[ProductOptions], product_page_url: Optional[str], custom_text_fields: Optional[List[Any]], manage_variants: Optional[bool], product_type: Optional[str], slug: Optional[str], weight: Optional[int], collections: Optional[List[Collection]], ribbon: Optional[str], inventory_item: Optional[UUID]) -> None:
        self.id = id
        self.updated_date = updated_date
        self.name = name
        self.description = description
        self.main_media = main_media
        self.media_items = media_items
        self.sku = sku
        self.ribbons = ribbons
        self.currency = currency
        self.price = price
        self.discounted_price = discounted_price
        self.formatted_price = formatted_price
        self.formatted_discounted_price = formatted_discounted_price
        self.discount = discount
        self.track_inventory = track_inventory
        self.in_stock = in_stock
        self.additional_info_sections = additional_info_sections
        self.product_options = product_options
        self.product_page_url = product_page_url
        self.custom_text_fields = custom_text_fields
        self.manage_variants = manage_variants
        self.product_type = product_type
        self.slug = slug
        self.weight = weight
        self.collections = collections
        self.ribbon = ribbon
        self.inventory_item = inventory_item

    @staticmethod
    def from_dict(obj: Any) -> 'Products':
        assert isinstance(obj, dict)
        id                          = from_union([lambda x: UUID(x), from_none], obj.get("_id"))
        updated_date                = from_union([from_datetime, from_none], obj.get("_updatedDate"))
        name                        = from_union([from_str, from_none], obj.get("name"))
        description                 = from_union([from_str, from_none], obj.get("description"))
        main_media                  = from_union([from_str, from_none], obj.get("mainMedia"))
        media_items                 = from_union([lambda x: from_list(MediaItem.from_dict, x), from_none], obj.get("mediaItems"))
        sku                         = from_union([from_str, from_none], obj.get("sku"))
        ribbons                     = from_union([lambda x: from_list(lambda x: x, x), from_none], obj.get("ribbons"))
        currency                    = from_union([from_str, from_none], obj.get("currency"))
        price                       = from_union([from_float, from_none], obj.get("price"))
        discounted_price            = from_union([from_float, from_none], obj.get("discountedPrice"))
        formatted_price             = from_union([from_str, from_none], obj.get("formattedPrice"))
        formatted_discounted_price  = from_union([from_str, from_none], obj.get("formattedDiscountedPrice"))
        discount                    = from_union([Discount.from_dict, from_none], obj.get("discount"))
        track_inventory             = from_union([from_bool, from_none], obj.get("trackInventory"))
        in_stock                    = from_union([from_bool, from_none], obj.get("inStock"))
        additional_info_sections    = from_union([lambda x: from_list(lambda x: x, x), from_none], obj.get("additionalInfoSections"))
        product_options             = from_union([ProductOptions.from_dict, from_none], obj.get("productOptions"))
        product_page_url            = from_union([from_str, from_none], obj.get("productPageUrl"))
        custom_text_fields          = from_union([lambda x: from_list(lambda x: x, x), from_none], obj.get("customTextFields"))
        manage_variants             = from_union([from_bool, from_none], obj.get("manageVariants"))
        product_type                = from_union([from_str, from_none], obj.get("productType"))
        slug                        = from_union([from_str, from_none], obj.get("slug"))
        weight                      = from_union([from_int, from_none], obj.get("weight"))
        collections                 = from_union([lambda x: from_list(Collection.from_dict, x), from_none], obj.get("collections"))
        ribbon                      = from_union([from_str, from_none], obj.get("ribbon"))
        inventory_item              = from_union([lambda x: UUID(x), from_none], obj.get("inventoryItem"))
        return Products(id, updated_date, name, description, main_media, media_items, sku, ribbons, currency, price, discounted_price, formatted_price, formatted_discounted_price, discount, track_inventory, in_stock, additional_info_sections, product_options, product_page_url, custom_text_fields, manage_variants, product_type, slug, weight, collections, ribbon, inventory_item)

    def to_dict(self) -> dict:
        result: dict = {}
        result["_id"]                       = from_union([lambda x: str(x), from_none], self.id)
        result["_updatedDate"]              = from_union([lambda x: x.isoformat(), from_none], self.updated_date)
        result["name"]                      = from_union([from_str, from_none], self.name)
        result["description"]               = from_union([from_str, from_none], self.description)
        result["mainMedia"]                 = from_union([from_str, from_none], self.main_media)
        result["mediaItems"]                = from_union([lambda x: from_list(lambda x: to_class(MediaItem, x), x), from_none], self.media_items)
        result["sku"]                       = from_union([from_str, from_none], self.sku)
        result["ribbons"]                   = from_union([lambda x: from_list(lambda x: x, x), from_none], self.ribbons)
        result["currency"]                  = from_union([from_str, from_none], self.currency)
        result["price"]                     = from_union([to_float, from_none], self.price)
        result["discountedPrice"]           = from_union([to_float, from_none], self.discounted_price)
        result["formattedPrice"]            = from_union([from_str, from_none], self.formatted_price)
        result["formattedDiscountedPrice"]  = from_union([from_str, from_none], self.formatted_discounted_price)
        result["discount"]                  = from_union([lambda x: to_class(Discount, x), from_none], self.discount)
        result["trackInventory"]            = from_union([from_bool, from_none], self.track_inventory)
        result["inStock"]                   = from_union([from_bool, from_none], self.in_stock)
        result["additionalInfoSections"]    = from_union([lambda x: from_list(lambda x: x, x), from_none], self.additional_info_sections)
        result["productOptions"]            = from_union([lambda x: to_class(ProductOptions, x), from_none], self.product_options)
        result["productPageUrl"]            = from_union([from_str, from_none], self.product_page_url)
        result["customTextFields"]          = from_union([lambda x: from_list(lambda x: x, x), from_none], self.custom_text_fields)
        result["manageVariants"]            = from_union([from_bool, from_none], self.manage_variants)
        result["productType"]               = from_union([from_str, from_none], self.product_type)
        result["slug"]                      = from_union([from_str, from_none], self.slug)
        result["weight"]                    = from_union([from_int, from_none], self.weight)
        result["collections"]               = from_union([lambda x: from_list(lambda x: to_class(Collection, x), x), from_none], self.collections)
        result["ribbon"]                    = from_union([from_str, from_none], self.ribbon)
        result["inventoryItem"]             = from_union([lambda x: str(x), from_none], self.inventory_item)
        return result


class Temperatures:
    products: Optional[Products]

    def __init__(self, products: Optional[Products]) -> None:
        self.products = products

    @staticmethod
    def from_dict(obj: Any) -> 'Temperatures':
        assert isinstance(obj, dict)
        products = from_union([Products.from_dict, from_none], obj.get("products"))
        return Temperatures(products)

    def to_dict(self) -> dict:
        result: dict = {}
        result["products"] = from_union([lambda x: to_class(Products, x), from_none], self.products)
        return result


def temperatures_from_dict(s: Any) -> Temperatures:
    return Temperatures.from_dict(s)


def temperatures_to_dict(x: Temperatures) -> Any:
    return to_class(Temperatures, x)

