import requests
import re
import json
from elasticsearch import Elasticsearch


# Auth token
auth = None

# USER API
user_api = "/_xpack/security/user/"

# ROLE_API
role_api = "/_xpack/security/role/"
elasticip = ''

headers = {'Content-type': 'application/json'}


def authenticate(user, password, elasticip_addr):
    global auth, elasticip

    elasticip = elasticip_addr + ":9200"
    '''To authenticate perform a get request on elasticip.
    If status = 200 login is successful'''
    try:
        req = requests.get("http://" + elasticip, auth=(user, password), timeout=3)
    except requests.exceptions.ConnectTimeout:
        return 'Connection timed out'

    except requests.exceptions.ConnectionError:
        return "Connection Error"

    auth = (user, password)
    return req.status_code


def create_user(user, password):
    # CREATE USER
    if password is None:
        password = "qwerty"
    body = '''{
        "password" : "''' + password + '''",
        "roles" : ["kibana_dashboard_only_user", "''' + user.upper() + '''_ROLE"]
    }'''

    print(user, password)
    req = requests.post("http://" + elasticip + user_api + user, auth=auth, headers=headers, data=body)
    if req.status_code == 200:
        print("User: " + user + " created")
    else:
        print("Error creating user \"" + user + "\", Code: " + str(req.status_code) + ", " + req.reason)

    return req.status_code


def create_role(user):
    # CREATE USER ROLE IF NOT EXIST

    body = '''
    {
        "cluster": [],
        "indices":[
            {
                "names":["logstash-*"],
                "privileges":["read", "view_index_metadata"],
				"query" : {"match_phrase_prefix":{"device": "''' + user.upper() + '''"}}
            }
        ]
    }'''

    req = requests.post("http://" + elasticip + role_api + user.upper() + "_ROLE", auth=auth, headers=headers,
                        data=body)
    if req.status_code == 200:
        print("Role: " + user.upper() + "_ROLE " + "created")
    else:
        print("Error creating role for \"" + user + "\", Code: " + str(req.status_code) + ", " + req.reason)

    return req.status_code


def validate(user, password):
    if re.search('[ !@#$%^&*()+=<>.,?/"\';:|\\\[\]{}`~]', user) is not None or user == '':
        return "Bad username"

    if password == "" or re.search(' ', password) is not None or len(password) < 6:
        return "Bad password"


def delete_users(users):
    headers = {'Content-type': 'application/json'}

    for user in users:

        # Delete user
        req = requests.delete("http://" + elasticip + user_api + user, auth=auth, headers=headers)
        if req.status_code == 200:
            print("User: " + user + " deleted")
        else:
            print("Error deleting user(" + user + "): " + str(req.status_code) + ", " + req.reason)

        # Delete role associated with this user
        role = user.upper() + "_ROLE"
        req = requests.delete("http://" + elasticip + role_api + role, auth=auth, headers=headers)
        if req.status_code == 200:
            print("Role: " + role + " deleted")
        else:
            print("Error deleting role(" + role + "): " + str(req.status_code) + ", " + req.reason)


def delete_roles(roles):
    for role in roles:

        # Delete user
        req = requests.delete("http://" + elasticip + role_api + role, auth=auth, headers=headers)
        if req.status_code == 200:
            print("Role: " + role + " deleted")
        else:
            print("Error deleting role(" + user + "): " + str(req.status_code) + ", " + req.reason)


def get_users():
    users = []
    req = requests.get("http://" + elasticip + user_api, auth=auth)
    if req.status_code != 200:
        print("Error getting users, code: " + str(req.status_code) + ", " + req.reason)
        return req

    for username, fields in json.loads(req.text).items():
        if not fields['metadata']:
            if "superuser" in fields['roles']:
                users.append(username + "(superuser)")
            else:
                users.append(username)

    return sorted(users)


def get_roles():
    roles = []
    req = requests.get("http://" + elasticip + role_api, auth=auth)
    if req.status_code != 200:
        print("Error getting roles, code: " + str(req.status_code) + ", " + req.reason)
        return req

    for rolename, fields in json.loads(req.text).items():
        if not fields['metadata']:
            roles.append(rolename)

    return sorted(roles)


def get_devices():
    es = Elasticsearch(elasticip, http_auth=auth)
    devices = []

    query = {
        "size": 0,
        "aggs": {
            "devices": {
                "terms": {
                    "field": "device.keyword",
                    "size": 1000
                }
            }
        },
        "_source": ["device"]
    }

    response = es.search(index="logstash-*", body=query)
    for device in response['aggregations']['devices']['buckets']:
        newdev = ""
        for char in device['key']:
            if char.isalpha():
                newdev += char
            else:
                break

        if newdev not in devices:
            devices.append(newdev)

    return sorted(devices)


def manage_user(user, password):
    devices = get_devices()
    users = get_users()
    roles = get_roles()

    # Create users automatically
    if user is None and password is None:
        for device in devices:
            req = requests.get("http://" + elasticip + user_api + device.lower(), auth=auth, headers=headers)

            if req.status_code == 404:
                if create_user(device.lower(), password) == 200:  # All good, check role
                    if device + "_ROLE" not in roles:
                        create_role(device.lower())
                    else:
                        return None
            else:
                return req

    else:  # Create user manually
        # Check if user exists
        req = requests.get("http://" + elasticip + user_api + user, auth=auth)
        if req.status_code == 404:  # He doesn't exist, so create
            if create_user(user, password) == 200:  # All good, check role
                if user.upper() + "_ROLE" not in roles:
                    create_role(user)
                else:
                    return None
        elif req.status_code == 200:
            print("User \"" + user + "\" already exists")
            return None
        else:
            return req
