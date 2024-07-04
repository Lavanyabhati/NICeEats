from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from helpers.jwthelper import JWToken
from user.register_views import Register
from .forms import OTPForm
from .background import OTP
from configuration import *




@require_http_methods(["POST"])
@csrf_exempt
def otp(request):
    cls_register = Register()
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
        log.info(uri)
        print(uri)

        if action == 'generate':
            response = otp_handler.generate(LOG_PREFIX, mobile_number)
            log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "Result":"{response}"')
            if response:
                log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "MobileNo":"{mobile_number}", "Result":"Success"')
                return JsonResponse(
                    {"status": "SUCCESS", "statuscode": 200, "msg": "OTP Sent successfully!"})
            log.info(f'{LOG_PREFIX}, "Action":"GenerateOTP", "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"InternalServerError"')


        elif action == 'verify':
            otp_code = request.POST.get('otp')
            v_status, v_response = otp_handler.verify(LOG_PREFIX, mobile_number, otp_code)
            if v_status:
                profile_status, profile_data = cls_register._find(LOG_PREFIX, mobile_number)
                if profile_status:
                    # user exists in the collection profile_user
                    token_payload = {
                        'contact': profile_data['mobile_number'],
                        'firstname': profile_data.get('first_name', ''),
                        'lastname': profile_data.get('last_name', ''),
                        'scope': TOKEN_SCOPE_USER
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
                    add_result = cls_register._add(LOG_PREFIX, mobile_number)
                    if not add_result:
                        log.info(
                            f'{LOG_PREFIX}, "Action":"VerifyOTP", "Result":"Failure", "Reason":"UserProfileCreationFailed"')
                    token_payload = {
                        'contact': mobile_number,
                        'firstname': '',
                        'lastname': '',
                        'scope': TOKEN_SCOPE_USER
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
            log.info(f'{LOG_PREFIX}, "Action":"VerifyOTP", "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"InternalServerError"')

        elif action == 'resend':
            response = otp_handler.resend(LOG_PREFIX, mobile_number)
            if response:
                log.info(f'{LOG_PREFIX}, "Action":"ResendOTP", "Result":"Success"')
                return JsonResponse(
                    {"status": "SUCCESS", "statuscode": 200, "msg": "OTP resent successfully!"})
            log.info(f'{LOG_PREFIX}, "Action":"ResendOTP", "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"InternalServerError"')

        return JsonResponse({
            "status": "FAILURE",
            "statuscode": 500,
            "msg": 'Internal Server Error'
        })
    except Exception as e:
        log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
        return JsonResponse({"status": "FAILURE", "statuscode": 500, "msg": 'Internal Server Error'})

