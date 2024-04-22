from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

app = FastAPI()

# MongoDB connection details
MONGO_DETAILS = "mongodb://localhost:27017/shopping_list"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.dbname
collection = db.collection_name

# Helper to handle MongoDB ObjectId
def objectid_str(v):
    return str(v)

# Pydantic models for Data Validation
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    on_offer: Optional[bool] = False

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str = Field(default_factory=objectid_str, alias="_id")

# CRUD operations
@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = await collection.insert_one(item.dict(by_alias=True))
    created_item = await collection.find_one({"_id": new_item.inserted_id})
    return created_item

@app.get("/items/", response_model=List[Item])
async def read_items():
    items = await collection.find().to_list(100)
    return items

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemCreate):
    update_result = await collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict(by_alias=True)})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await collection.find_one({"_id": ObjectId(item_id)})
    return updated_item

@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: str):
    deleted_item = await collection.find_one_and_delete({"_id": ObjectId(item_id)})
    if deleted_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted_item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
