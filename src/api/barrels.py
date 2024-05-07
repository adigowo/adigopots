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
            INSERT INTO gold_ledger
            (gold, transaction_id)
            VALUES (:gold, :transaction_id)
            """
            ),

            [{
            "gold": gold,
            "transaction_id": transaction}])
            

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


        print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

        return "OK"
    


# @router.post("/plan")
# def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
#     """Determines which barrels to purchase based on inventory and gold."""

#     with db.engine.begin() as connection:
#         # Get the total sum of gold from the gold_ledger
#         gold_sum = connection.execute(
#             sqlalchemy.text("SELECT SUM(gold) AS total_gold FROM gold_ledger")
#         ).fetchone()
#         gold = gold_sum['total_gold'] if gold_sum and 'total_gold' in gold_sum else 0

#         # Get the total ml values
#         ml_sums = connection.execute(
#             sqlalchemy.text("SELECT SUM(red_ml) AS total_red_ml, SUM(green_ml) AS total_green_ml, SUM(blue_ml) AS total_blue_ml, SUM(dark_ml) AS total_dark_ml FROM ml_ledger")
#         ).fetchone()

#         if ml_sums:
#             red_ml = ml_sums['total_red_ml'] if 'total_red_ml' in ml_sums else 0
#             green_ml = ml_sums['total_green_ml'] if 'total_green_ml' in ml_sums else 0
#             blue_ml = ml_sums['total_blue_ml'] if 'total_blue_ml' in ml_sums else 0
#             dark_ml = ml_sums['total_dark_ml'] if 'total_dark_ml' in ml_sums else 0
#         else:
#             red_ml = green_ml = blue_ml = dark_ml = 0  # Set to 0 if no results are returned

#         purchase_plan = []

#         print(f"Available Gold: {gold}, Red ML: {red_ml}, Green ML: {green_ml}, Blue ML: {blue_ml}, Dark ML: {dark_ml}")

#         # Decide on purchasing based on the potion needs
#         for barrel in wholesale_catalog:
#             if gold > barrel.price:
#                 quantity_to_buy = min(gold // barrel.price, barrel.quantity)
#                 if barrel.potion_type == [1, 0, 0, 0] and red_ml < 1000:
#                     purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
#                 elif barrel.potion_type == [0, 1, 0, 0] and green_ml < 1000:
#                     purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
#                 elif barrel.potion_type == [0, 0, 1, 0] and blue_ml < 1000:
#                     purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
#                 elif barrel.potion_type == [0, 0, 0, 1] and dark_ml < 1000:
#                     purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})

#         return purchase_plan


@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """Determines which barrels to purchase based on inventory and gold."""


    with db.engine.begin() as connection:
        # Get the current ml values
        money = connection.execute(sqlalchemy.text("SELECT gold FROM gold_ledger")).fetchone()

        gold = money.gold if money else 0

        purchase_plan = []

        # Get the current ml values
        result = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml FROM ml_ledger")).fetchone()[0]
    
        red_ml = result.red_ml if result else 0
        green_ml = result.green_ml if result else 0
        blue_ml = result.blue_ml if result else 0
        dark_ml = result.dark_ml if result else 0

        
        # Decide on purchasing based on the potion needs
        for barrel in wholesale_catalog:
            if gold > barrel.price:
                quantity_to_buy = min(gold // barrel.price, barrel.quantity)
                if barrel.potion_type == [1, 0, 0, 0] and red_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
                elif barrel.potion_type == [0, 1, 0, 0] and green_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
                elif barrel.potion_type == [0, 0, 1, 0] and blue_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
                elif barrel.potion_type == [0, 0, 0, 1] and dark_ml < 1000:
                    purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})

        return purchase_plan