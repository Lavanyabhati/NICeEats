from django.http import JsonResponse
from .forms import *
from .register_views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
@csrf_exempt
def register_res_owner(request):
    cls_register = Register()
    try:
        post_data = request.POST
        form = RegisterRestaurantOwnerForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        insert_res_owner = cls_register._add_owner_details(data=post_data)

        if insert_res_owner:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant registered successfully!"})

    except Exception as e:
        print("Exception in register(). Reason : %s" % e)
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})

@csrf_exempt
def register_res(request):
    cls_register = Register()
    try:
        post_data = request.POST
        form = RegisterRestaurantForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})

        insert_res = cls_register._add(data=post_data)

        if insert_res:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant registered successfully!"})
    except Exception as e:
        print("Exception in register(). Reason : %s" %e)
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})

@csrf_exempt
def list_res(request):
    cls_register = Register()
    try:
        post_data = request.POST
        form = RestaurantListForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status":"FAILURE","statuscode":400,"msg":form.errors})

        res_list = cls_register._list(data=post_data)
        if res_list:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant registered successfully!"})
    except Exception as e:
        print("Exception in register(). Reason : %s" %e)
        return JsonResponse({"status":"FAILURE","statuscode":500,"msg":"Internal Server Error!"})

@csrf_exempt
def update_res(request):
    cls_register = Register()
    try:
        post_data = request.POST
        form = RestaurantUpdateForm(post_data)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        res_update = cls_register._update_db(res_id=post_data.get('id'), data=post_data)
        if res_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update restaurant!"})
    except Exception as e:
        print("Exception in update_res(). Reason: %s" % e)
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
def delete_res(request):
    cls_register = Register()
    try:
        res_id = request.POST.get('id')
        if not res_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Restaurant ID is required!"})

        res_delete = cls_register._delete(res_id=res_id)
        if res_delete:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Restaurant deleted successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to delete restaurant!"})
    except Exception as e:
        print("Exception in delete_res(). Reason: %s" % e)
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})
