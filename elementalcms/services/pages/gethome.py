import os
import json

from elementalcms.persistence.repositories import GlobalDepsRepository, PagesRepository, DraftsRepository
from elementalcms.services import UseCaseResult, NoResult, Success
from elementalcms.core import MongoDbContext


class GetHome:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, draft=False, add_gloabl_deps=True, design_mode_opts=None) -> UseCaseResult:
        if draft:
            repo = DraftsRepository(self.__db_context)
        else:
            repo = PagesRepository(self.__db_context)

        if not design_mode_opts:
            result = repo.find({'isHome': True}, page=0, page_size=10)
            if result['total'] == 0:
                return NoResult()

        else:
            languages = design_mode_opts.get('languages')
            pages_folder = design_mode_opts.get('pages_folder')

            home_filename = None
            for filename in os.listdir(f'{pages_folder}/{languages[0]}/'):
                if not filename.endswith('.json'):
                    continue
                with open(f'{pages_folder}/{languages[0]}/{filename}') as f:
                    content_as_json = json.loads(f.read())
                    if content_as_json.get('isHome', False):
                        home_filename = content_as_json.get('name')
                        break

            if home_filename is None:
                return NoResult()

            items = []
            for lang in languages:
                with open(f'{pages_folder}/{lang}/{home_filename}.html') as html_file:
                    html_content = html_file.read()
                with open(f'{pages_folder}/{lang}/{home_filename}.json') as spec_file:
                    spec_content = spec_file.read()
                spec = json.loads(spec_content)
                spec['content'] = html_content
                items.append(spec)

            result = dict(items=items, total=len(items))

        pages = {}
        if add_gloabl_deps:
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
