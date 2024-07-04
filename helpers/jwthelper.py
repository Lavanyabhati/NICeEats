from datetime import datetime, timedelta
import jwt
from configuration import *


class JWToken:
    def __init__(self):
        self.secret_key = SECRET_KEY

    def _generate(self, type, payload):
        success = False
        try:
            if type == "access":
                payload['grant_type'] = "access"
                payload['exp'] = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXP)
            else:
                payload['grant_type'] = "refresh"
                payload['exp'] = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXP)

            token = jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
            success = True
            return success, token
        except Exception as e:
            data = {
                "error": str(e)
            }
            return success, data

    def _validate(self, token):
        success = False
        try:
            decode_token = jwt.decode(token, key=self.secret_key, algorithms=['HS256'])
            success = True
            return success, decode_token
        except jwt.ExpiredSignatureError:
            return success, {
                "error": 'EXPIRED'
            }
        except jwt.InvalidTokenError:
            return success, {
                "error": 'INVALID'
            }
        except Exception as e:
            return success, {
                "error": f'{e}'
            }

# cls_jwt = JWToken()
# payload = {
#     'name':'test'
# }
# res, tokenn = cls_jwt._generate(type='access', payload=payload)
# print(tokenn)
# print(cls_jwt._validate(tokenn))
