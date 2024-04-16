import os

from dotenv.main import load_dotenv

load_dotenv()

# Logs
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
LOG_FILE_NAME = os.environ.get('LOG_FILE_NAME', 'app')

# Mongo
MONGO_URI = os.environ.get('MONGO_URI')
