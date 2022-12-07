import json

from elementalcms.persistence.repositories import GlobalDepsRepository, PagesRepository, DraftsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, name, draft=False, add_global_deps=True, design_mode_opts=None) -> UseCaseResult:
        if draft:
            repo = DraftsRepository(self.__db_context)
        else:
            repo = PagesRepository(self.__db_context)

        if not design_mode_opts:
            page = 0
            page_size = 100
            result = repo.find({'name': name}, page=page, page_size=page_size)
            if result['total'] == 0:
                return NoResult()
        else:
            items = []
            languages = design_mode_opts.get('languages')
            pages_folder = design_mode_opts.get('pages_folder')
            for lang in languages:
                with open(f'{pages_folder}/{lang}/{name}.html') as html_file:
                    html_content = html_file.read()
                with open(f'{pages_folder}/{lang}/{name}.json') as spec_file:
                    spec_content = spec_file.read()
                spec = json.loads(spec_content)
                spec['content'] = html_content
                items.append(spec)

            result = dict(items=items, total=len(items))

        pages = {}
        if add_global_deps:
            global_deps = self.get_all_global_deps()
            css_deps = [d for d in global_deps if d['type'] == 'text/css']
            js_deps = [d for d in global_deps if d['type'] == 'application/javascript']
            for page in result['items']:
                if page['language'] not in pages:
                    pages[page['language']] = page
                pages[page['language']]['cssDeps'] = css_deps + pages[page['language']]['cssDeps']
                pages[page['language']]['jsDeps'] = js_deps + pages[page['language']]['jsDeps']
        return Success(pages)

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
