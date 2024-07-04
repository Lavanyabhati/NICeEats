from configuration import *


class DBOperation:
    def __init__(self, collection):
        self.db = db_conn()
        self.coll_name = collection

    def _count(self, filter, limit=None):
        try:
            db = self.db
            if limit:
                countdoc = db[self.coll_name].count_documents(filter, limit=limit)
            else:
                countdoc = db[self.coll_name].count_documents(filter)
            return countdoc
        except Exception as e:
            log.error("Exception in DBOperation.CountDocuments(). Reason:%s" % e)
            return None

    def _find_all(self, filter, sort_ts=None, remove_ts=None, sort_by=None, sortby_withid=None, required_keys=None):
        try:
            db = self.db
            if sortby_withid:
                find = list(db[self.coll_name].find(filter).sort(sortby_withid, -1))
            elif sort_by:
                find = list(db[self.coll_name].find(filter, {'_id': False}).sort(sort_by, -1))
            elif sort_ts:
                find = list(db[self.coll_name].find(filter, {'_id': False}).sort('created_at', -1))
            elif remove_ts:
                find = list(db[self.coll_name].find(filter, {'_id': False, 'created_at': False, 'updated_at': False}))
            elif required_keys:
                required = {k:True for k in required_keys}
                required.update({'_id': False})
                find = list(db[self.coll_name].find(filter, required))
            else:
                find = list(db[self.coll_name].find(filter, {'_id': False}))
            return find
        except Exception as e:
            log.error("Exception in DBOperation.Find(). Reason:%s" % e)
            return None

    def _find_one(self, filter, remove_ts=None):
        try:
            db = self.db
            if remove_ts:
                find = db[self.coll_name].find_one(filter, {'_id': False, 'created_at': False, 'updated_at': False})
            else:
                find = db[self.coll_name].find_one(filter, {'_id': False})
            return find
        except Exception as e:
            log.error("Exception in DBOperation.FindOne(). Reason:%s" % e)
            return None

    def _insert(self, data, upsert_filter=None):
        try:
            db = self.db
            if upsert_filter:
                insert = db[self.coll_name].update_one(upsert_filter, {'$set': data}, upsert=True)
            else:
                insert = db[self.coll_name].insert_one(data)
            return insert
        except Exception as e:
            log.error("Exception in DBOperation.Insert(). Reason:%s" % e)
            return None

    def _update(self, filter_q, update_data, upsert=None, multi_ops=None):
        try:
            db = self.db
            if multi_ops:
                update = db[self.coll_name].update_one(filter_q, update_data)
            elif upsert:
                update_q = {"$set": update_data}
                update = db[self.coll_name].update_one(filter_q, update_q, upsert=upsert)
            else:
                update_q = {"$set": update_data}
                update = db[self.coll_name].update_one(filter_q, update_q)
            return update
        except Exception as e:
            log.error("Exception in DBOperation.Update(). Reason:%s" % e)
            return None

    def _update_many(self, filter_q, update_data):
        try:
            db = self.db
            update_q = {"$set": update_data}
            update_many = db[self.coll_name].update_many(filter_q, update_q)
            return update_many
        except Exception as e:
            log.error("Exception in DBOperation.UpdateMany(). Reason:%s" % e)
            return None

    def _delete(self, filter_d, multiple=None):
        try:
            db = self.db
            if multiple:
                delete = db[self.coll_name].delete_many(filter_d)
            else:
                delete = db[self.coll_name].delete_one(filter_d)
            return delete
        except Exception as e:
            log.error("Exception in DBOperation.Delete(). Reason:%s" % e)
            return None