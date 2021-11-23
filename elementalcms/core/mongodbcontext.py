class MongoDbContext(object):

    def __init__(self, settings: dict):
        self.id = settings['id']
        self.host_name = settings['hostName']
        self.port_number = settings['portNumber']
        self.database_name = settings['databaseName']
        self.username = settings['username']
        self.password = settings['password']

    def get_connection_string(self) -> str:
        return f'mongodb://{self.username}:{self.password}@{self.host_name}:{self.port_number}'
