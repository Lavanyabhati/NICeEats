from datetime import datetime
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt

from helpers.dbhelper import DBOperation
import random
from configuration import *


class Restaurant:
    def __init__(self):
        self.db = DBOperation(DB_NAME)
        self.db_res = DBOperation(COLLECTION_PROFILE_RESTAURANT)
        self.db_res_owner = DBOperation(COLLECTION_PROFILE_RESTAURANT_OWNER)
        self.db_res_menu = DBOperation(COLLECTION_RES_MENU)
        self.db_item_rating = DBOperation(COLLECTION_RATING)

    def _find(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "Restaurant._find()"
        try:
            profile_user = self.db_res._find_one(
                filter={
                    'mobile_number': mobile_number
                }
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

    def _add(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            res_name = data.get('name')
            category = data.get('category')
            location_name = data.get('location_name')
            location_lat = data.get('latitude')
            location_long = data.get('longitude')
            food_type = data.get('food_type')
            operating_hours = data.get('operating_hours')
            subcategory = data.get('subcategory')

            data_dict = {
                'unique_id': unique_id,
                'name': res_name,
                'category': category,
                'location_name': location_name,
                'location': {
                    'type': 'Point',
                    'coordinates': [float(location_long), float(location_lat)]
                },
                'food_type': food_type,
                'operating_hours': operating_hours,
                'subcategory': subcategory,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_res = self.db_res._insert(data_dict)
            return True if insert_res.inserted_id else False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _add_owner_details(self, LOG_PREFIX, data):
        try:
            mobile_number = data.get('mobile_number')
            unique_id = data.get('unique_id')

            name = data.get('name', '')
            address = data.get('address', '')
            email = data.get('email', '')
            date_of_birth = data.get('date_of_birth', '')
            gender = data.get('gender', '')
            verification_id = data.get('verification_id', '')
            verification_type = data.get('verification_type', '')


            filter_data = {
                'mobile_number': mobile_number,
                'unique_id': unique_id
            }
            rest_document = {
                'name': name,
                'address': address,
                'email': email,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'profile_type': 'OWNER',
                'verification_id': verification_id,
                'verification_type': verification_type,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_res_owner = self.db_res_owner._insert(upsert_filter=filter_data, data=rest_document)

            print("Restaurant profile saved successfully!")
            return True if insert_res_owner.inserted_id else False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _update_owner_details(self, LOG_PREFIX, data):
        try:
            mobile_number = data.get('mobile_number')
            unique_id = data.get('unique_id')

            name = data.get('name', '')
            address = data.get('address', '')
            email = data.get('email', '')
            date_of_birth = data.get('date_of_birth', '')
            gender = data.get('gender', '')
            verification_id = data.get('verification_id', '')
            verification_type = data.get('verification_type', '')

            filter_data = {
                'mobile_number': mobile_number,
                'unique_id': unique_id
            }
            update_data = {
                'name': name,
                'address': address,
                'email': email,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'profile_type': 'OWNER',
                'verification_id': verification_id,
                'verification_type': verification_type,
                'updated_at': datetime.now(),
            }

            update_res_owner = self.db_res_owner._update(filter_q=filter_data, update_data=update_data, upsert=True)

            if update_res_owner.modified_count > 0:
                print("Restaurant profile updated successfully!")
                return True
            else:
                return False

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return {"status": "FAILURE", "message": "Error updating owner details"}

    def _details(self, LOG_PREFIX, unique_id):
        try:
            data_dict = {
                'unique_id': unique_id,
            }
            log.info("DBRES ::: %s" %self.db_res_menu.coll_name)
            res_details = self.db_res._find_one(filter=data_dict)
            return res_details

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def get_restaurant_rating(self, LOG_PREFIX, unique_id):
        try:
            query = {'unique_id': unique_id}
            items_list = self.db_res_menu._find_all(query)

            total_rating = 0
            total_items = 0

            for item in items_list:
                item_id = item.get('item_id')
                rating_info = self.db_item_rating._find_one({'item_id': item_id}, remove_ts=True)
                logging.info("RATING INFO::: %s" % rating_info)

                if isinstance(rating_info, dict):
                    res_rating = rating_info.get('avg_rating', 0)
                    no_of_ratings = rating_info.get('no_of_ratings', 0)

                    total_rating += res_rating * no_of_ratings
                    total_items += no_of_ratings

            if total_items == 0:
                return 0

            restaurant_rating = total_rating / total_items
            restaurant_rating = round(restaurant_rating, 1)

            return restaurant_rating

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _list(self, LOG_PREFIX, data):
        try:
            lat = data.get('latitude')
            long = data.get('longitude')
            max_distance = data.get('max_distance', 5000)  # Default to 5km

            query = {
                'location': {
                    '$near': {
                        '$geometry': {
                            'type': 'Point',
                            'coordinates': [float(long), float(lat)]
                        },
                        '$maxDistance': int(max_distance)
                    }
                }
            }
            log.info("QUERY :: %s" %query)
            res_list = self.db_res._find_all(filter=query, sort_ts=True)
            log.info("COLLECTION : %s" %self.db_res.coll_name)
            return res_list

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _update_db(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            res_name = data.get('name')
            location_name = data.get('location_name')
            category = data.get('category')
            location_lat = data.get('location_lat')
            location_long = data.get('location_long')
            food_type = data.get('food_type')
            operating_hours = data.get('operating_hours')
            subcategory = data.get('subcategory')

            filter_data = {
                'unique_id': unique_id
            }

            update_data = {
                'name': res_name,
                'location_name': location_name,
                'category': category,
                'location': {
                    'type': 'Point',
                    'coordinates': [float(location_long), float(location_lat)]
                },
                'food_type': food_type,
                'operating_hours': operating_hours,
                'subcategory': subcategory,
                'updated_at': datetime.now(),
            }
            res_update = self.db_res._update(filter_q=filter_data, update_data=update_data, upsert=True)
            return res_update.modified_count > 0
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _delete(self, LOG_PREFIX, unique_id, data):
        try:
            unique_id = data.get('unique_id')

            filter_data = {
                'unique_id': unique_id
            }

            res_delete = self.db_res._delete(filter_d=filter_data, multiple=False)

            if res_delete and res_delete.deleted_count > 0:
                self.db_res_owner._delete(filter_d=filter_data, multiple=True)
                self.db_res_menu._delete(filter_d=filter_data, multiple=True)
                return True

        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False



class Menu:
    def __init__(self):
        self.db_res_menu = DBOperation(COLLECTION_RES_MENU)
        self.db_item_rating = DBOperation(COLLECTION_RATING)

    def _add_menu(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            item_id = data.get('item_id')
            item_name = data.get('item_name')
            item_description = data.get('item_description')
            item_price = data.get('item_price')
            item_category = data.get('item_category')
            item_type = data.get('item_type')

            data_dict = {
                'unique_id': unique_id,
                'item_id': item_id,
                'item_name': item_name,
                'item_description': item_description,
                'item_price': item_price,
                'item_category': item_category,
                'item_type': item_type,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }

            insert_menu_item = self.db_res_menu._insert(data=data_dict)
            return True if insert_menu_item.inserted_id else False
        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _update_menu(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            item_id = data.get('item_id')
            item_name = data.get('item_name')
            item_description = data.get('item_description')
            item_price = data.get('item_price')
            item_category = data.get('item_category')
            item_type = data.get('item_type')

            filter_data = {
                'unique_id': unique_id,
                'item_id': item_id
            }

            update_data = {
                'unique_id': unique_id,
                'item_id': item_id,
                'item_name': item_name,
                'item_description': item_description,
                'item_price': item_price,
                'item_category': item_category,
                'item_type': item_type,
                'updated_at': datetime.now(),
            }

            update_menu_item = self.db_res_menu._update(filter_q=filter_data, update_data=update_data, upsert=False)
            return update_menu_item.modified_count > 0
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def item_list(self, LOG_PREFIX, unique_id):
        try:
            query = {
                'unique_id': unique_id
            }
            log.info("QUERY :: %s" % query)
            items_list = self.db_res_menu._find_all(filter=query, sort_ts=True)
            log.info("COLLECTION : %s" % self.db_res_menu.coll_name)

            for item in items_list:
                item_id = item.get('item_id')
                rating_info = self.db_item_rating._find_one({'item_id': item_id}, {'avg_rating': 1, 'no_of_ratings': 1})

                if rating_info:
                    item['avg_rating'] = rating_info.get('avg_rating', 0)
                    item['no_of_ratings'] = rating_info.get('no_of_ratings', 0)
                else:
                    item['avg_rating'] = 0
                    item['no_of_ratings'] = 0

            return items_list

        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _delete_item(self, LOG_PREFIX, item_id):
        try:
            filter_data = {
                'item_id': item_id
            }

            item_delete = self.db_res_menu._delete(filter_d=filter_data, multiple=False)

            if item_delete and item_delete.deleted_count > 0:
                return True
            else:
                return False

        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False

    def _rate_item(self, LOG_PREFIX, data):
        try:
            item_id = data.get('item_id')
            item_rating = data.get('item_rating')

            item = self.db_item_rating._find_one({'item_id': item_id})

            if item:
                new_no_of_ratings = item.get('no_of_ratings', 0) + 1
                new_avg_rating = ((item.get('avg_rating', 0) * item.get('no_of_ratings',
                                                                        0)) + item_rating) / new_no_of_ratings

                new_avg_rating = round(new_avg_rating, 1)

                filter_data = {
                    'item_id': item_id
                }
                update_data = {
                    'avg_rating': new_avg_rating,
                    'no_of_ratings': new_no_of_ratings,
                    'updated_at': datetime.now()
                }
                self.db_item_rating._update(filter_q=filter_data, update_data=update_data)
            else:
                data_dict = {
                    'item_id': item_id,
                    'avg_rating': item_rating,
                    'no_of_ratings': 1,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                }
                self.db_item_rating._insert(data=data_dict)

            return True
        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def update_item_rating(self, LOG_PREFIX, data):
        try:
            item_id = data.get('item_id')
            old_rating = data.get('old_rating')
            new_rating = data.get('new_rating')

            item = self.db_item_rating._find_one({'item_id': item_id})

            if item:
                no_of_ratings = item.get('no_of_ratings', 0)
                avg_rating = item.get('avg_rating', 0)

                if no_of_ratings <= 1:
                    new_avg_rating = new_rating
                else:
                    total_rating = avg_rating * no_of_ratings
                    total_rating = total_rating - old_rating + new_rating
                    new_avg_rating = total_rating / no_of_ratings

                new_avg_rating = round(new_avg_rating, 1)

                filter_data = {
                    'item_id': item_id
                }
                update_data = {
                    'avg_rating': new_avg_rating,
                    'updated_at': datetime.now()
                }
                self.db_item_rating._update(filter_q=filter_data, update_data=update_data)
            else:
                return False
            return True
        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None
