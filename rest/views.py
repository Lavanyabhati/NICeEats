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
            if token_scope != TOKEN_SCOPE_RESTAURANT:
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


def generate_item_id():
    return ''.join(random.choices('0123456789ABCDEF', k=16))


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def register_res(request, *args, **kwargs):
    EVENT = "AddRestaurant"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Restaurant()
    try:

        post_data = request.POST
        form = RegisterRestaurantForm(post_data)

        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})

        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        data_dict = {
                'unique_id': unique_id,
                'name': post_data.get('name'),
                'category': post_data.get('category'),
                'location_name': post_data.get('location_name'),
                'latitude': post_data.get('latitude'),
                'longitude': post_data.get('longitude'),
                'food_type': post_data.get('food_type'),
                'operating_hours': post_data.get('operating_hours'),
                'subcategory': post_data.get('subcategory')
        }

        insert_res = cls_register._add(LOG_PREFIX, data=data_dict)
        log.info("INSERT RES :%s" %insert_res)

        if insert_res:
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
        post_data = request.POST
        form = RegisterRestaurantOwnerForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        insert_res_owner = cls_register._add_owner_details(data=post_data)

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
        post_data = request.POST
        form = UpdateRestaurantOwnerForm(post_data)
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
            'name': post_data.get('name', ''),
            'address': post_data.get('address', ''),
            'email': post_data.get('email', ''),
            'date_of_birth': post_data.get('date_of_birth', ''),
            'gender': post_data.get('gender', ''),
            'verification_id': post_data.get('verification_id', ''),
            'verification_type': post_data.get('verification_type', ''),
        }

        res_owner_update = cls_register._update_owner_details(LOG_PREFIX, data=update_data)
        log.info("RES OWNER UPDATE :%s" %res_owner_update)
        if res_owner_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant owner updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update restaurant owner!"})

    except Exception as e:
        print(f"Exception in update_res_owner(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["GET","POST"])
@verify_auth_token
def list_res(request,*args, **kwargs):
    cls_register = Restaurant()
    EVENT = "ListRestaurants"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'

    try:
        post_data = request.POST
        form = RestaurantListForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        data = {}
        data['latitude'] = post_data.get('latitude')
        data['longitude'] = post_data.get('longitude')
        data['max_distance'] = post_data.get('max_distance')

        res_list = cls_register._list(LOG_PREFIX, data=data)
        log.info("RES LIST:%s" %res_list)
        if res_list:
            for res in res_list:
                origin = (float(post_data.get('longitude')), float(post_data.get('latitude')))
                dist = (res['location']['coordinates'][0], res['location']['coordinates'][1])
                aerial_dist = math.ceil(geodesic(dist, origin).kilometers)
                # road_dist = (254.5/99) * aerial_dist
                res['distance'] = aerial_dist
                res['delivery_time'] = f'{(aerial_dist * 7) + 20}-{(aerial_dist * 10)+ 20} Mins'

        return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurants listed successfully!", "restaurants": res_list})
        # else:
        #     return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "No restaurants found!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["GET", "POST"])
@verify_auth_token
def update_res(request, *args, **kwargs):
    cls_register = Restaurant()
    EVENT = "UpdateResProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        log.info("In Here...")
        post_data = request.POST
        form = RestaurantUpdateForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})
        log.info("KWARGS in update_res : %s" % kwargs)

        unique_id = kwargs.get('unique_id')

        update_data = {
            'unique_id': unique_id,
            'name': post_data.get('name', ''),
            'location_name': post_data.get('location_name', ''),
            'category': post_data.get('category', ''),
            'location_long': post_data.get('longitude'),
            'location_lat': post_data.get('latitude'),
            'food_type': post_data.get('food_type'),
            'operating_hours': post_data.get('operating_hours'),
            'subcategory': post_data.get('subcategory')
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
@require_http_methods(["POST"])
@verify_auth_token
def add_item(request, *args, **kwargs):
    EVENT = "AddMenuItem"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_register = Menu()
    cls_res = Restaurant()
    try:

        post_data = request.POST

        subcategory_list = []
        form = MenuForm(post_data, subcategory_list)

        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})
        log.info("KWARGS in update_res : %s" % kwargs)

        # item_id = generate_item_id()
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})
        item_id = ''.join(random.choices('0123456789ABCDEF', k=16))
        data_dict = {
                'unique_id': unique_id,
                'item_id': item_id,
                'item_name': post_data.get('item_name'),
                'item_description': post_data.get('item_description'),
                'item_price': post_data.get('item_price'),
                'item_category': post_data.get('item_category'),
                'item_type': post_data.get('item_type')
        }

        insert_menu_item = cls_register._add_menu(LOG_PREFIX, data=data_dict)
        log.info("INSERT MENU ITEM :%s" %insert_menu_item)

        if insert_menu_item:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Menu item added successfully!"})
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
    try:

        post_data = request.POST
        form = MenuUpdateForm(post_data)

        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})
        log.info("KWARGS in update_item : %s" % kwargs)

        # item_id = generate_item_id()
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        update_data = {
                'unique_id': unique_id,
                'item_id': post_data.get('item_id'),
                'item_name': post_data.get('item_name'),
                'item_description': post_data.get('item_description'),
                'item_price': post_data.get('item_price'),
                'item_category': post_data.get('item_category'),
                'item_type': post_data.get('item_type')
        }

        update_menu_item = cls_register._update_menu(LOG_PREFIX, data=update_data)
        log.info("INSERT MENU ITEM :%s" % update_menu_item)

        if update_menu_item:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Menu item added successfully!"})
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
        item_id = kwargs.get('item_id')
        log.info("UNIQUE ID :%s" % item_id)
        if not item_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Item ID is required!"})

        data = {'item_id': item_id}

        item_delete = cls_register._delete_item(LOG_PREFIX, item_id, data)
        log.info("ITEM DELETE :%s" %item_delete)

        if item_delete:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Item deleted successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to delete item!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})

