from fastapi import APIRouter
import sqlalchemy
from src.database import engine  

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    # """
    # Fetches the current catalog of potions available for sale, focusing on green potions for Version 1.
    # """
    # #number of green potions available and their price

    # catalog = []
    # with engine.begin() as connection:
    #     results = connection.execute(sqlalchemy.text("SELECT inventory, sku, type, price from potion_catalog")).all()

    #     for row in results:
    #         catalog.append({"sku": row.sku, "quantity": row.inventory, "potion_type": row.type,"price": row.price})    

    # return catalog

    # catalog = []
    # with engine.begin() as connection:
    #     results = connection.execute(sqlalchemy.text("SELECT inventory, sku, type, price FROM potion_catalog")).all()
    #     for row in results:
    #         catalog.append({"sku": row.sku, "quantity": row.inventory, "potion_type": row.type, "price": row.price})
    #     return catalog

    select_sql = "SELECT potion_id, potion_name, inventory, red, green, blue, dark, price FROM global_inventory;"
    with engine.connect() as connection:
        results = connection.execute(sqlalchemy.text(select_sql)).all()
        catalog = [{
            "sku": "POTION_{row.potion_id}",
            "name": row.potion_name,
            "quantity": row.inventory,
            "price": row.price,
            "potion_type": [row.red, row.green, row.blue, row.dark]
        } for row in results]
        return catalog if catalog else [{"error": "No potions available."}]


# me rn

    # select_sql = "SELECT * FROM global_inventory;"
    # with engine.connect() as connection:
    #     result = connection.execute(sqlalchemy.text(select_sql)).all()
    
    # returnList = []
    # count = 0
    # for potion in result:
    #     if count >=20:
    #         break
    #     with db.engine.begin() as connection:
    #         returnList = connection.execute(sqlalchemy.text (""" SELECT SUM(quantity) AS potion_quantity FROM potion_ledger WHERE potion_ledger.potion_id = :potion_id;"""), [{"potion_id" : potion.potion_id}]).first()

    #         return(returnList)






    #     if result:
    #         num_green_potions, _ = result
            
    #         price_per_potion = 10  

            
    #         if num_green_potions > 0:
    #             return [{
    #                 "sku": "GREEN_POTION_0",
    #                 "name": "green potion",
    #                 "quantity": num_green_potions,
    #                 "price": price_per_potion,
    #                 "potion_type": [0, 100, 0, 0], 
    #             }]
    #         else:
    #             return [{"error": "No green potions available."}]

    # return [{"error": "Unable to fetch catalog."}]
