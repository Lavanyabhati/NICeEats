import logging
from random import randint
from django.http import JsonResponse
from django.utils import timezone
# from FoodApp.settings import MONGO_DB
from datetime import datetime
from configuration import *
from helpers.dbhelper import *

class OTP:
    def __init__(self):
        # self.collection = COLLECTION_OTP
        self.db = DBOperation(COLLECTION_OTP)
        # self.db_2 = DBOperation(COLLECTION_OTP)
        self.EXPIRY_MINUTES = EXPIRY_MINUTES

    def calculate_ttl(self, document):
        expiry = document.get('expiry')
        if expiry:
            now = timezone.now()
            return max(0, (expiry - now).total_seconds())
        else:
            return None

    def generate(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "GenerateOTP"
        try:
            otp_code = randint(100000, 999999)
            expiry = datetime.now()
            dfilter = {'mobile_number': mobile_number}
            dupdate = {'otp_code': otp_code, 'created_at': expiry}
            result = self.db._update(filter_q=dfilter, update_data=dupdate, upsert=True)
            log.info(
                f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "OTP":"{otp_code}", "Expiry":"{expiry}", "Result":"Success", "Reason":"{result}"')
            success = True
            return success
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"{e}"')
            return success

    def verify(self, LOG_PREFIX, mobile_number, otp_code):
        success = False
        ACTION = "VerifyOTP"
        try:
            dfilter = {
                'mobile_number': mobile_number,
                'otp_code': int(otp_code)
            }
            otp_data = self.db._find_one(filter=dfilter)
            if not otp_data:
                log.info(
                    f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "OTP":"{otp_code}", "Result":"Failure", "Reason":"DataNotFound"')
                return success, 'Data Not Found'

            db_dt = otp_data.get('created_at')
            log.info("DT DIFF ::::: %s" %(datetime.now() - db_dt).total_seconds())
            dt_diff = (datetime.now() - db_dt).total_seconds()
            if dt_diff > (EXPIRY_MINUTES * 60):
                log.info(
                    f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "OTP":"{otp_code}", "TimeDifference":"{dt_diff} Seconds", "Result":"Failure", "Reason":"OTPExpired"')
                return success, 'OTP Expired'
            if dt_diff < (EXPIRY_MINUTES * 60):
                log.info(
                    f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "OTP":"{otp_code}", "TimeDifference":"{dt_diff} Seconds", "Result":"Success"')
                success = True
                return success, 'Success'

            self.db._delete(filter_d=dfilter)
            return success, None
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "OTP":"{otp_code}", "Result":"Failure", "Reason":"{e}"')
            return success, None

    def resend(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "ResendOTP"
        try:
            return self.generate(LOG_PREFIX, mobile_number)
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"{e}"')
            return success, None