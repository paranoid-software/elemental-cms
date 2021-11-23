import pymongo
from bson import ObjectId

from elementalcms.persistence import MongoDbConnectionManager

from elementalcms.core import MongoDbContext


class GlobalDepsRepository(MongoDbConnectionManager):

    def __init__(self, db_context: MongoDbContext):
        self.__coll = self._get_db(db_context).get_collection('global_deps')

    def find_one(self, _id):
        if not ObjectId.is_valid(_id):
            return None
        find_one_result = self.__coll.find_one({'_id': ObjectId(_id)})
        return find_one_result

    def delete_one(self, _id):
        if not ObjectId.is_valid(_id):
            return None
        delete_one_result = self.__coll.delete_one({'_id': ObjectId(_id)})
        return delete_one_result.deleted_count == 1

    def update(self, _id, page, upsert=True) -> bool:
        if not ObjectId.is_valid(_id):
            return False
        update_result = self.__coll.replace_one({'_id': ObjectId(_id)}, page, upsert=upsert)
        return update_result.modified_count == 1

    def find(self, query, page, page_size):

        result = {
            'items': [],
            'total': 0
        }

        cursor = self.__coll.aggregate([{
            '$facet': {
                'data': [
                    {'$match': query},
                    {'$sort': {'type': 1, 'order': 1}},
                    {'$skip': page * page_size},
                    {'$limit': page_size}
                ],
                'total': [
                    {'$match': query},
                    {'$sort': {'type': 1, 'order': 1}},
                    {'$count': 'total'}
                ]
            }
        }])

        aggregate_result = list(cursor)
        if len(aggregate_result) == 0:
            return result

        response = aggregate_result[0]
        for doc in response['data']:
            result['items'].append(doc)

        result['total'] = 0 if len(response['total']) == 0 else response['total'][0]['total']

        return result
