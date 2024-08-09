from configuration import *
from datetime import datetime
import json
from django.http import JsonResponse
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from helpers.dbhelper import DBOperation
import random
from datetime import timedelta


class Agent:
    def __init__(self):
        self.db = DBOperation(DB_NAME)
        self.db_agent_profile = DBOperation(COLLECTION_PROFILE_AGENT)
        self.db_agent_session = DBOperation(COLLECTION_SESSION_AGENT)
        self.db_user_profile = DBOperation(COLLECTION_PROFILE_USER)
        self.db_order_collection = DBOperation(COLLECTION_ORDERS)

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
            update_data = {
                'agent_status': new_status,
            }

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
            agent_location_latitude = data.get('agent_location_latitude', '')
            agent_location_longitude = data.get('agent_location_longitude', '')
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
                'location': {
                    'type': 'Point',
                    'coordinates': [float(agent_location_longitude), float(agent_location_latitude)]
                },
                'agent_status': agent_status,
                'verification_status': 'APPROVED',
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
                agent_location_latitude = data.get('agent_location_latitude', '')
                agent_location_longitude = data.get('agent_location_longitude', '')
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
                    'location': {
                        'type': 'Point',
                        'coordinates': [float(agent_location_longitude), float(agent_location_latitude)]
                    },
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
            order_id = data.get('order_id')
            unique_id = data.get('unique_id')
            session_id = data.get('session_id')
            order_status = data.get('order_status')
            payment_mode = data.get('payment_mode')
            payment_amount = data.get('payment_amount')
            pickup_location_latitude = data.get('pickup_location_latitude')
            pickup_location_longitude = data.get('pickup_location_longitude')
            pickup_location_name = data.get('pickup_location_name')
            delivery_location_latitude = data.get('delivery_location_latitude')
            delivery_location_longitude = data.get('delivery_location_longitude')
            delivery_location_name = data.get('delivery_location_name')

            search_filter = {
                'order_id': order_id
            }

            user_contact = self.db_order_collection._find_one(search_filter)
            db = db_conn()
            abc = db['UserOrder'].find_one({'order_id':"O_SE7MTV3JVAXDSX"}, {'_id': False})
            log.info("OUTPUT :: %s" %abc)

            log.info("COLL :%s" % self.db_order_collection.coll_name)
            log.info("DB :%s" % self.db_order_collection.db)
            log.info("USER PROFILE :%s" % user_contact)
            log.info("ORDER ID :%s" % order_id)
            if not user_contact:
                return False

            user_contact_no = user_contact['delivery_contact_no']

            session_document = {
                'unique_id': unique_id,
                'order_id': order_id,
                'session_id': session_id,
                'session_start_time': datetime.now(),
                'order_status': "accepted",
                'pickup_location': {
                    'type': 'Point',
                    'coordinates': [float(pickup_location_longitude), float(pickup_location_latitude)]
                },
                'pickup_location_name': pickup_location_name,
                'delivery_location': {
                    'type': 'Point',
                    'coordinates': [float(delivery_location_longitude), float(delivery_location_latitude)]
                },
                'delivery_location_name': delivery_location_name,
                'user_contact_no': user_contact_no,
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
            session_end_time = datetime.now()

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
                'session_end_time': session_end_time
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

    def _agent_profile_status(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            agent_status = data.get('agent_status')

            filter_data = {
                'unique_id': unique_id
            }
            document = {
                'agent_status': agent_status
            }

            update_profile_status = self.db_agent_profile._update(filter_q=filter_data, update_data=document)
            if update_profile_status.modified_count > 0:
                return True
            else:
                return False
        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False

    def _agent_location(self,LOG_PREFIX, unique_id):
        try:
            filter_data = {'unique_id': unique_id}
            agent_profile = self.db_agent_profile._find_one(filter=filter_data)

            if not agent_profile:
                log.info(f'{LOG_PREFIX}, "Agent profile not found for unique_id: {unique_id}"')
                return None

            log.info(f'{LOG_PREFIX}, "Agent Profile": {agent_profile}')

            location = agent_profile.get('location')
            if not location or 'coordinates' not in location:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Location coordinates are missing!"')
                return None

            coordinates = location['coordinates']
            agent_location_longitude, agent_location_latitude = coordinates

            if agent_profile.get('agent_status') == 'online':
                return {
                    'unique_id': agent_profile.get('unique_id'),
                    # 'location': agent_profile.get('location')
                    'agent_location_latitude': agent_location_latitude,
                    'agent_location_longitude': agent_location_longitude,
                }
            else:
                log.info(f'{LOG_PREFIX}, "Agent is not online for unique_id: {unique_id}"')
                return None

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return None

    def _update_order_status(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            order_id = data.get('order_id')
            order_status = data.get('order_status')

            if not unique_id or not order_id:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Unique ID or Order ID missing!"')
                return False

            filter_data = {
                'unique_id': unique_id,
                'order_id': order_id
            }

            session_document = {
                'order_status': order_status,
            }

            if order_status == "accepted":
                session_document['session_start_time'] = datetime.now()
                self._update_agent_status(unique_id, "engaged", LOG_PREFIX)

            if order_status == "delivered":
                session_document['session_end_time'] = datetime.now()
                self._update_agent_status(unique_id, "online", LOG_PREFIX)

            log.info("DEBUG 1 : %s" %filter_data)
            log.info("DEBUG 2 : %s" %session_document)

            update_session_order_status = self.db_agent_session._update(filter_q=filter_data, update_data=session_document)

            if update_session_order_status.modified_count > 0:

                order_document = {
                    'order_status': order_status,
                    'updated_at': datetime.now()
                }

                update_order_status = self.db_order_collection._update(filter_q={'order_id': order_id}, update_data=order_document)

                if update_order_status.modified_count > 0:
                    return True
                else:
                    log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Failed to update order status in order collection!"')
                    return False
            else:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Failed to update session status!"')
                return False

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False

    def _update_location(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            agent_location_latitude = data.get('agent_location_latitude')
            agent_location_longitude = data.get('agent_location_longitude')

            filter_data = {
                'unique_id': unique_id
            }
            update_data = {
                'location': {
                    'type': 'Point',
                    'coordinates': [float(agent_location_longitude), float(agent_location_latitude)]
                }
            }
            update_agent_location = self.db_agent_profile._update(filter_q=filter_data, update_data=update_data)

            if update_agent_location.modified_count > 0:
                return True
            else:
                return False

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return {"status": "FAILURE", "message": "Error updating Agent Location"}

    def _delete_agent_profile(self, LOG_PREFIX, unique_id):
        try:
            filter_data = {
                'unique_id': unique_id
            }

            agent_profile_delete = self.db_agent_profile._delete(filter_d=filter_data, multiple=False)

            if agent_profile_delete and agent_profile_delete.deleted_count > 0:
                self.db_agent_session._delete(filter_d=filter_data, multiple=True)
                return True
            else:
                return False

        except Exception as e:
            logging.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False

    def _list_sessions(self, LOG_PREFIX, data):
        try:
            unique_id = data.get('unique_id')
            days_filter = data.get('days_filter', 7)

            if not unique_id:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Unique ID is required!"')
                return False

            if days_filter not in [7, 15, 30]:
                log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"Invalid days filter value!"')
                return False

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_filter)

            filter_data = {
                'unique_id': unique_id,
                'session_end_time': {'$gte': start_date, '$lte': end_date}
            }

            log.info("QUERY :: %s" % filter_data)
            session_list = self.db_agent_session._find_all(filter=filter_data, sort_ts=True)
            log.info("COLLECTION : %s" % self.db_agent_session.coll_name)
            return session_list

        except Exception as e:
            log.error(f'{LOG_PREFIX}, "Result":"Failure", "Reason":"{e}"')
            return False
