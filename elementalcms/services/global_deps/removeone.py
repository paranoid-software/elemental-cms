from elementalcms.persistence.repositories import GlobalDepsRepository
from elementalcms.services import UseCaseResult, Success
from elementalcms.core import MongoDbContext


class RemoveOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id) -> UseCaseResult:
        repo = GlobalDepsRepository(self.__db_context)
        success = repo.delete_one(_id)
        return Success(success)
