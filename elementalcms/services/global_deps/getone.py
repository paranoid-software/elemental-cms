from elementalcms.persistence.repositories import GlobalDepsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id) -> UseCaseResult:
        repo = GlobalDepsRepository(self.__db_context)
        dep = repo.find_one(_id)
        if dep is None:
            return NoResult()
        return Success(dep)
