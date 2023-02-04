class MongoDbContext(object):

    def __init__(self, settings: dict):
        self.id = settings.get('id')
        self.connection_string = settings.get('connectionString')
        self.database_name = settings.get('databaseName')
