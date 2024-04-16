import motor.motor_asyncio
from app.server.config.config import MONGO_URI

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = mongo_client['kgp_mtp']
