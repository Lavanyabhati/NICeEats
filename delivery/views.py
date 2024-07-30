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
        log.info("UNIQUE ID :%s" % unique_id)

        if not unique_id:
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": "Unique ID is required!"})

        data_dict = {
            'unique_id': unique_id,
            'session_start_time': datetime.now(),
            'session_end_time': datetime.now(),
            'order_status': decoded_body.get('order_status'),
            'agent_location_latitude': decoded_body.get('agent_location_latitude'),
            'agent_location_longitude': decoded_body.get('agent_location_longitude'),
            'payment_mode': decoded_body.get('payment_mode'),
            'payment_amount': decoded_body.get('payment_amount')
        }

        insert_agent_session = cls_session._add_agent_session(LOG_PREFIX, data=data_dict)

        if insert_agent_session:
            return JsonResponse({"status": "SUCCESS", "statuscode": 200, "msg": "Agent's session created successfully!"})
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
    EVENT = "UpdateAgentProfile"
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
