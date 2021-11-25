from elementalcms.persistence.repositories import MediaRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetAll:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self) -> UseCaseResult:
        repo = MediaRepository(self.__db_context)
        media_files = []
        page = 0
        page_size = 50
        while True:
            result = repo.find(sort={'name': 1}, page=page, page_size=page_size)
            total = result['total']
            if total == 0:
                return NoResult()
            media_files.extend(result['items'])
            if len(media_files) >= total:
                break
            page += 1
        return Success(media_files)
