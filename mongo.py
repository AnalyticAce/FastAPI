import pymongo as mg
from config import MONGO_CONNECTION_STRING
from bson.objectid import ObjectId
# import motor.motor_asyncio

class Mongo():
    def __init__(self, db: str, collection: str):
        self.url = MONGO_CONNECTION_STRING
        self.db_name = db
        self.collection_name = collection
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self) -> None:
        try:
            self.client = mg.MongoClient(self.url)
            # self.client = motor.motor_asyncio.AsyncIOMotorClient(self.url)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except mg.errors.ConnectionFailure as e:
            print(f"Connection error: {e}")

    def _user_helper(self, user) -> dict:
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "password": user["password"]
        }

    def create_db(self, db: str) -> None:
        if db not in self.client.list_database_names():
            self.client[db]
            print(f"Database {db} created")

    def create_collection(self, collection: str) -> None:
        if collection not in self.db.list_collection_names():
            self.db.create_collection(collection)
            print(f"Collection {collection} created")

    async def create_user(self, user: dict) -> dict:
        return self.collection.insert_one(user)

    async def get_user_by_id(self, id: str) -> dict:
        user = await self.collection.find_one({"_id": ObjectId(id)})
        if user:
            return self._user_helper(user)

    async def update_user(self, id: str, data: dict) -> bool:
        if len(data) < 1:
            return False
        user = await self.collection.find_one({"_id": ObjectId(id)})
        if user:
            updated_user = await self.collection.update_one(
                {"_id": ObjectId(id)}, {"$set": data}
            )
            if updated_user:
                return True
            return False

    async def delete_user(self, id: str) -> bool:
        user = await self.collection.find_one({"_id": ObjectId(id)})
        if user:
            await self.collection.delete_one({"_id": ObjectId(id)})
            return True

    async def get_userid_by_mail(self, email: str) -> dict:
        user = await self.collection.find_one({"email": email})
        if user:
            return str(user["_id"])
    
    async def get_user_list(self) -> list:
        users = []
        async for user in self.collection.find():
            users.append(self._user_helper(user))
        return users

if __name__ == "__main__":
    pass