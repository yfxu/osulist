import os
from enum import Enum
from dotenv import load_dotenv, find_dotenv

# import env variables
load_dotenv( find_dotenv() )

APP_SECRET_KEY = os.getenv( 'APP_SECRET_KEY' )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )
OSU_CLIENT_ID = os.getenv( 'OSU_CLIENT_ID' )
OSU_CLIENT_SECRET = os.getenv( 'OSU_CLIENT_SECRET' )
OAUTH_STATE = os.getenv( 'OAUTH_STATE' )
MONGO_URI = os.getenv("MONGO_URI")


# enums
Sort = Enum( 'Sort', 'new old top' )
