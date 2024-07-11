import random

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from helpers.jwthelper import JWToken
# from user.register_views import Register
from .forms import OTPForm
from .background import OTP
from configuration import *
from rest.register_views import Restaurant, Menu
from user.register_views import User


@require_http_methods(["POST"])
@csrf_exempt
def otp(request):
    # cls_register = Register()
    otp_handler = OTP()
    cls_jwt = JWToken()
    EVENT = "OTP"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    try:
        form = OTPForm(request.POST)
        if not form.is_valid():
            log.info(f'{LOG_PREFIX}, "Action":"ValidateForm", "Result":"Failure", "Reason":"{form.errors}"')
            return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})

        mobile_number = request.POST.get('mobile_number')
        action = request.POST['action']
        uri = request.build_absolute_uri()
        log.info("Requested URL : %s" %uri)

        if "restaurant" in uri:
            user_type = "restaurant"
            token_scope = TOKEN_SCOPE_RESTAURANT
            cls_register = Restaurant()
        elif "user" in uri:
            user_type = "user"
            token_scope = TOKEN_SCOPE_USER
            cls_register = User()
        else:
            user_type = "unknown"
            token_scope = ''

        print(f'URI: {uri}, UserType: {user_type}')
        print(uri)

        if action == 'generate':
            response = otp_handler.generate(LOG_PREFIX, mobile_number, user_type)
            log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "Result":"{response}"')
            if response:
                log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "MobileNo":"{mobile_number}", "UserType":"{user_type}" ,"Result":"Success"')
                return JsonResponse(
                    {"status": "SUCCESS", "statuscode": 200, "msg": "OTP Sent successfully!"})
            log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "MobileNo":"{mobile_number}","UserType":"{user_type}", "Result":"Failure", "Reason":"InternalServerError"')


        elif action == 'verify':
            otp_code = request.POST.get('otp')
            v_status, v_response = otp_handler.verify(LOG_PREFIX, mobile_number, otp_code,user_type)
            if v_status:
                unique_id = ''.join(random.choices('0123456789ABCDEF', k=16))
                profile_status, profile_data = cls_register._find(LOG_PREFIX, mobile_number)
                if profile_status:
                    # user exists in the collection profile_user
                    token_payload = {
                        'contact': profile_data['mobile_number'],
                        'unique_id': unique_id,
                        'firstname': profile_data.get('first_name', ''),
                        'lastname': profile_data.get('last_name', ''),
                        'scope': token_scope,
                        # 'user_type': user_type
                    }
                    token_status, token_res = cls_jwt._generate('access', token_payload)
                    refresh_token_status, refresh_token_res = cls_jwt._generate('refresh', token_payload)
                    if token_status and refresh_token_status:
                        log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "Result":"Success"')
                        return JsonResponse({
                            "status": "SUCCESS",
                            "statuscode": 200,
                            "msg": "User details found",
                            "access_token": token_res,
                            "refresh_token": refresh_token_res,
                        })
                    log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "Result":"Failure", "Reason":"TokenCreationFailed"')
                else:
                    if token_scope == TOKEN_SCOPE_USER:
                        add_result = cls_register._add(LOG_PREFIX, mobile_number)
                        log.info("USER.....")
                    else:
                        data = {
                            'mobile_number': mobile_number,
                            'unique_id': unique_id,
                        }
                        add_result = cls_register._add_owner_details(LOG_PREFIX, data)
                        log.info("RES.....")

                    if not add_result:
                        log.info(
                            f'{LOG_PREFIX}, "Action":"VerifyOTP", "Result":"Failure", "Reason":"UserProfileCreationFailed"')
                    token_payload = {
                        'contact': mobile_number,
                        'unique_id': unique_id,
                        'firstname': '',
                        'lastname': '',
                        'scope': token_scope,
                        # 'user_type': user_type
                    }
                    token_status, token_res = cls_jwt._generate('access', token_payload)
                    refresh_token_status, refresh_token_res = cls_jwt._generate('refresh', token_payload)
                    if token_status and refresh_token_status:
                        log.info(f'{LOG_PREFIX}, "Action":"VerifyOTP", "Result":"Success"')
                        return JsonResponse({
                            "status": "SUCCESS",
                            "statuscode": 200,
                            "msg": "User details found",
                            "access_token": token_res,
                            "refresh_token": refresh_token_res,
                        })
                    log.info(
                        f'{LOG_PREFIX}, "Action":"VerifyOTP", "Result":"Failure", "Reason":"TokenCreationFailed"')
            elif v_response:
                log.info(
                    f'{LOG_PREFIX}, "Action":"VerifyOTP", "Result":"Failure", "Reason":"{v_response}"')
                return JsonResponse({
                    "status": "FAILURE",
                    "statuscode": 400,
                    "msg": v_response
                })
            log.info(f'{LOG_PREFIX}, "Action":"VerifyOTP", "MobileNo":"{mobile_number}","UserType":"{user_type}", "Result":"Failure", "Reason":"InternalServerError"')

        elif action == 'resend':
            response = otp_handler.resend(LOG_PREFIX, mobile_number, user_type)
            if response:
                log.info(f'{LOG_PREFIX}, "Action":"ResendOTP", "Result":"Success"')
                return JsonResponse(
                    {"status": "SUCCESS", "statuscode": 200, "msg": "OTP resent successfully!"})
            log.info(f'{LOG_PREFIX}, "Action":"ResendOTP", "MobileNo":"{mobile_number}","UserType":"{user_type}", "Result":"Failure", "Reason":"InternalServerError"')

        return JsonResponse({
            "status": "FAILURE",
            "statuscode": 500,
            "msg": 'Internal Server Error'
        })
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": 'Internal Server Error'})

