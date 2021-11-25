from elementalcms.persistence.repositories import SessionsRepository
from elementalcms.services import UseCaseResult, Success
from elementalcms.core import MongoDbContext


class CreateExpirationIndex:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self) -> UseCaseResult:
        repo = SessionsRepository(self.__db_context)
        repo.create_expiration_index()
        return Success(True)
