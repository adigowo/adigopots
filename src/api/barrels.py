from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import exc
from src import database as db

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
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        transaction = 0
        gold = 0
        red_ml = 0
        green_ml = 0
        blue_ml = 0
        dark_ml = 0
        
        for barrel in barrels_delivered:
            gold -= barrel.price*barrel.quantity
            
            if barrel.potion_type == [1, 0, 0, 0]:
                red_ml += barrel.ml_per_barrel * barrel.quantity
            elif barrel.potion_type == [0, 1, 0, 0]:
                green_ml += barrel.ml_per_barrel * barrel.quantity
            elif barrel.potion_type == [0, 0, 1, 0]:
                blue_ml += barrel.ml_per_barrel * barrel.quantity
            elif barrel.potion_type == [0, 0, 0, 1]:
                dark_ml += barrel.ml_per_barrel * barrel.quantity
            else:
                raise Exception("invalid barrel")
            
            transaction += 1

            connection.execute(
            sqlalchemy.text(
            """
            INSERT INTO ml_ledger
            (transaction_id, red_ml, green_ml, blue_ml, dark_ml)
            VALUES (:transaction_id, :red_ml, :green_ml, :blue_ml, :dark_ml)
            """
            ),
            [{
            "transaction_id": transaction,
            "red_ml": red_ml,
            "green_ml": green_ml,
            "blue_ml": blue_ml,
            "dark_ml": dark_ml}])

        return "OK"




# @router.post("/deliver/{order_id}")
# def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
#     """Endpoint for delivering barrels."""
#     with engine.begin() as connection:
#         # Get the current inventory and gold
#         result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))
#         row = result.fetchone()
#         num_red_ml, num_green_ml, num_blue_ml, gold = row
        
#         # Update inventory and gold based on delivered barrels
#         for barrel in barrels_delivered:
#             gold -= barrel.price
#             if barrel.potion_type == [100, 0, 0]:  # Red potion
#                 num_red_ml += barrel.ml_per_barrel * barrel.quantity
#             elif barrel.potion_type == [0, 100, 0]:  # Green potion
#                 num_green_ml += barrel.ml_per_barrel * barrel.quantity
#             elif barrel.potion_type == [0, 0, 100]:  # Blue potion
#                 num_blue_ml += barrel.ml_per_barrel * barrel.quantity

#         # Update the database do insert not update 
#         connection.execute(sqlalchemy.text(
#             "UPDATE global_inventory SET num_red_ml=:red, num_green_ml=:green, num_blue_ml=:blue, gold=:gold"),
#             {"red": num_red_ml, "green": num_green_ml, "blue": num_blue_ml, "gold": gold}
#         )

#     return "OK"

@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Determines which barrels to purchase based on inventory and gold."""

    purchase_plan = []
    
    with engine.begin() as connection:
        # Get the current inventory and gold
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))
        row = result.fetchone()
        num_red_ml, num_green_ml, num_blue_ml, gold = row
        
        # Decide on purchasing based on the potion needs
        for barrel in wholesale_catalog:
            if gold > barrel.price:
                quantity_to_buy = min(gold // barrel.price, barrel.quantity)
                if barrel.potion_type == [100, 0, 0] and num_red_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
                elif barrel.potion_type == [0, 100, 0] and num_green_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
                elif barrel.potion_type == [0, 0, 100] and num_blue_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})

        return purchase_plan