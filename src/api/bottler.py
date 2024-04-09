from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
from sqlalchemy import text
from src.database import engine


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """delivered potions end point """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Converts barrel contents to bottled potions, focusing on green potions.
    """
    # Query for green
    select_sql = "SELECT num_green_ml FROM global_inventory WHERE id=1;"
    with engine.begin() as connection:
        num_green_ml = connection.execute(text(select_sql)).scalar()
    
   
    num_potions_to_brew = num_green_ml // 100
    if num_potions_to_brew > 0:
        
        update_sql = """
        UPDATE global_inventory
        SET num_green_potions = num_green_potions + :num_potions,
            num_green_ml = num_green_ml - (:num_potions * 100)
        WHERE id=1;
        """
        connection.execute(text(update_sql), num_potions=num_potions_to_brew)
    
    
    return [
        {
            "potion_type": [0, 0, 100, 0],  
            "quantity": num_potions_to_brew,
        }
    ]

if __name__ == "__main__":
    print(get_bottle_plan())