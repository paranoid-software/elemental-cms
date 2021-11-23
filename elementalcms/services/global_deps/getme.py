from elementalcms.persistence.repositories import GlobalDepsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, name, _type) -> UseCaseResult:
        repo = GlobalDepsRepository(self.__db_context)
        page = 0
        page_size = 100
        result = repo.find({'name': name, 'type': _type}, page, page_size)
        if result['total'] == 0:
            return NoResult()
        dep = result['items'][0]
        return Success(dep)
