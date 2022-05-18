class MongoDbContext(object):

    def __init__(self, settings: dict):
        self.id = settings['id']
        self.host_name = settings['hostName']
        self.port_number = settings['portNumber']
        self.database_name = settings['databaseName']
        self.username = settings['username']
        self.password = settings['password']
        self.direct_connection = settings.get('directConnection', True)

    def get_connection_string(self) -> str:
        user_info_parts = []
        if self.username:
            user_info_parts.append(self.username)
        if self.password:
            user_info_parts.append(self.password)
        user_info = str.join(':', user_info_parts)
        if self.direct_connection:
            return f'mongodb://{user_info}{"@" if user_info else ""}{self.host_name}:{self.port_number}/?directConnection=true'
        return f'mongodb://{user_info}{"@" if user_info else ""}{self.host_name}:{self.port_number}'
