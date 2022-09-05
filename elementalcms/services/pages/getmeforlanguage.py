from elementalcms.persistence.repositories import GlobalDepsRepository, PagesRepository, DraftsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetMeForLanguage:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, name, language, draft=False, add_global_deps=True) -> UseCaseResult:
        if draft:
            repo = DraftsRepository(self.__db_context)
        else:
            repo = PagesRepository(self.__db_context)
        page = 0
        page_size = 100
        result = repo.find({'name': name, 'language': language}, page=page, page_size=page_size)
        if result['total'] == 0:
            return NoResult()
        page = result['items'][0]
        if add_global_deps:
            global_deps = self.get_all_global_deps()
            css_deps = [d for d in global_deps if d['type'] == 'text/css']
            page['cssDeps'] = css_deps + page['cssDeps']
            js_deps = [d for d in global_deps if d['type'] == 'application/javascript']
            page['jsDeps'] = js_deps + page['jsDeps']
        return Success(page)

    def get_all_global_deps(self):
        repo = GlobalDepsRepository(self.__db_context)
        all_deps = []
        page = 0
        page_size = 50
        while True:
            result = repo.find(sort={'type': 1, 'order': 1}, page=page, page_size=page_size)
            total = result['total']
            if total == 0:
                return []
            all_deps.extend(result['items'])
            if len(all_deps) >= total:
                break
            page += 1
        return all_deps
