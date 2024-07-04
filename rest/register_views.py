from datetime import datetime
from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt

# from FoodApp.settings import MONGO_DB


class Register():
    def __init__(self):
        self.db = MONGO_DB
        self.collection = 'restaurant'

    @csrf_exempt
    def _add_owner_details(self, data):
        db = self.db
        coll = self.collection

        try:
            name = data.get('name')
            mobile_number = data.post('mobile_number')
            address = data.get('address')
            email = data.get('email')
            age = data.get('age')
            gender = data.get('gender')
            verification_id = data.get('verification_id')
            verification_type = data.get('verification_type')

            rest_document = {
                'name': name,
                'mobile_number': mobile_number,
                'address': address,
                'email': email,
                'age': age,
                'gender': gender,
                'profile_type': 'OWNER',
                'verification_id': verification_id,
                'verification_type': verification_type,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_res_owner = db[coll].insert_one(rest_document)
            print("Restaurant profile saved successfully!")
            return True if insert_res_owner.inserted_id else False
        except Exception as e:
            print("Exception in Register._Register_res_owner(). Reason : %s" % e)
            return None

    @csrf_exempt
    def _add(self, data):
        db = self.db
        coll = self.collection
        try:
            res_name = data.get('name')
            category = data.get('category')
            location_name = data.get('location_name')
            location_lat = data.get('latitude')
            location_long = data.get('longitude')

            data_dict = {
                'name': res_name,
                'category': category,
                'location_name': location_name,
                'location': {
                    'type': 'Point',
                    'coordinates': [float(location_long), float(location_lat)]
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            insert_res = db[coll].insert_one(data_dict)
            return True if insert_res.inserted_id else False
        except Exception as e:
            print("Exception in Register._add(). Reason: %s" % e)
            return None

    @csrf_exempt
    def _list(self, data):
        db = self.db
        coll = self.collection
        try:
            lat = data.get('lat')
            long = data.get('long')
            max_distance = data.get('max_distance', 5000)  # Default to 5km

            query = {
                'coordinates': {
                    '$near': {
                        '$geometry': {
                            'type': 'Point',
                            'coordinates': [float(long), float(lat)]
                        },
                        '$maxDistance': max_distance
                    }
                }
            }
            res_list = list(db[coll].find(query))
            return res_list

        except Exception as e:
            print("Exception in Register._list(). Reason: %s" % e)
            return None

    @csrf_exempt
    def _update_db(self, res_id, data):
        db = self.db
        coll = self.collection
        try:
            data_dict = {
                'name': data.get('name'),
                'location': data.get('location'),
                'coordinates': {
                    'type': 'Point',
                    'coordinates': [data.get('long'), data.get('lat')]
                },
                'updated_at': datetime.now(),
            }
            res_update = db[coll].update_one({'_id': ObjectId(res_id)}, {'$set': data_dict})
            return res_update.modified_count > 0
        except Exception as e:
            print("Exception in Register._update_db(). Reason: %s" % e)
            return None

    @csrf_exempt
    def _delete(self, res_id):
        db = self.db
        coll = self.collection
        try:
            res_delete = db[coll].delete_one({'_id': ObjectId(res_id)})
            return res_delete.deleted_count > 0
        except Exception as e:
            print("Exception in Register._delete(). Reason: %s" % e)
            return None
