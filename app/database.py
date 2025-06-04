from typing import Optional
from tenacity import retry, stop_after_attempt, wait_fixed

import databases
import sqlalchemy
import ormar

try:
    import config
except: 
    import app.config as config


#default value
_database_url = config.DATABASE_URL

database = databases.Database(_database_url)
metadata = sqlalchemy.MetaData()

base_ormar_config = ormar.OrmarConfig(
    metadata = metadata,
    database = database
)



def __change_db(url: str):
    _database = databases.Database(url)


@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
async def connect_database(database_url: Optional[str] = None):
    """
    Method for connecting to database

    Accepts database url in format:\n
    connector://user:password@host:port/database_name
    """
    if database_url:
        __change_db(database_url)
    engine = sqlalchemy.create_engine(database_url or _database_url)
    print('> engine create')
    base_ormar_config.metadata.create_all(engine)

    print('> all create')
    database_ = base_ormar_config.database
    if not database_.is_connected:
        await database_.connect()
        print('> connected')



async def disconnect_database():
    """
    Method for disconnecting from database
    """
    if base_ormar_config.database.is_connected:
        await base_ormar_config.database.disconnect()
