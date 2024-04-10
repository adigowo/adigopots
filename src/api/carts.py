from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.database import engine  

router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    dependencies=[Depends(auth.get_api_key)],
)


class CartCheckout(BaseModel):
    payment: str
    quantity: int  #potions are bought

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """
    Process a cart checkout. This involves:
    - Checking if the requested quantity of green potions is available.
    - Updating the inventory to reflect the sale.
    - Increasing the store's gold by the sale amount.
    """
    select_sql = "SELECT num_green_potions, gold FROM global_inventory WHERE id=1;"
    update_sql = """
        UPDATE global_inventory
        SET num_green_potions = num_green_potions - :quantity,
            gold = gold + (:quantity * :price_per_potion)
        WHERE id=1;
    """
    price_per_potion = 10  
    total_cost = cart_checkout.quantity * price_per_potion
    
    with engine.begin() as connection:
        current_inventory = connection.execute(sqlalchemy.text(select_sql)).fetchone()
        if current_inventory:
            num_green_potions, _ = current_inventory
            if num_green_potions >= cart_checkout.quantity:
                connection.execute(sqlalchemy.text(update_sql), quantity=cart_checkout.quantity, price_per_potion=price_per_potion)
                return {"total_potions_bought": cart_checkout.quantity, "total_gold_paid": total_cost}
            else:
                return {"error": "Not enough potions in stock."}
    return {"error": "Checkout failed."}

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

