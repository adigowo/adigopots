from fastapi import APIRouter
import sqlalchemy
from src.database import engine  

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Fetches the current catalog of potions available for sale, focusing on green potions for Version 1.
    """
    #number of green potions available and their price
    select_sql = "SELECT num_green_potions, gold FROM global_inventory;"

    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(select_sql)).fetchone()
        if result:
            num_green_potions, _ = result
            
            price_per_potion = 10  

            
            if num_green_potions > 0:
                return [{
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num_green_potions,
                    "price": price_per_potion,
                    "potion_type": [0, 0, 100, 0], 
                }]
            else:
                return [{"error": "No green potions available."}]

    return [{"error": "Unable to fetch catalog."}]
