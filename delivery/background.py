from configuration import *
from datetime import datetime
import json
from django.http import JsonResponse
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from helpers.dbhelper import DBOperation
import random


class Agent:
    def __init__(self):
        self.db = DBOperation(DB_NAME)
        self.db_agent_profile = DBOperation(COLLECTION_PROFILE_AGENT)
        self.db_agent_session = DBOperation(COLLECTION_SESSION_AGENT)

    def _find(self, LOG_PREFIX, mobile_number):
        success = False
        ACTION = "Agent._find()"
        try:
            profile_user = self.db_agent_profile._find_one(
                filter={
                    'mobile_number': mobile_number
                }
            )
            if profile_user:
                log.info(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Success"')
                success = True
                return success, profile_user
            log.info(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"DataNotFound"')
            return success, None

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Action":{ACTION}, "MobileNo":"{mobile_number}", "Result":"Failure", "Reason":"{e}"')
            return success, None

    def _update_agent_status(self, unique_id, new_status, LOG_PREFIX):
        try:
            filter_data = {'unique_id': unique_id}
            update_data = {'agent_status': new_status}

            update_result = self.db_agent_profile._update(filter_data, update_data)

            if update_result.modified_count > 0:
                log.info(f'{LOG_PREFIX}, "Agent profile updated successfully to {new_status}!"')
            else:
                log.info(f'{LOG_PREFIX}, "Agent profile not updated to {new_status}!"')

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')

    def _add_delivery_agent(self, LOG_PREFIX, data):
        try:
            mobile_number = data.get('mobile_number')
            unique_id = data.get('unique_id')

            name = data.get('name', '')
            address = data.get('address', '')
            email = data.get('email', '')
            date_of_birth = data.get('date_of_birth', '')
            gender = data.get('gender', '')
            verification_id = data.get('verification_id', '')
            verification_type = data.get('verification_type', '')
            vehicle_type = data.get('vehicle_type', '')
            vehicle_reg_no = data.get('vehicle_reg_no', '')
            agent_status = data.get('agent_status', '')

            filter_data = {
                'mobile_number': mobile_number,
                'unique_id': unique_id,
            }
            agent_document = {
                'name': name,
                'address': address,
                'email': email,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'profile_type': 'AGENT',
                'verification_id': verification_id,
                'verification_type': verification_type,
                'vehicle_type': vehicle_type,
                'vehicle_reg_no': vehicle_reg_no,
                'agent_status': agent_status,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_delivery_agent = self.db_agent_profile._insert(upsert_filter=filter_data, data=agent_document)

            print("Delivery agent profile saved successfully!")
            return True if insert_delivery_agent.inserted_id else False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _update_delivery_agent(self, LOG_PREFIX, data):
        try:
            mobile_number = data.get('mobile_number')
            unique_id = data.get('unique_id')

            name = data.get('name', '')
            address = data.get('address', '')
            email = data.get('email', '')
            date_of_birth = data.get('date_of_birth', '')
            gender = data.get('gender', '')
            verification_id = data.get('verification_id', '')
            verification_type = data.get('verification_type', '')
            vehicle_type = data.get('vehicle_type', '')
            vehicle_reg_no = data.get('vehicle_reg_no', '')
            agent_status = data.get('agent_status', '')

            filter_data = {
                'mobile_number': mobile_number,
                'unique_id': unique_id,

            }
            update_data = {
                'name': name,
                'address': address,
                'email': email,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'profile_type': 'AGENT',
                'verification_id': verification_id,
                'verification_type': verification_type,
                'vehicle_type': vehicle_type,
                'vehicle_reg_no': vehicle_reg_no,
                'agent_status': agent_status,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }

            delivery_agent_update = self.db_agent_profile._update(filter_q=filter_data, update_data=update_data, upsert=True)

            if delivery_agent_update.modified_count > 0:
                return True
            else:
                return False

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return {"status": "FAILURE", "message": "Error updating owner details"}

    def _add_agent_session(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            # order_id = data.get('order_id')
            order_status = data.get('order_status')
            agent_location_latitude = data.get('agent_location_latitude')
            agent_location_longitude = data.get('agent_location_longitude')
            payment_mode = data.get('payment_mode')
            payment_amount = data.get('payment_amount')

            if agent_location_latitude is None or agent_location_longitude is None:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Latitude and Longitude are required!"')
                return False

            session_document = {
                'unique_id': unique_id,
                # 'order_id': order_id,
                'session_start_time': datetime.now(),
                'session_end_time': datetime.now(),
                'order_status': order_status,
                'location': {
                    'type': 'Point',
                    'coordinates': [float(agent_location_longitude), float(agent_location_latitude)]
                },
                'payment_mode': payment_mode,
                'payment_amount': payment_amount,
            }
            insert_agent_session = self.db_agent_session._insert(data=session_document)
            return True if insert_agent_session.inserted_id else False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False

    def _update_agent_session(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            # order_id = data.get('order_id')
            order_status = data.get('order_status')
            agent_location_latitude = data.get('agent_location_latitude')
            agent_location_longitude = data.get('agent_location_longitude')
            payment_mode = data.get('payment_mode')
            payment_amount = data.get('payment_amount')

            if agent_location_latitude is None or agent_location_longitude is None:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Latitude and Longitude are required!"')
                return False
            filter_data={
                'unique_id': unique_id,
                # 'order_id': order_id,

            }
            session_document = {
                'order_status': order_status,
                'location': {
                    'type': 'Point',
                    'coordinates': [float(agent_location_longitude), float(agent_location_latitude)]
                },
                'payment_mode': payment_mode,
                'payment_amount': payment_amount,
            }
            if order_status == "accepted":
                session_document['session_start_time'] = datetime.now()
                self._update_agent_status(unique_id, "engaged", LOG_PREFIX)

            if order_status == "delivered":
                session_document['session_end_time'] = datetime.now()
                self._update_agent_status(unique_id, "online", LOG_PREFIX)

            update_agent_session = self.db_agent_session._update(filter_q=filter_data, update_data=session_document, upsert=True)
            if update_agent_session.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False
