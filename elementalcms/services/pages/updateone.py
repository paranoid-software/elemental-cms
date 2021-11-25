import datetime
from elementalcms.persistence.repositories import PagesRepository, DraftsRepository
from elementalcms.services import UseCaseResult, Success
from elementalcms.core import MongoDbContext


class UpdateOne:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, _id, page, draft=False) -> UseCaseResult:
        if draft:
            repo = DraftsRepository(self.__db_context)
        else:
            repo = PagesRepository(self.__db_context)
        if '_id' in page:
            del page['_id']
        page['lastModifiedAt'] = datetime.datetime.utcnow()
        success = repo.replace_one(_id, page, True)
        return Success(success)
