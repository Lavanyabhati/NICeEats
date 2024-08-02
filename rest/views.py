import json
from django.http import JsonResponse
from .forms import *
from .register_views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from configuration import *
from geopy.distance import geodesic
import math
from functools import wraps
from helpers.jwthelper import JWToken
import random


def verify_auth_token(func):
    cls_jwt = JWToken()

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            log.info("REQUEST HEADERS ::: %s" % request.headers)
            log.info("REQUEST META ::: %s" % request.META)
            authorization_token = request.headers.get('Authorization-Token')
            log.info("AuthorizationToken ::: %s" % authorization_token)
            if not authorization_token:
                return JsonResponse({"status": "FAILURE", "statuscode": 403, "msg": "Authorization token missing"})

            validate_success, token_data = cls_jwt._validate(authorization_token)
            log.info("ValidateRes :: %s" % validate_success)
            log.info("ValidateResData :: %s" % token_data)
            if not validate_success:
                error_msg = token_data.get('error', 'Unknown error')
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": f"Token validation failed: {error_msg}"})

            token_scope = token_data.get('scope')
            if token_scope not in (TOKEN_SCOPE_USER, TOKEN_SCOPE_RESTAURANT):
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Invalid Scope!"})

            mobile_number = token_data.get('contact')
            unique_id = token_data.get('unique_id')

            kwargs['mobile_number'] = mobile_number
            kwargs['unique_id'] = unique_id

            log.info("KWARGS :: %s" % kwargs)

            return func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": f"Internal Server Error: {e}"})
    return wrapper


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def register_res(request, *args, **kwargs):
    EVENT = "AddRestaurant"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Restaurant()
    try:

        decoded_body = json.loads((request.body).decode())
        form = RegisterRestaurantForm(decoded_body)

        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})

        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        data_dict = {
                'unique_id': unique_id,
                'name': decoded_body.get('name'),
                'category': decoded_body.get('category'),
                'location_name': decoded_body.get('location_name'),
                'latitude': decoded_body.get('latitude'),
                'longitude': decoded_body.get('longitude'),
                'food_type': decoded_body.get('food_type'),
                'operating_hours': decoded_body.get('operating_hours'),
                'subcategory': decoded_body.get('subcategory')
        }

        insert_res = cls_register._aduid(LOG_PREFIX, data=data_dict)
        log.info("INSERT RES :%s" %insert_res)

        if insert_res:
            cls_register._update_owner_status(unique_id=unique_id, status=2)
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant registered successfully!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
def register_res_owner(request):
    cls_register = Restaurant()
    EVENT = "AddResOwnerProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = RegisterRestaurantOwnerForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        insert_res_owner = cls_register._add_owner_details(LOG_PREFIX, data=decoded_body)

        if insert_res_owner:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant registered successfully!"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_res_owner(request, *args, **kwargs):
    cls_register = Restaurant()
    EVENT = "UpdateResOwnerProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = UpdateRestaurantOwnerForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_res_owner : %s" %kwargs)

        mobile_number = kwargs.get('mobile_number')
        unique_id = kwargs.get('unique_id')
        if not mobile_number or not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Mobile number and unique ID are required"})

        update_data = {
            'unique_id': unique_id,
            'mobile_number': mobile_number,
            'name': decoded_body.get('name', ''),
            'address': decoded_body.get('address', ''),
            'email': decoded_body.get('email', ''),
            'date_of_birth': decoded_body.get('date_of_birth', ''),
            'gender': decoded_body.get('gender', ''),
            'verification_id': decoded_body.get('verification_id', ''),
            'verification_type': decoded_body.get('verification_type', ''),
        }

        res_owner_update = cls_register._update_owner_details(LOG_PREFIX, data=update_data)
        log.info("RES OWNER UPDATE :%s" %res_owner_update)
        if res_owner_update:
            cls_register._update_owner_status(unique_id=unique_id, status=1)
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant owner updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update restaurant owner!"})

    except Exception as e:
        print(f"Exception in update_res_owner(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def list_res(request, *args, **kwargs):
    cls_register = Restaurant()
    EVENT = "ListRestaurants"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = RestaurantListForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        data = {}
        data['latitude'] = decoded_body.get('latitude')
        data['longitude'] = decoded_body.get('longitude')
        data['max_distance'] = decoded_body.get('max_distance')

        res_list = cls_register._list(LOG_PREFIX, data=data)
        log.info("RES LIST:%s" % res_list)

        if res_list:
            for res in res_list:
                origin = (float(decoded_body.get('longitude')), float(decoded_body.get('latitude')))
                dist = (res['location']['coordinates'][0], res['location']['coordinates'][1])
                aerial_dist = math.ceil(geodesic(dist, origin).kilometers)
                res['distance'] = aerial_dist
                res['delivery_time'] = f'{(aerial_dist * 7) + 20}-{(aerial_dist * 10) + 20} Mins'

                restaurant_rating = cls_register.get_restaurant_rating(LOG_PREFIX, res['unique_id'])
                res['restaurant_rating'] = restaurant_rating if restaurant_rating is not None else "Rating not available"

        return JsonResponse({
            "status": "SUCCESS",
            "statuscode": 200,
            "msg": "Restaurants listed successfully!",
            "restaurants": res_list
        })

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_res(request, *args, **kwargs):
    cls_register = Restaurant()
    EVENT = "UpdateResProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        log.info("In Here...")
        decoded_body = json.loads((request.body).decode())
        form = RestaurantUpdateForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})
        log.info("KWARGS in update_res : %s" % kwargs)

        unique_id = kwargs.get('unique_id')

        update_data = {
            'unique_id': unique_id,
            'name': decoded_body.get('name', ''),
            'location_name': decoded_body.get('location_name', ''),
            'category': decoded_body.get('category', ''),
            'location_long': decoded_body.get('longitude'),
            'location_lat': decoded_body.get('latitude'),
            'food_type': decoded_body.get('food_type'),
            'operating_hours': decoded_body.get('operating_hours'),
            'subcategory': decoded_body.get('subcategory')
        }
        log.info("update_data :%s" % update_data)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        res_update = cls_register._update_db(LOG_PREFIX, data=update_data)

        log.info("RES UPDATE :%s" % res_update)

        if res_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update restaurant!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def delete_res(request, *args, **kwargs):
    cls_register = Restaurant()
    EVENT = "DeleteRes"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)
        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        data = {'unique_id': unique_id}

        res_delete = cls_register._delete(LOG_PREFIX, unique_id, data)
        log.info("RES DELETE :%s" %res_delete)

        if res_delete:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant deleted successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to delete restaurant!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["GET"])
