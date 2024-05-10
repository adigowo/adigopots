from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import exc
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]  
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_potions(potions_delivered: list[PotionInventory], order_id: int):
    """Endpoint for delivering bottled potions."""
    print("potions delivered: {potions_delivered} order_id: {order_id}")

    red_used = 0
    green_used = 0
    blue_used = 0
    dark_used = 0
    transaction = -1
    
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            red_used -= potion.potion_type[0] * potion.quantity
            green_used -= potion.potion_type[1] * potion.quantity
            blue_used -= potion.potion_type[2] * potion.quantity
            dark_used -= potion.potion_type[3] * potion.quantity
        
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
            "red_ml": red_used,
            "green_ml": green_used,
            "blue_ml": blue_used,
            "dark_ml": dark_used}])
        
        for potion in potions_delivered:
            
             connection.execute(
                sqlalchemy.text(
                """
                INSERT INTO potion_ledger
                (transaction_id, potion_id, quantity )
                VALUES (:transaction_id, :potion_id:, :quantity)
                """
                ),
                [{
                "transaction_id": transaction,
                "potion_id": potion.potion_type,
                "quantity": potion.quantity,}])
             
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle for green potions.
    """
    bottle_plan = []
    
    with db.engine.begin() as connection:  

        result = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_green_potions, num_red_ml, num_red_potions, num_blue_ml, num_blue_potions gold FROM global_inventory"))
        row = result.fetchone()
        num_green_ml = row[0]
        num_green_potions = row[1]
        num_red_ml = row[2]
        num_red_potions = row[3]
        num_blue_ml = row[4]
        num_blue_potions = row[5]
       
           
        # new_green_potions = num_green_ml // 100
        # used_ml = new_potions * 100
        

        # num_green_ml = num_green_ml - used_ml
        # new_potions = num_green_potions + new_potions

        if num_green_ml > 50:
            bottle_plan.append({
                "potion_type": [0, 100, 0], 
                "quantity": 1,
            })

        elif num_red_ml > 50:
            bottle_plan.append({
                "potion_type": [100, 0, 0], 
                "quantity": 1,
            })
        
        elif num_blue_ml > 50:
            bottle_plan.append({
                "potion_type": [0, 0, 100], 
                "quantity": 1,
            })
        
        


    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())