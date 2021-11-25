from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetAll:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self) -> UseCaseResult:
        repo = SnippetsRepository(self.__db_context)
        snippets = []
        page = 0
        page_size = 50
        while True:
            result = repo.find(page=page, page_size=page_size)
            total = result['total']
            if total == 0:
                return NoResult()
            snippets.extend(result['items'])
            if len(snippets) >= total:
                break
            page += 1
        return Success(snippets)
