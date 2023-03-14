import os
import json
from elementalcms.persistence.repositories import SnippetsRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure
from elementalcms.core import MongoDbContext


class GetMany:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, names, design_mode_opts=None) -> UseCaseResult:
        if not design_mode_opts:
            repo = SnippetsRepository(self.__db_context)
            result = repo.find({'name': { '$in': names }}, page=0, page_size=30)
            if result['total'] == 0:
                return NoResult()
        else:
            items = []
            snippets_folder = design_mode_opts.get('snippets_folder')
            if os.path.exists(snippets_folder):
                for filename in os.listdir(snippets_folder):
                    if filename == '.bak':
                        continue
                    if filename.endswith('.html'):
                        continue
                    with open(f'{snippets_folder}/{filename}', encoding='utf-8') as f:
                        item = json.loads(f.read())
                        if item.get('name') in names:
                            items.append(item)
            result = dict(items=items, total=len(items))
        return Success(result['items'])
