from datetime import datetime
from configuration import *
from helpers.dbhelper import DBOperation
from rest.register_views import Menu
from django.http import JsonResponse
from helpers.dbhelper import DBOperation


class User:
    def __init__(self):
        self.db_user = DBOperation(COLLECTION_PROFILE_USER)


    def _find(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "Register._find()"
        try:
            profile_user = self.db_user._find_one(
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
            insert_user = self.db_user._insert(data=insert_data)
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
        db = self.db_user
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
        db = self.db_user
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



class Cart:

    def __init__(self):
        self.db_user = DBOperation(COLLECTION_CART)

    def add_to_cart(self,LOG_PREFIX,cart,user_id,item,item_id,item_quantity):
        if not cart:
            return self.create_newcart('LOG_PREFIX',user_id,item_id,item_quantity,item)

        else:
            return self.update_cartforadd('LOG_PREFIX',cart,user_id,item_id, item_quantity, item)


    def create_newcart(self,LOG_PREFIX,user_id,item_id,item_quantity,item):

        new_cart = {
            'userid': user_id,
            'res_id': item['unique_id'],
            'items': [{
                'item_id': item_id,
                'item_name': item['item_name'],
                'item_description': item['item_description'],
                'item_price': item['item_price'],
                'item_category': item['item_category'],
                'item_type': item['item_type'],
                'quantity': item_quantity
            }
            ]
        }
        self.db_user._insert(new_cart)
        return JsonResponse({'status':'SUCCESS','statuscode':'201','message': 'Cart created successfully'})

    def update_cartforadd(self,LOG_PREFIX,cart,user_id,item_id, item_quantity, item):

        cart_items = cart['items']
        log.info("cart items %s" % cart_items)
        item_exists = False
        for cart_item in cart_items:
            if cart_item['item_id'] == item_id:
                item_exists = True
                int_quantity = int(item_quantity)
                log.info("quantity given %s" % int_quantity)
                cart_quantity = int(cart_item['quantity'])
                cart_quantity += int_quantity
                item_p_add = int(item['item_price']) * cart_quantity
                cart_item['quantity'] = str(cart_quantity)
                cart_item['item_price'] = str(item_p_add)
                log.info("quantity given %s" % cart_item['quantity'])
                log.info("price addition %s" % cart_item['item_price'])

        if not item_exists:
            new_item = {
                    'item_id': item_id,
                    'item_name': item['item_name'],
                    'item_description': item['item_description'],
                    'item_price': item['item_price'],
                    'item_category': item['item_category'],
                    'item_type': item['item_type'],
                    'quantity': item_quantity
                }
            cart_items.append(new_item)

        self.db_user._update({'userid': user_id}, {'items': cart_items}, upsert=None, multi_ops=None)
        return JsonResponse({'status': 'SUCCESS', 'statuscode': '202', 'mssg': 'cart updated successfully'})




    def sub_from_cart(self, LOG_PREFIX, cart,user_id, item, item_id, item_quantity):

        if not cart:
            return JsonResponse({'status':'FAILURE','statuscode':'408','msg':'Cart is not there for reduction'})

        cart_items = cart['items']
        log.info("cart items %s" % cart_items)
        item_exists = False
        for cart_item in cart_items:
            if cart_item['item_id'] == item_id:
                item_exists = True
                int_quantity = int(item_quantity)
                log.info("quantity given %s" % int_quantity)
                cart_quantity = int(cart_item['quantity'])
                cart_quantity -= int_quantity
                item_p_sub = int(item['item_price']) * cart_quantity
                cart_item['quantity'] = str(cart_quantity)
                cart_item['item_price'] = str(item_p_sub)
                log.info("quantity remaining %s" % cart_item['quantity'])
                log.info("price subtraction %s" % cart_item['item_price'])
                if cart_item['quantity'] <= '0':
                    cart_items.remove(cart_item)

        if not cart_items:
            self.db_user._delete({'userid': user_id}, multiple=None)
            return JsonResponse({'status':'SUCCESS','statuscode':'203','mssg': 'cart deleted successfully'})

        self.db_user._update({'userid': user_id}, {'items': cart_items}, upsert=None, multi_ops=None)
        return JsonResponse({'status':'SUCCESS','statuscode':'202','mssg': 'cart updated successfully'})




