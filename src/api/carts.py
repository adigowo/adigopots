from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

from sqlalchemy import select, desc, asc


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    query = select(LineItem)


    if customer_name:
        query = query.where(LineItem.customer_name.ilike(f"%{customer_name}%"))
    if potion_sku:
        query = query.where(LineItem.item_sku.ilike(f"%{potion_sku}%"))


    sort_expression = {
        search_sort_options.customer_name: LineItem.customer_name,
        search_sort_options.item_sku: LineItem.item_sku,
        search_sort_options.line_item_total: LineItem.line_item_total,
        search_sort_options.timestamp: LineItem.timestamp,
    }[sort_col]

    if sort_order == search_sort_order.desc:
        query = query.order_by(desc(sort_expression))
    else:
        query = query.order_by(asc(sort_expression))


    if search_page:
        query = query.offset(int(search_page) * 5)  
    query = query.limit(5)

  
    with db.engine.connect() as conn:
        result = conn.execute(query)
        items = [
            {
                "line_item_id": row.LineItem.id,
                "item_sku": row.LineItem.item_sku,
                "customer_name": row.LineItem.customer_name,
                "line_item_total": row.LineItem.line_item_total,
                "timestamp": row.LineItem.timestamp.isoformat(),
            }
            for row in result
        ]

    return {
        "previous": "" if search_page == "" else max(0, int(search_page) - 1),
        "next": int(search_page) + 1 if items else "",
        "results": items
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    return {"total_potions_bought": 1, "total_gold_paid": 50}