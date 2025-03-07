import json
from django.http import JsonResponse
from .forms import *
from .background import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from configuration import *
from geopy.distance import geodesic
import math
from functools import wraps
from helpers.jwthelper import JWToken
from datetime import timedelta
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
            log.info("ValidateAgent :: %s" % validate_success)
            log.info("ValidateAgentData :: %s" % token_data)
            if not validate_success:
                error_msg = token_data.get('error', 'Unknown error')
                return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": f"Token validation failed: {error_msg}"})

            token_scope = token_data.get('scope')
            if token_scope != TOKEN_SCOPE_AGENT:
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
def register_agent(request):
    cls_register = Agent()
    EVENT = "AddDeliveryAgentProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = RegisterDeliveryAgentForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        insert_delivery_agent = cls_register._add_delivery_agent(LOG_PREFIX, data=decoded_body)

        if insert_delivery_agent:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Delivery Agent registered successfully!"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_agent(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "UpdateDeliveryAgentProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = UpdateDeliveryAgentForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_agent : %s" %kwargs)

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
            'vehicle_type': decoded_body.get('vehicle_type', ''),
            'vehicle_reg_no': decoded_body.get('vehicle_reg_no', ''),
            'agent_location_latitude': decoded_body.get('agent_location_latitude', ''),
            'agent_location_longitude': decoded_body.get('agent_location_longitude', ''),
            'agent_status': decoded_body.get('agent_status', '')
        }

        delivery_agent_update = cls_register._update_delivery_agent(LOG_PREFIX, data=update_data)
        log.info("DELIVERY AGENT UPDATE :%s" %delivery_agent_update)
        if delivery_agent_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Delivery Agent's profile updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update delivery agent's profile!"})

    except Exception as e:
        print(f"Exception in update_agent(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def agent_session(request, *args, **kwargs):
    cls_session = Agent()
    EVENT = "AddAgentSession"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads(request.body.decode())
        form = AgentSessionForm(decoded_body)

        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        unique_id = kwargs.get('unique_id')
        order_id = decoded_body.get('order_id')
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        if not order_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Order ID is required!"})

        session_id = 'S_' + ''.join(random.choices('0123456789ABCDEF', k=14))
        data_dict = {
            'unique_id': unique_id,
            'session_id': session_id,
            'order_id': order_id,
            'order_status': decoded_body.get('order_status'),
            'payment_mode': decoded_body.get('payment_mode'),
            'payment_amount': decoded_body.get('payment_amount'),
            'pickup_location_latitude': decoded_body.get('pickup_location_latitude'),
            'pickup_location_longitude': decoded_body.get('pickup_location_longitude'),
            'pickup_location_name': decoded_body.get('pickup_location_name'),
            'delivery_location_latitude': decoded_body.get('delivery_location_latitude'),
            'delivery_location_longitude': decoded_body.get('delivery_location_longitude'),
            'delivery_location_name': decoded_body.get('delivery_location_name'),
        }

        insert_agent_session = cls_session._add_agent_session(LOG_PREFIX, data=data_dict)
        log.info("INSERT AGENT SESSION :%s" % insert_agent_session)
        if insert_agent_session:
            filter_data = {
                'order_id': order_id,
            }

            update_data = {
                'order_status': decoded_body.get('order_status')
            }
            order_update_result = cls_session.db_order_collection._update(filter_q=filter_data, update_data=update_data)

            if order_update_result.modified_count > 0:
                log.info("ORDER UPDATE :%s" % order_update_result)
                return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent's session created and order updated successfully!"})
            else:
                return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Agent's session created, but failed to update the order!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to create agent's session!"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_session(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "UpdateAgentSession"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = UpdateAgentSessionForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_session : %s" %kwargs)
        unique_id = kwargs.get('unique_id')

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        update_data = {
            'unique_id': unique_id,
            # 'order_id' : order_id,
            'order_status': decoded_body.get('order_status'),
            'agent_location_latitude': decoded_body.get('agent_location_latitude'),
            'agent_location_longitude': decoded_body.get('agent_location_longitude'),
            'payment_mode': decoded_body.get('payment_mode'),
            'payment_amount': decoded_body.get('payment_amount')
        }

        agent_session_update = cls_register._update_agent_session(LOG_PREFIX, data=update_data)
        log.info("AGENT SESSION UPDATE :%s" %agent_session_update)
        if agent_session_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent session updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update agent session!"})

    except Exception as e:
        print(f"Exception in update_session(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def profile_status(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "UpdateAgentProfileStatus"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = AgentProfileStatusForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_agent_status : %s" % kwargs)
        unique_id = kwargs.get('unique_id')

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        update_data = {
            'unique_id': unique_id,
            'agent_status': decoded_body.get('agent_status')
        }

        update_profile_status = cls_register._agent_profile_status(LOG_PREFIX, data=update_data)
        log.info("AGENT PROFILE STATUS UPDATE :%s" % update_profile_status)
        if update_profile_status:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent status updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update agent status!"})

    except Exception as e:
        print(f"Exception in update_session(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def delivery_agent_location(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "GetAgentLocation"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'

    try:
        unique_id = kwargs.get('unique_id')

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        location_data = cls_register._agent_location(LOG_PREFIX, unique_id)

        if location_data:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "data": location_data})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 404, "msg": "Agent not found or not online"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{str(e)}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_order_status(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "UpdateOrderStatus"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = UpdateOrderStatusForm(decoded_body)

        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_order_status : %s" % kwargs)
        unique_id = kwargs.get('unique_id')
        order_id = decoded_body.get('order_id')

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        if not order_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Order ID is required"})

        update_data = {
            'unique_id': unique_id,
            'order_id': order_id,
            'order_status': decoded_body.get('order_status')
        }

        order_status_update = cls_register._update_order_status(LOG_PREFIX, data=update_data)
        log.info("ORDER STATUS UPDATE: %s" % order_status_update)

        if order_status_update:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Order status updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update order status!"})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def update_agent_location(request, *args, **kwargs):
    cls_register = Agent()
    EVENT = "UpdateAgentLocation"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        decoded_body = json.loads((request.body).decode())
        form = UpdateAgentLocationForm(decoded_body)
        if not form.is_valid():
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        log.info("KWARGS in update_agent_location : %s" % kwargs)
        unique_id = kwargs.get('unique_id')

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required"})

        update_data = {
            'unique_id': unique_id,
            'agent_location_latitude': decoded_body.get('agent_location_latitude'),
            'agent_location_longitude': decoded_body.get('agent_location_longitude')
        }
        update_agent_status = cls_register._update_location(LOG_PREFIX, data=update_data)
        log.info("AGENT LOCATION UPDATE :%s" % update_agent_status)
        if update_agent_status:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent Location updated successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to update agent location!"})

    except Exception as e:
        print(f"Exception in update_session(). Reason: {e}")
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def delete_agent(request, *args, **kwargs):
    cls_agent = Agent()
    EVENT = "DeleteAgentProfile"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        unique_id = kwargs.get('unique_id')
        log.info("UNIQUE ID :%s" % unique_id)
        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        data = {'unique_id': unique_id}

        agent_profile_delete = cls_agent._delete_agent_profile(LOG_PREFIX, unique_id)
        log.info("RES DELETE :%s" %agent_profile_delete)

        if agent_profile_delete:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent Profile deleted successfully!"})
        else:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to delete agent profile!"})
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})


@csrf_exempt
@require_http_methods(["POST"])
@verify_auth_token
def sessions_list(request, *args, **kwargs):
    cls_agent = Agent()
    EVENT = "GetSessionsList"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'

    try:
        decoded_body = json.loads(request.body.decode())
        unique_id = kwargs.get('unique_id')
        days_filter = decoded_body.get('days_filter', 7)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        if days_filter not in [7, 15, 30]:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Invalid days filter value!"})

        data = {
            'unique_id': unique_id,
            'days_filter': days_filter
        }

        session_list = cls_agent._list_sessions(LOG_PREFIX, data)
        if session_list is False:
            return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Failed to fetch sessions!"})

        return JsonResponse({"status": "SUCCESS", "statuscode": 200, "sessions": list(session_list)})

    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": "Internal Server Error!"})
