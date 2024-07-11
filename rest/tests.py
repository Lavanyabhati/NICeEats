from geopy.distance import geodesic

data1 = {
  "_id": {
    "$oid": "66835dc13e13cede378d4362"
  },
  "res_id": "89A2F684FA0653D1",
  "name": "Dominos",
  "category": "Pizza",
  "location_name": "Kamla Nagar",
  "location": {
    "type": "Point",
    "coordinates": [
      77.20824208363237,
      28.679925373970057
    ]
  },
  "created_at": {
    "$date": "2024-07-02T07:24:09.667Z"
  },
  "updated_at": {
    "$date": "2024-07-02T07:24:09.667Z"
  }
}

data2 = {
  "_id": {
    "$oid": "66835e123e13cede378d4363"
  },
  "res_id": "458DFA76FEE6F982",
  "name": "Sagar Ratna",
  "category": "South Indian",
  "location_name": "Ashok Vihar",
  "location": {
    "type": "Point",
    "coordinates": [
      77.19886868268507,
      28.686258420761057
    ]
  },
  "created_at": {
    "$date": "2024-07-02T07:25:30.661Z"
  },
  "updated_at": {
    "$date": "2024-07-02T07:25:30.661Z"
  }
}
# origin = (data1['location']['coordinates'][0], data1['location']['coordinates'][1])  # (latitude, longitude) don't confuse
# dist = (data2['location']['coordinates'][0], data2['location']['coordinates'][1])


origin = (78.04681486522907, 30.345207115649753)
dist = (77.1779045376542, 28.693655961268426)

print(geodesic(origin, dist).meters)  # 23576.805481751613
print(geodesic(origin, dist).kilometers)  # 23.576805481751613
print(geodesic(origin, dist).miles)  # 14.64994773134371