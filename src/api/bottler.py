from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src.database import engine  # Assuming your database setup is in src/database.py

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]  # Assuming [0, 0, 100, 0] represents 100% green potion
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """Endpoint for delivering bottled potions."""
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle for green potions.
    """
    bottle_plan = []
    select_sql = "SELECT num_green_ml FROM global_inventory WHERE id=1;"
    update_sql = """
        UPDATE global_inventory
        SET num_green_ml = num_green_ml - :used_ml,
            num_green_potions = num_green_potions + :new_potions
        WHERE id=1;
    """
    with engine.begin() as connection:  # Ensure engine is correctly defined in your database.py
        current_inventory = connection.execute(sqlalchemy.text(select_sql)).fetchone()
        if current_inventory:
            num_green_ml = current_inventory['num_green_ml']
            # Assuming each potion requires 100 ml
            new_potions = num_green_ml // 100
            if new_potions > 0:
                used_ml = new_potions * 100
                connection.execute(sqlalchemy.text(update_sql), used_ml=used_ml, new_potions=new_potions)
                bottle_plan.append({
                    "potion_type": [0, 0, 100, 0],  # Representing 100% green potion
                    "quantity": new_potions,
                })
    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())