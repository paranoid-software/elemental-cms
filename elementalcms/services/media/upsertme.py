import datetime

from bson import ObjectId

from elementalcms.core import MongoDbContext
from elementalcms.persistence.repositories import MediaRepository
from elementalcms.services import UseCaseResult, NoResult, Success, Failure


class UpsertMe:
    __db_context: MongoDbContext

    def __init__(self, db_context: MongoDbContext):
        self.__db_context = db_context

    def execute(self, file_path) -> UseCaseResult:
        repo = MediaRepository(self.__db_context)
        find_result = repo.find({'filePath': file_path}, page=0, page_size=10)
        if find_result['total'] == 0:
            replace_one_result = repo.replace_one(ObjectId(), {
                'filePath': file_path,
                'createdAt': datetime.datetime.utcnow(),
                'lastModifiedAt': datetime.datetime.utcnow()
            }, True)
            return Success(replace_one_result)
        if find_result['total'] > 1:
            return Failure({'duplicatedMedia': True})
        media = find_result['items'][0]
        _id = media['_id']
        del media['_id']
        media['lastModifiedAt'] = datetime.datetime.utcnow()
        replace_one_result = repo.replace_one(_id, media, True)
        return Success(replace_one_result)
