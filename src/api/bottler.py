from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
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
def post_deliver_potions(potions_delivered: list[PotionInventory], order_id: int):
    """Endpoint for delivering bottled potions."""
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")
    
    total_ml = 0
    total_potions = 0
    with engine.begin() as connection:
        for potion in potions_delivered:
            green_ml = potion.potion_type[1] * potion.quantity  # Calculate green ml based on quantity
            total_ml += green_ml
            total_potions += potion.quantity

        # Update global inventory
        connection.execute(sqlalchemy.text("""
            UPDATE global_inventory
            SET num_green_ml = num_green_ml - :total_ml,
                num_green_potions = num_green_potions + :total_potions
        """), {
            "total_ml": total_ml, 
            "total_potions": total_potions
        })

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle for green potions.
    """
    bottle_plan = []
    
    with engine.begin() as connection:  

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