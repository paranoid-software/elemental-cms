from bson import ObjectId

from elementalcms.persistence import MongoDbConnectionManager
from elementalcms.core import MongoDbContext


class GenericRepository(MongoDbConnectionManager):

    def __init__(self, db_context: MongoDbContext, coll_name: str):
        self._coll = self._get_db(db_context).get_collection(coll_name)

    def find_one(self, _id):
        if not ObjectId.is_valid(_id):
            return None
        find_one_result = self._coll.find_one({'_id': ObjectId(_id)})
        return find_one_result

    def delete_one(self, _id) -> bool:
        if not ObjectId.is_valid(_id):
            return False
        delete_one_result = self._coll.delete_one({'_id': ObjectId(_id)})
        return delete_one_result.deleted_count == 1

    def insert_one(self, payload) -> str:
        insert_result = self._coll.insert_one(payload)
        return str(insert_result.inserted_id)

    def replace_one(self, _id, spec, upsert=True) -> bool:
        if not ObjectId.is_valid(_id):
            return False
        update_result = self._coll.replace_one({'_id': ObjectId(_id)}, spec, upsert=upsert)
        return update_result.raw_result['n'] == 1 or update_result.modified_count == 1

    def find(self, query=None, sort=None, page=0, page_size=10):

        result = {
            'items': [],
            'total': 0
        }

        data = [
                    {'$match': query if query else {}},
                    {'$skip': page * page_size},
                    {'$limit': page_size}
                ]
        total = [
                    {'$match': query if query else {}},
                    {'$count': 'total'}
                ]

        if sort:
            data.append({
                '$sort': sort
            })
            total.append({
                '$sort': sort
            })

        cursor = self._coll.aggregate([{
            '$facet': {
                'data': data,
                'total': total
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
