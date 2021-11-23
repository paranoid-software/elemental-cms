from elementalcms.persistence.repositories import GlobalDepsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetAll:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self) -> UseCaseResult:
        repo = GlobalDepsRepository(self.__db_context)
        pages = []
        page = 0
        page_size = 50
        while True:
            result = repo.find({}, page, page_size)
            total = result['total']
            if total == 0:
                return NoResult()
            pages.extend(result['items'])
            if len(pages) >= total:
                break
            page += 1
        return Success(pages)
