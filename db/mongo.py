import pymongo as mg
from utils.config import MONGO_CONNECTION_STRING
from bson.objectid import ObjectId
from routers.models import UserInDB
import motor.motor_asyncio

class Mongo():
    def __init__(self, db: str, collection: str):
        self.url = MONGO_CONNECTION_STRING
        self.db_name = db
        self.collection_name = collection
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.url)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def _connect(self) -> None:
        try:
            self.client = mg.MongoClient(self.url)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except mg.errors.ConnectionFailure as e:
            print(f"Connection error: {e}")

    def _get_collection(self, collection: str):
        return self.db[collection]

    async def get_user(self, username: str):
        user = await self.collection.find_one({"username": username})
        if user:
            return UserInDB(
                username=user["username"],
                email=user["email"],
                hashed_password=user["hashed_password"],
                disabled=user.get("disabled", False)
            )
        return None

    def _user_helper(self, user) -> dict:
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "password": user["password"]
        }

    async def create_db(self, db: str) -> None:
        if db not in await self.client.list_database_names():
            self.client[db]
            print(f"Database {db} created")

    async def create_collection(self, collection: str) -> None:
        if collection not in await self.db.list_collection_names():
            self.db.create_collection(collection)
            print(f"Collection {collection} created")

    async def create_user(self, user: dict) -> dict:
            result = await self.collection.insert_one(user)
            return await self.collection.find_one({"_id": result.inserted_id})

    async def get_me_id(self, username: str) -> str:
        user = await self.collection.find_one({"username" : username})
        return str(user["_id"])

    async def get_user_by_github_id(self, github_id: int):
        return await self.collection.find_one({"github_id": github_id})

    async def get_user_by_username(self, username: str) -> dict:
        return await self.collection.find_one({"username": username})

    async def get_user_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def update_user(self, username: str, data: dict) -> bool:
        if len(data) < 1:
            return False
        result = await self.collection.update_one(
            {"username": username}, {"$set": data}
        )
        return result.modified_count > 0

    async def delete_user(self, username: str) -> bool:
        result = await self.collection.delete_one({"username": username})
        return result.deleted_count > 0

if __name__ == "__main__":
    pass