@verify_auth_token
def get_res(request, *args, **kwargs):
    EVENT = "GetResDetails"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Restaurant()
    try:
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)
        res_details = cls_register._res_details(LOG_PREFIX, unique_id)
        log.info("GET RES DETAILS :%s" % res_details)

        if res_details:
            subcategory = res_details.get('subcategory', '')
            subcategory_list = [subcat.strip() for subcat in subcategory.split(',') if subcat]
            res_details['subcategory_list'] = subcategory_list

            restaurant_rating = cls_register.get_restaurant_rating(LOG_PREFIX, unique_id)
            log.info("RESTAURANT RATING :%s" % restaurant_rating)
            res_details['restaurant_rating'] = restaurant_rating

            return JsonResponse(
                {"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant details", "data": res_details})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Restaurant not found"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["GET"])
@verify_auth_token
def get_res_owner(request, *args, **kwargs):
    EVENT = "GetResOwnerDetails"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Restaurant()

    try:
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)
        res_owner_details = cls_register._res_owner_details(LOG_PREFIX, unique_id)
        log.info("GET RES OWNER DETAILS :%s" % res_owner_details)

        if res_owner_details:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant details", "data": res_owner_details})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Restaurant not found"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def add_item(request, *args, **kwargs):
    EVENT = "AddMenuItem"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()
    cls_res = Restaurant()
    try:
        decoded_body = json.loads((request.body).decode())

        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        res_details = cls_res._res_details(LOG_PREFIX, unique_id)
        log.info("GET RES DETAILS :%s" % res_details)

        if res_details:
            subcategory = res_details.get('subcategory', '')
            subcategory_list = [subcat.strip() for subcat in subcategory.split(',') if subcat]
            res_details['subcategory_list'] = subcategory_list

            form = MenuForm(decoded_body, subcategory_list=subcategory_list)
            if not form.is_valid():
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

            item_id = ''.join(random.choices('0123456789ABCDEF', k=16))
            data_dict = {
                'unique_id': unique_id,
                'item_id': item_id,
                'item_name': decoded_body.get('item_name'),
                'item_description': decoded_body.get('item_description'),
                'item_price': decoded_body.get('item_price'),
                'item_category': decoded_body.get('item_category'),
                'item_type': decoded_body.get('item_type')
            }

            insert_menu_item = cls_register._add_menu(LOG_PREFIX, data=data_dict)
            log.info("INSERT MENU ITEM :%s" % insert_menu_item)

            if insert_menu_item:
                cls_res._update_owner_status(unique_id=unique_id, status=3)
                return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Menu item added successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Restaurant not found"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_item(request, *args, **kwargs):
    EVENT = "UpdateMenuItem"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()
    cls_res = Restaurant()

    try:
        decoded_body = json.loads((request.body).decode())
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID : %s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        res_details = cls_res._details(LOG_PREFIX, unique_id)
        log.info("GET RES DETAILS : %s" % res_details)

        if res_details:
            subcategory = res_details.get('subcategory', '')
            subcategory_list = [subcat.strip() for subcat in subcategory.split(',') if subcat]
            res_details['subcategory_list'] = subcategory_list

            form = MenuUpdateForm(decoded_body, subcategory_list=subcategory_list)
            if not form.is_valid():
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

            item_id = decoded_body.get('item_id')  # Get item_id from POST data
            if not item_id:
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Item ID is required!"})

            update_data = {
                'unique_id': unique_id,
                'item_id': item_id,
                'item_name': decoded_body.get('item_name'),
                'item_description': decoded_body.get('item_description'),
                'item_price': decoded_body.get('item_price'),
                'item_category': decoded_body.get('item_category'),
                'item_type': decoded_body.get('item_type')
            }

            update_menu_item = cls_register._update_menu(LOG_PREFIX, data=update_data)
            log.info("UPDATE MENU ITEM : %s" % update_menu_item)

            if update_menu_item:
                return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Menu item updated successfully!"})
            else:
                return JsonResponse(
                    {"status": "FAILURE", "statuscode": 404, "msg": "Menu item not found or update failed"})

        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Restaurant not found"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def list_item(request, *args, **kwargs):
    EVENT = "ListItems"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()
    try:
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID : %s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        items_list = cls_register.item_list(LOG_PREFIX, unique_id)
        log.info("ITEMS LIST : %s" % items_list)

        if items_list is not None:
            return JsonResponse(
                {"status": "SUCCESS", "statuscode": 200, "msg": "Items retrieved successfully!", "data": items_list})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to retrieve items!"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def delete_item(request, *args, **kwargs):
    EVENT = "DeleteItem"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()
    try:
        decoded_body = json.loads((request.body).decode())
        item_id = decoded_body.get('item_id') or kwargs.get('item_id')
        log.info("ITEM ID: %s" % item_id)

        if not item_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Item ID is required!"})

        item_delete = cls_register._delete_item(LOG_PREFIX, item_id)
        log.info("ITEM DELETE :%s" %item_delete)

        if item_delete:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Item deleted successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to delete item!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def item_rating(request, *args, **kwargs):
    EVENT = "RateItem"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()

    try:
        decoded_body = json.loads((request.body).decode())

        unique_id = kwargs.get('unique_id')
        logging.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        form = RateItemForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        item_id = decoded_body.get('item_id')
        item_rating = float(decoded_body.get('item_rating'))

        if not item_id or item_rating is None:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Item ID and rating are required!"})

        data_dict = {
            'item_id': item_id,
            'item_rating': item_rating,
        }
        add_item_rating = cls_register._rate_item(LOG_PREFIX, data_dict)
        logging.info("RATE ITEM :%s" % add_item_rating)

        if add_item_rating:
            item = cls_register.db_item_rating._find_one({'item_id': item_id})
            return JsonResponse({
                "status": "SUCCESS",
                "statuscode": 200,
                "msg": "Item rated successfully!",
                "data": {
                        "avg_rating": item['avg_rating'],
                        "no_of_ratings": item['no_of_ratings']
                }
            })
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Item not found"})
    except Exception as e:
        logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_rating(request, *args, **kwargs):
    EVENT = "UpdateItemRating"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()

    try:
        decoded_body = json.loads((request.body).decode())

        unique_id = kwargs.get('unique_id')
        logging.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        form = UpdateRatingForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        item_id = decoded_body.get('item_id')
        old_rating = float(decoded_body.get('old_rating'))
        new_rating = float(decoded_body.get('new_rating'))

        if not item_id or old_rating is None or new_rating is None:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Item ID, old rating, and new rating are required!"})

        data_dict = {
            'item_id': item_id,
            'old_rating': old_rating,
            'new_rating': new_rating,
        }
        updated_rating = cls_register.update_item_rating(LOG_PREFIX, data_dict)
        logging.info("UPDATE ITEM RATING :%s" % updated_rating)

        if updated_rating:
            item = cls_register.db_item_rating._find_one({'item_id': item_id})
            return JsonResponse({
                "status": "SUCCESS",
                "statuscode": 200,
                "msg": "Item rating updated successfully!",
                "data": {
                    "avg_rating": item['avg_rating'],
                    "no_of_ratings": item['no_of_ratings']
                }
            })
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Item not found"})
    except Exception as e:
        logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})