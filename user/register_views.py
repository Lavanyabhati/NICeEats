from datetime import datetime
from configuration import *
from helpers.dbhelper import DBOperation


class Register:
    def __init__(self):
        # self.db = db_conn()
        # self.collection = 'profile_user'
        self.db = DBOperation(COLLECTION_PROFILE)

    def _find(self, LOG_PREFIX, mobile_number):
        # db = self.db
        # collection = self.collection
        success = False
        ACTION = "Register._find()"
        try:
            profile_user = self.db._find_one(
                filter={'mobile_number': mobile_number}
            )
            if profile_user:
                log.info(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Success"')
                success = True
                return success, profile_user
            log.info(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"DataNotFound"')
            return success, None

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"{e}"')
            return success, None

    def _add(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "Register._add()"
        try:
            insert_data = {
                'mobile_number': mobile_number
            }
            insert_user = self.db._insert(data=insert_data)
            if insert_user.inserted_id:
                success = True
                log.info(
                    f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Success"')
                return success
            log.info(
                f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"InsertFailure"')
            return success
        except Exception as e:
            log.error(
                f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"{e}"')
            return success

    def _update(self, data, mobile_number):
        db = self.db
        collection = self.collection
        try:
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            age = data.get('age')
            address = data.get('address')

            data_dict = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'age': age,
                'address': address,
                'updated_at': datetime.now()
            }

            update_user = db[collection].update_one({'mobile_number':mobile_number}, {'$set': data_dict})
            if update_user.modified_count>0:
                print("The user profile is updated.")
                # update user will return 1 - to denote the number of records modified
                return True
            else:
                print("The user profile couldn't be updated.")
                return False

        except Exception as e:
            print("Exception in Register._add(). Reason : %s" %e)
            return None



    def _delete(self, mobile_number):
        db = self.db
        collection = self.collection
        try:
            delete_user = db[collection].delete_one({'mobile_number': mobile_number})

            if delete_user.deleted_count>0:
                # implies, one user record has been deleted
                print('User profile deleted!')
                return True
            else:
                print("User profile couldn't be deleted ")
                return False

        except Exception as e:
            print(f"Exception in _delete: {e}")
            return False






