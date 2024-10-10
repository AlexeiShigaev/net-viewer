from app.database.mongo_motor import MongoMotorEngine
from app.settings import settings


motorchik = MongoMotorEngine(
            connection_uri="mongodb://{}:{}@{}:{}".format(
                settings.DB_USER, settings.DB_PASSWORD,
                settings.DB_HOST, settings.DB_PORT
            ),
            database="macfinder"
        )
