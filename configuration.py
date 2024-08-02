import logging
import pymongo


############################################ Static Values Start ############################################
EXPIRY_MINUTES = 10
SECRET_KEY = b'k2p1IAURFRzyxX7wqATNe2oxpmJCW17aG3_V5AvxHgI='
ACCESS_TOKEN_EXP = 1
REFRESH_TOKEN_EXP = 7
TOKEN_SCOPE_USER = 'USER'
TOKEN_SCOPE_RESTAURANT = 'OWNER'
TOKEN_SCOPE_AGENT = 'AGENT'
MIN_TRAVEL_TIME_PER_KM = 7
MAX_TRAVEL_TIME_PER_KM = 10
FOOD_PREP_TIME = 20
RATING_INCREMENT = 1

############################################ Static Values End ############################################



############################################ Logging Conf Start ############################################
LOG_FILE_PATH = 'C:/Users/lavan/PythonProjects/NICeEats/niceeats.log'
log = logging.getLogger('')
info_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
formatter = logging.Formatter('{"Time":"%(asctime)s", "Level":"%(levelname)s", "File":"%(filename)s", "Line":"%(lineno)d", %(message)s}')
info_handler.setFormatter(formatter)
log.addHandler(info_handler)
log.setLevel(logging.INFO)
############################################ Logging Conf End ############################################


############################################ Database Connection Start ############################################
DB_HOST = "localhost"
DB_PORT = 27017
DB_NAME = "NICeEats"
# DB_NAME = "Restaurant_database"
COLLECTION_OTP = 'OTP'
COLLECTION_PROFILE_USER = 'UserProfile'
COLLECTION_PROFILE_RESTAURANT = 'Restaurant'
COLLECTION_PROFILE_RESTAURANT_OWNER = 'RestaurantOwnerProfile'
COLLECTION_RESTAURANT_RECENT_ORDERS = 'RestaurantOrders'
COLLECTION_RES_MENU = 'Menu'
COLLECTION_RATING = 'MenuItemRating'
COLLECTION_PROFILE_AGENT = 'DeliveryAgentProfile'
COLLECTION_SESSION_AGENT = 'DeliveryAgentSession'



def db_conn():
    client = pymongo.MongoClient(DB_HOST, DB_PORT)
    db = client[DB_NAME]
    return db
############################################ Database Connection End ############################################

def client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except Exception as e:
        log.error(f'"Event":"GetClientIP", "Result":"Exception", "Reason":"{e}"')
        return None
