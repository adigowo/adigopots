from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from sqlalchemy import text
from src.database import engine  

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """Endpoint for delivering barrels."""
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Determines which barrels to purchase based on inventory and gold."""
    purchase_plan = []
    # SQL query to check current inventory and gold
    select_sql = "SELECT num_green_potions, gold FROM global_inventory WHERE id=1;"
    with engine.begin() as connection:  # Make sure you have defined engine in your database.py
        result = connection.execute(text(select_sql)).fetchone()
        if result:
            num_green_potions, gold = result
            # Assuming each green barrel costs 50 gold and you add 1000 ml per barrel
            if num_green_potions < 10 and gold >= 50:
                for barrel in wholesale_catalog:
                    if barrel.sku == "SMALL_GREEN_BARREL" and barrel.price <= gold:
                        quantity_to_buy = gold // barrel.price
                        purchase_plan.append({
                            "sku": barrel.sku,
                            "quantity": quantity_to_buy,
                        })
                        # Update gold and num_green_ml in inventory
                        update_sql = """
                        UPDATE global_inventory
                        SET gold = gold - (:price * :quantity),
                            num_green_ml = num_green_ml + (:ml_per_barrel * :quantity)
                        WHERE id=1;
                        """
                        connection.execute(text(update_sql), price=barrel.price, quantity=quantity_to_buy, ml_per_barrel=barrel.ml_per_barrel)
                        break
    return purchase_plan
