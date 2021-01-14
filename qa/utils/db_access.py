import pymongo
from urllib import parse
from bson.objectid import ObjectId
from enum import Enum
import copy
import datetime

mongo_client = None

class AccountType(Enum):
    Publisher = 1
    Publisher_GodMode = 2
    Publisher_Mrec = 3
    Both = 4
    Vungler = 5


def get_database():
    
    from qa.settings import config

    mongo_config = config['mongodb']
    conn_string = "mongodb://%s:%s@qa-vvv-repl-shard-00-00-becyx.mongodb.net:27017,qa-vvv-repl-shard-00-01-becyx.mongodb.net:27017,qa-vvv-repl-shard-00-02-becyx.mongodb.net:27017/vvv-repl?authSource=admin&replicaSet=QA-vvv-repl-shard-0&retryWrites=true&w=majority&ssl=true" % (
                        parse.quote(mongo_config['username']),
                        parse.quote(mongo_config['password'])
                    )
    global mongo_client
    try:
        if mongo_client is None:
            mongo_client = pymongo.MongoClient(conn_string)
        return mongo_client['vvv-repl']
    except Exception as ex:
        raise ex
    return mongo_client['vvv-repl']

# Retrieve account information by object ID
def get_account_info_by_id(obj_id: str):
    query_condition = {'_id': ObjectId(obj_id)}
    return get_database()['accounts'].find_one(query_condition)

# Retrieve account information by passing contract email
def get_account_info(contract_email:str):
    query_condition = {'contactEmail': contract_email}
    return get_database()['accounts'].find_one(query_condition)

# Get user id.
def get_user_id(email):
    query_condition = {'email': email}
    return str(get_database()['people'].find_one(query_condition)['_id'])

# Reset account info that are filled in the account page
def reset_account_info(contact_email):

    try:
        account_info = get_account_info(contact_email)

        account_info['contactPhone'] = ''
        account_info['city'] = ''
        account_info['state'] = ''
        account_info['postal'] = ''
        account_info['address1'] = ''
        account_info['address2'] = ''
        account_info['country'] = ''

        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update(query_condition, account_info)

    except Exception as ex:
        raise ex

# Remove account info (Delete user info from accounts collection and people collection permanently)
def delete_account_info(contact_email):
    get_database()['accounts'].delete_one({'contactEmail': contact_email})
    get_database()['people'].delete_one({'email': contact_email})

# Retrieve user infomation from the people collection
def get_user_info(email_address):
    return get_database()['people'].find_one({'email': email_address})

# Get user token from the people collection
def get_user_activation_token(email_address):
    return get_user_info(email_address)['token']

# Get password reset token from the people collection
def get_reset_password_token(email_address):
    return get_user_info(email_address)['password_reset_token']

# Remove the SDK term from current test account
def remove_sdk_agreement(contact_email):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update(query_condition, {'$unset': {'sdkTermsAgreement':''}})
    except Exception as ex:
        raise ex

# Set the SDK term to an older version
def reset_sdk_agreement_version(contact_email):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update(query_condition,
                                          {'$set': {"sdkTermsAgreement.0.version": "2000-01-01"}}
                                          )
    except Exception as ex:
        raise ex

# Set flat cpm cap value
def set_flat_cpm_cap_value(contact_email:str, cap_val):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update_one(query_condition, 
                                         {'$set': {'flat_cpm_cap' : cap_val}}
                                         )
    except Exception as ex:
        raise ex

# Remove flat cpm cap value
def remove_flat_cpm_cap(contact_email:str):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update_one(query_condition, 
                                         {'$unset': {'flat_cpm_cap' : ''}}
                                         )
    except Exception as ex:
        raise ex

# Set pub_alert_emails
def set_pub_alert_emails(contact_email:str, receipts:list):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update_one(query_condition, 
                                         {'$set': {'pub_alert_emails' : receipts}}
                                         )
    except Exception as ex:
        raise ex

# Remove pub_alert_emails
def remove_pub_alert_emails(contact_email):
    try:
        query_condition = {'contactEmail': contact_email}
        get_database()['accounts'].update_one(query_condition, 
                                         {'$unset': {'pub_alert_emails': ''}}
                                         )
    except Exception as ex:
        raise ex

# Retrieve specific team member info from people collection
def get_specific_team_member_info(email):
    return get_database()['people'].find_one({'email': email})

# Retrieve all team members info from people collection via primary account id
def get_all_team_members_info(primary_account_id, primary_user_name):
    results = []
    for placement in get_database()['people'].find({'$and': [
                                                            {'account': ObjectId(primary_account_id)},
                                                            {'email': {'$ne': primary_user_name}}]}):
        results.append(placement)
    return results

# Delete all team members info from people coll via primary account id
def delete_all_team_members(primary_account_id, primary_account_email):
    result = get_database()['people'].delete_many({'$and': [{'account': ObjectId(primary_account_id)},
                                                            {'email': {'$ne': primary_account_email}}]})
    return result.deleted_count

# Retrieve account id by passing contract email
def get_account_id(contract_email):
    account = get_account_info(contract_email)
    if account is None:
        return None
    return str(account['_id'])

# Retrieve all applications info by account_id
def get_apps_info(account_id):
    results = []
    for app in get_database()['applications'].find({'$or': [{'parentAccount': ObjectId(account_id)},
                                                                 {'owner': ObjectId(account_id)}]}):
        results.append(app)
    return results

# Get the specific application by app id
def get_app_info(app_id):
    return get_database()['applications'].find_one({'_id': ObjectId(app_id)})

# Get the specific placement by placement id
def get_placement(placement_id):
    return get_database()['placements'].find_one({'_id': ObjectId(placement_id)})


# Get app info by app name and id
def get_app_info_by_name(account_id, app_name):
    return get_database()['applications'].find_one({'$or': [{'parentAccount': ObjectId(account_id), 'name': app_name},
                                                            {'owner': ObjectId(account_id), 'name': app_name}]})

# get the specific placement from the app
def get_placement_info(app_id, placement_reference_id):
    return get_database()['placements'].find_one({'application_id': ObjectId(app_id),
                                                  'reference_id': placement_reference_id})

# Get placements information
def get_placements_info(app_id):
    results = []
    for placement in get_database()['placements'].find({'application_id': ObjectId(app_id)}):
        results.append(placement)
    return results

# Delete one specific app
def delete_app(app_id):
    result = get_database()['applications'].delete_one({'_id': ObjectId(app_id)})
    return result.deleted_count

# Delete the specified placement by placement id
def delete_placement(placement_id):
    result = get_database()['placements'].delete_one({'_id': ObjectId(placement_id)})
    return result.deleted_count

# Delete all associated applications
def delete_all_apps(account_id):
    result = get_database()['applications'].delete_many({'$or': [{'parentAccount': ObjectId(account_id)},
                                                                 {'owner': ObjectId(account_id)}]})
    return result.deleted_count

# Delete all associated placements
def delete_all_placements(account_id):
    result = get_database()['placements'].delete_many({'account_id': ObjectId(account_id)})
    return result.deleted_count


# Delete all associated notification of a given user
def delete_all_notifications(user_id):
    result = get_database()['notifications'].delete_many({'user': ObjectId(user_id)})
    return result.deleted_count


# Delete all test apps and associated placement data from a given user account id
def delete_apps_data(account_id):
    delete_all_apps(account_id)
    delete_all_placements(account_id)

# Insert application test data(Test mode, not live on store)
def insert_app_test_data(account_id, app_name, platform, status='t', created_date=None):

    import random
    import string

    app_data = copy.deepcopy(_app_test_data_template)

    app_data['name'] = app_name
    app_data['parentAccount'] = ObjectId(account_id)
    # Fill in storeId with a random string to avoid duplicate key error when inserting app test data
    app_data['storeId'] = ''.join(random.sample(string.ascii_letters + string.digits, 12))

    if created_date is None:
        app_data['dateCreated'] = datetime.datetime.utcnow()
        app_data['date_last_store_refresh'] = datetime.datetime.utcnow()
    else:
        app_data['dateCreated'] = created_date
        app_data['date_last_store_refresh'] = created_date

    app_data['platform'] = platform

    if not status in ['a', 't', 'i']:
        raise Exception('Incorrect status value')

    app_data['status'] = status

    try:
        result = get_database()['applications'].insert_one(app_data)
        app_id = result.inserted_id

        # If the app doesn't live on store, then the storeId should take the value of app id 
        get_database()['applications'].update_one({"_id": app_id}, {"$set": {"storeId": str(app_id)}})
        
        # Insert a default interstitial placement for the new app
        insert_placement_data(account_id, app_id, 'default', 'Interstitial', 
                              is_archived=False, created_date=created_date)
        return str(app_id)
    
    except Exception as ex:
        raise ex

# Insert a live app test
def insert_live_app_test_data(account_id, app_name, platform, created_date=None):
    
    try:
        app_id = insert_app_test_data(account_id, app_name, platform, status='a', created_date=created_date)

        assert type(app_id), str
        # Update the app, set marketId, storeUrl
        get_database()['applications'].update_one({"_id": ObjectId(app_id)}, {"$set": {"marketId": "1131184101", 
                                                                              "storeUrl": "https://itunes.apple.com/cn/app/id1131184101",
                                                                              "category": "Games"}})
        
        return app_id
    except Exception as ex:
        raise ex


# Insert multiple app test data on specific platform
def insert_multiple_apps_data(account_id, app_name_list, platform):
    import random
    import string

    if type(app_name_list)!=list:
        raise Exception('The parameter app_name_list should a list type')
    
    # Define a app data list, all apps in this list will be bulk written to the MongoDb
    apps_data_list = []

    for app_name in app_name_list:
        app_data = copy.deepcopy(_app_test_data_template)
        app_data['name'] = app_name
        app_data['parentAccount'] = ObjectId(account_id)
        app_data['dateCreated'] = datetime.datetime.utcnow()
        app_data['date_last_store_refresh'] = datetime.datetime.utcnow()
        app_data['platform'] = platform
        # Fill in storeId with a random string to avoid duplicate key error when inserting app test data
        app_data['storeId'] = ''.join(random.sample(string.ascii_letters + string.digits, 12))

        apps_data_list.append(app_data)
    
    inserted_app_ids = []

    try:
        result = get_database()['applications'].insert_many(apps_data_list)
        
        for obj_id in result.inserted_ids:
            inserted_app_ids.append(str(obj_id))
        
        for app_id in inserted_app_ids:
            # Update the store id, apply the value of app_id to the field storeID
            get_database()['applications'].update_one({"_id": ObjectId(app_id)}, {"$set": {"storeId": app_id}})
            # Insert default interstital placment for the new app            
            insert_placement_data(account_id, app_id, 'default', 'Interstitial', 
                                  is_archived=False, created_date = datetime.datetime.utcnow())

        return inserted_app_ids

    except Exception as ex:
        raise ex


# Insert multiple placement data for specific app
def insert_multiple_placements_data(account_id, app_id, placement_name_list, placement_type, created_date=None):

    if type(placement_name_list)!=list:
        raise Exception('The parameter placement_name_list should a list type')

    valid_placement_types = ['Interstitial', 'Rewarded', 'BannerVideo', 'InFeed']

    if placement_type not in valid_placement_types:
        raise Exception('Incorrect parameter of placement type')
    
    # Define a placement data list will be bulk written to the MongoDb
    placement_data_list = []

    for placement_name in placement_name_list:
        placement_data = build_placement_data(account_id, app_id, placement_name, placement_type, created_date)
        placement_data_list.append(placement_data)
    
    inserted_placement_ids = []

    try:
        result = get_database()['placements'].insert_many(placement_data_list)

        for obj_id in result.inserted_ids:
            inserted_placement_ids.append(str(obj_id))

        return inserted_placement_ids

    except Exception as ex:
        raise ex

# Build user data
def build_user_data(account_id, first_name, last_name, email_address, created_date=None):
    
    user_data = copy.deepcopy(_user_data_template)

    user_data['firstName'] = first_name
    user_data['lastName'] = last_name
    user_data['account'] = ObjectId(account_id)
    user_data['email'] = email_address

    if created_date is None:
        user_data['dateCreated'] = datetime.datetime.utcnow()
        user_data['dateModified'] = datetime.datetime.utcnow()
    else:
        user_data['dateCreated'] = created_date
        user_data['dateModified'] = created_date
    
    return user_data

# Insert multiple users data
def insert_multiple_users_data(account_id, users_info_list, created_date=None):
    
    # Define user data list that will be bulk written to the MongoDB
    users_data_list = []
    
    for user_info in users_info_list:
        user_data = build_user_data(account_id, user_info['first_name'], user_info['last_name'], user_info['email_address'], created_date)
        users_data_list.append(user_data)
    
    inserted_user_ids = []

    try:
        result = get_database()['people'].insert_many(users_data_list)
        
        for obj_id in result.inserted_ids:
            inserted_user_ids.append(str(obj_id))

        return inserted_user_ids

    except Exception as ex:
        raise ex

# Insert an individual user data
def insert_user_data(account_id, first_name, last_name, email_address, created_date=None):
    user_data = build_user_data(account_id, first_name, last_name, email_address, created_date)
    try:
        result = get_database()['people'].insert_one(user_data)
        user_id = result.inserted_id
        return str(user_id)
    except Exception as ex:
        raise ex

# Build placement data
def build_placement_data(account_id, app_id, placement_name, placement_type, created_date=None):
    
    from random import randrange

    valid_placement_types = ['Interstitial', 'Rewarded', 'BannerVideo', 'InFeed', 'MREC']

    if placement_type not in valid_placement_types:
        raise Exception('Incorrect parameter of placement type: %s' % placement_type)

    placement_data = copy.deepcopy(_placement_test_data_template)

    placement_data['name'] = placement_name
    placement_data['reference_id'] = "%s-%d" % (placement_name.upper(), randrange(1000000, 9999999))
    placement_data['account_id'] = ObjectId(account_id)
    placement_data['application_id'] = ObjectId(app_id)
    if created_date is None:
        placement_data['created'] = datetime.datetime.utcnow()
        placement_data['updated'] = datetime.datetime.utcnow()
        placement_data['dateModified'] = datetime.datetime.utcnow()
    else:
        placement_data['created'] = created_date
        placement_data['updated'] = created_date
        placement_data['dateModified'] = created_date

    # Update fields based on placement type
    if placement_type == valid_placement_types[1]:  #Rewarded
        placement_data['is_incentivized'] = True
    elif placement_type == valid_placement_types[2]:  #BannerVideo
        placement_data['supported_template_types'] = ['multi_page_flexview', 'single_page_flexview']
        placement_data['supported_ad_formats'] = ['vungle_mraid']
    elif placement_type == valid_placement_types[3]:  #InFeed
        placement_data['supported_template_types'] = [ 'multi_page_flexfeed', 'single_page_flexfeed']
        placement_data['supported_ad_formats'] = ['vungle_mraid']
    elif placement_type == valid_placement_types[4]:  #MREC
        placement_data['supported_template_types'] = ['multi_page_mrec', 'single_page_mrec']
        placement_data['supported_ad_formats'] = ['vungle_mraid']

    return placement_data

# Insert placement test data
def insert_placement_data(account_id, app_id, placement_name, placement_type, is_archived=False, created_date=None):

    placement_data = build_placement_data(account_id, app_id, placement_name, placement_type, created_date)
    # Update placement.is_archived
    placement_data['is_archived'] = is_archived

    try:
        result = get_database()['placements'].insert_one(placement_data)
        placement_id = result.inserted_id
        return str(placement_id)
    except Exception as ex:
        raise ex

# Insert team member test data
def insert_team_member_data(primary_account_id, firstName, lastName, email, alive=False, role='read'):

    if role not in ['write', 'read']:
        raise Exception('Incorrect role parameter')

    team_member_data = copy.deepcopy(_team_member_data_template)

    team_member_data['firstName'] = firstName
    team_member_data['lastName'] = lastName
    team_member_data['account'] = ObjectId(primary_account_id)
    team_member_data['email'] = email
    team_member_data['alive'] = alive
    team_member_data['role'] = role

    team_member_data['dateCreated'] = datetime.datetime.utcnow()
    team_member_data['dateModified'] = datetime.datetime.utcnow()

    try:
        result = get_database()['people'].insert_one(team_member_data)
        id = result.inserted_id
        return {'id': str(id), 'first_name': firstName, 'last_name':lastName, 'email': email}
    except Exception as ex:
        raise ex

# Create a new test account
def create_test_account(account_type:AccountType, name=None, email=None):
    import string, random
    # Generate random string for email
    def randomString(stringLength=6):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))
    # Generate random email address if it's not provided in the parameter
    if email is None:
        if account_type == AccountType.Publisher:
            email = 'pub_%s@qa.com' % randomString()
        elif account_type == AccountType.Both:
            email = 'both_%s@qa.com' % randomString()
        elif account_type == AccountType.Publisher_GodMode:
            email = 'p_god_%s@qa.com' % randomString()
        elif account_type == AccountType.Publisher_Mrec:
            email = 'p_mrec_%s@qa.com' % randomString()
        elif account_type == AccountType.Vungler:
            email = 'v_%s@qa.com' % randomString()
    # Build account data and insert it to the accounts collection
    try:
        account_data = build_account_data(email, account_type)
        if name is not None:
            account_data['name'] = name
        result = get_database()['accounts'].insert_one(account_data)
        account_id = str(result.inserted_id)
    except Exception as ex:
        raise ex
    
    # Build user data and insert it to the users collection
    user_data = build_user_data(account_id, 'QA', 'Automation', email)
    user_data['alive']=True
    # Grant different permission based on account type 
    if account_type == AccountType.Publisher_GodMode:
        user_data['permissions']['pub_godmode'] = True
    if account_type == AccountType.Publisher_Mrec:
        user_data['permissions']['placements'] = {"mrec": {"write": True}}
    if account_type == AccountType.Vungler:
        user_data['role'] = 'vungler'
        user_data['permissions']['admin']= {"access": True}
    try:
        get_database()['people'].insert_one(user_data)
    except Exception as ex:
        raise ex
    
    return {'account_id': account_id, 'email': email, 'name': name}

def build_account_data(email:str, account_type:AccountType):
    account_data = copy.deepcopy(_pub_account_data_template)

    account_data['contactEmail'] = email
    account_data['dateCreated'] = datetime.datetime.utcnow()
    account_data['dateModified'] = datetime.datetime.utcnow()
    account_data['sdkTermsAgreement'][0]['email'] = email
    account_data['sdkTermsAgreement'][0]['acceptedDate'] = datetime.datetime.utcnow()
    account_data['updated'] = datetime.datetime.utcnow()

    if account_type == AccountType.Both:
        account_data['notifications_email'] = 'grow@vungle.com'
        account_data['is_approval_exempt_campaigns'] = True
        account_data['permissions']['access-grow-vungle-com'] = True
        account_data['accountType'] = 'both'

    return account_data

def insert_sdk_candidate():
    try:
        result = get_database()['sdk_candidates'].insert_one(_sdk_candidate)
        return str(result.inserted_id)
    except Exception as ex:
        raise ex

def delete_sdk_candidate(sdk_candidate_id:str):
    result = get_database()['sdk_candidates'].delete_one({'_id': ObjectId(sdk_candidate_id)})
    return result.deleted_count

_pub_account_data_template = {
    "contactName" : "Vungle",
    "contactEmail" : None,
    "name" : "QA Automation",
    "is_budget_pacing" : True,
    "budget_type" : "prepay",
    "registration_source" : "auth",
    "sdkTermsAgreement" : [ 
        {
            "email" : None,
            "acceptedDate" : None,
            "version" : "2018-04-18",
            "_id" : ObjectId("5ca46bb9ee022200102ba7b3")
        }
    ],
    "account_app_blacklist" : [],
    "dateModified" : None,
    "dateCreated" : None,
    "permissions" : {
        "placements" : {
            "cpm_floor" : {
                "write" : False,
                "read" : False
            }
        }
    },
    "accountType" : "publisher",
    "country" : "US",
    "contactPhone" : "",
    "state" : "",
    "postal" : "",
    "city" : "",
    "address2" : "",
    "address1" : "",
    "is_deleted" : False,
    "__v" : 1,
    "updated" : None
}

_user_data_template = {
    "firstName" : None,
    "lastName" : None,
    "account" : None,
    "email" : None,
    "password" : "$2a$10$pJ5SN.C2dX9uKe3f3wjy7uqTEadHEFX2c5GRTnXjIM/VLytK32XsW",
    "password_reset_token" : "12ed2082f825ec2cd71d",
    "secretKey" : "d638ea6d28152dab16fd30a2dd28c798",
    "permissions" : {},
    "token" : "39b4d4c973bf93b712988dda50d6d9a80a61c8d66507c594ca40f53f6c809b219ed39a60ce4dc27bbd1b599daaa37761",
    "loginCount" : 0,
    "dateModified" : None,
    "dateCreated" : None,
    "admin" : False,
    "alive" : False,
    "emailOptIn" : True,
    "avatar_url" : "",
    "role" : "write",
    "is_deleted" : False,
    "__v" : 0
}

_app_test_data_template = {
    "category" : "",
    "name" : None,
    "platform" : None,
    "parentAccount" : None,
    "date_last_store_refresh": None,
    "minOs" : 6,
    "storeId" : "",
    "storeUrl" : "",
    "marketId" : "",
    "isFree" : False,
    "callbackURL" : "",
    "s2sSecret" : None,
    "isManual" : False,
    "vikingSubcategories" : [],
    "vikingCategories" : [],
    "vikingMaturityMinAge" : 0,
    "vikingDeviceWhitelist" : [],
    "vikingGeoBlacklist" : [],
    "perComplete" : 0,
    "archived" : False,
    "dailyViewLimit" : 20,
    "totalInstalls" : 0,
    "viewLookBackPeriod" : 0,
    "clickLookBackPeriod" : 14,
    "pubTagWhitelist" : [],
    "pubTagBlacklist" : [],
    "pubWhitelist" : [],
    "pubBlacklist" : [],
    "dashboardVersion" : "3.0",
    "adServerConfigs" : [],
    "allowedAdTypes" : "all",
    "allowedDeliveryTypes" : "both",
    "serving_cost_revenue_share" : 0.03,
    "hostingCostsEnabled" : True,
    "cpm" : 0,
    "revShare" : 0.45,
    "adTagBlacklist" : [],
    "adTagWhitelist" : [],
    "adWhitelist" : [],
    "adBlacklist" : [],
    "allowABTemplateTests" : False,
    "supported_template_types" : [
        "single_page_flexfeed",
        "multi_page_flexfeed",
        "single_page_flexview",
        "multi_page_flexview",
        "single_page_fullscreen",
        "multi_page_fullscreen"
    ],
    "ignoreCreativeCaps" : False,
    "isCoppaCompliant" : False,
    "replacements" : [
        {
            "key" : "CLOSE_BUTTON_DELAY_SECONDS",
            "value" : "9999",
            "_id" : ObjectId("5c480c7142ca260018e916a7")
        },
        {
            "key" : "EC_CLOSE_BUTTON_DELAY_SECONDS",
            "value" : "0",
            "_id" : ObjectId("5c480c7142ca260018e916a6")
        },
        {
            "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
            "value" : "9999",
            "_id" : ObjectId("5c480c7142ca260018e916a5")
        },
        {
            "key" : "INCENTIVIZED_BODY_TEXT",
            "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
            "_id" : ObjectId("5c480c7142ca260018e916a4")
        },
        {
            "key" : "INCENTIVIZED_CLOSE_TEXT",
            "value" : "Close",
            "_id" : ObjectId("5c480c7142ca260018e916a3")
        },
        {
            "key" : "INCENTIVIZED_CONTINUE_TEXT",
            "value" : "Continue",
            "_id" : ObjectId("5c480c7142ca260018e916a2")
        },
        {
            "key" : "INCENTIVIZED_TITLE_TEXT",
            "value" : "Close this ad?",
            "_id" : ObjectId("5c480c7142ca260018e916a1")
        },
        {
            "key" : "SHOW_OVERLAY_WHEN",
            "value" : "delayed",
            "_id" : ObjectId("5c480c7142ca260018e916a0")
        },
        {
            "key" : "START_MUTED",
            "value" : "False",
            "_id" : ObjectId("5c480c7142ca260018e9169f")
        },
        {
            "key" : "VIDEO_CLOSE_BUTTON_DELAY_SECONDS",
            "value" : "0",
            "_id" : ObjectId("5c480c7142ca260018e9169e")
        },
        {
            "key" : "VIDEO_CROP",
            "value" : "False",
            "_id" : ObjectId("5c480c7142ca260018e9169d")
        },
        {
            "key" : "VIDEO_PROGRESS_BAR",
            "value" : "True",
            "_id" : ObjectId("5c480c7142ca260018e9169c")
        }
    ],
    "templates" : [
        ObjectId("5c2f4b06907de96b0a50421e"),
        ObjectId("5bfca005a314133a89cc655f"),
        ObjectId("5b36d9c1970118222f6e909c"),
        ObjectId("5b36d9a37ca6ee1c67fc7ae8"),
        ObjectId("5b35b64db21b17240c09a7df"),
        ObjectId("5b35b632651bdc1e35d55663"),
        ObjectId("5a3a22d4befa3f4d0c007309"),
        ObjectId("59e668a90d2286431700ef46"),
        ObjectId("59e66854fa5a56611700d8b1"),
        ObjectId("59e6616ad02db4551700d21f"),
        ObjectId("59e660defa5a56611700d72d"),
        ObjectId("59ceba760d228643170008e5"),
        ObjectId("59ceb8c9fa5a56611700098e"),
        ObjectId("596fe17693b39c6c5600336d"),
        ObjectId("596fe0bf46486a7e5600360b"),
        ObjectId("594d7a11214509f41a00257f"),
        ObjectId("5928b144cc4c8fff46000040"),
        ObjectId("58dd7fd14fcd779438000065"),
        ObjectId("58cc6de9b1557a9918000454"),
        ObjectId("58cc6cd1e73be38618000552"),
        ObjectId("58c2f62c34f5e387180003fa"),
        ObjectId("58b0dad4307d9d0f3c000053"),
        ObjectId("58a4ec0023112c970700023d"),
        ObjectId("58a4ebb82ad3568507000333"),
        ObjectId("58a4eb872ad35685070002e2"),
        ObjectId("58865198caedc66d7f0002c4"),
        ObjectId("58829a7710f77a617f00004d"),
        ObjectId("57f812d93e4d63c13c000038"),
        ObjectId("57eea7983c5937912400002c"),
        ObjectId("57eea58b0f747e8424000051"),
        ObjectId("57ed5ef40f747e8424000035"),
        ObjectId("57d0a0835a4630344c000083"),
        ObjectId("5d027ce452f61a1927f0eb6d"), 
        ObjectId("5d7936a80ed7e506be620bf0"), 
        ObjectId("5d7936c86c82da06b7490cd7"), 
        ObjectId("5d810bbf2102142176dd5b86"), 
        ObjectId("5da986bb1a64cc439bb34b76"), 
        ObjectId("5da98734fbf2af43a2aa4972"),
        ObjectId("5dd6d4357045313e374d3656"),
        ObjectId("5dd6d4614dbb883e43b03be8")
    ],
    "eligibleTemplates" : [
        {
            "template" : ObjectId("57d0a0835a4630344c000083"),
            "_id" : ObjectId("5c480c7142ca260018e917b7"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917be"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917bd"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917bc"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917bb"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917ba"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917b9"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e917b8"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("57ed5ef40f747e8424000035"),
            "_id" : ObjectId("5c480c7142ca260018e917af"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917b6"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917b5"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917b4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917b3"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917b2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917b1"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e917b0"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("57eea58b0f747e8424000051"),
            "_id" : ObjectId("5c480c7142ca260018e917a6"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917ae"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917ad"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917ac"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917ab"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917aa"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917a9"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e917a8"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e917a7"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("57eea7983c5937912400002c"),
            "_id" : ObjectId("5c480c7142ca260018e9179d"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917a5"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e917a4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917a3"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917a2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917a1"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e917a0"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9179f"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9179e"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("57f812d93e4d63c13c000038"),
            "_id" : ObjectId("5c480c7142ca260018e91795"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9179c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9179b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9179a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91799"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91798"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91797"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91796"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58829a7710f77a617f00004d"),
            "_id" : ObjectId("5c480c7142ca260018e9178c"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91794"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91793"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91792"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91791"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91790"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9178f"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9178e"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9178d"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58865198caedc66d7f0002c4"),
            "_id" : ObjectId("5c480c7142ca260018e91783"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9178b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9178a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91789"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91788"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91787"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91786"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91785"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91784"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58a4eb872ad35685070002e2"),
            "_id" : ObjectId("5c480c7142ca260018e9177a"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91782"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91781"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91780"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9177f"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9177e"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9177d"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9177c"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9177b"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58a4ebb82ad3568507000333"),
            "_id" : ObjectId("5c480c7142ca260018e91771"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91779"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91778"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91777"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91776"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91775"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91774"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91773"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91772"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58a4ec0023112c970700023d"),
            "_id" : ObjectId("5c480c7142ca260018e91768"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91770"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9176f"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9176e"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9176d"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9176c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9176b"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9176a"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91769"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58b0dad4307d9d0f3c000053"),
            "_id" : ObjectId("5c480c7142ca260018e9175f"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91767"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91766"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91765"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91764"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91763"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91762"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91761"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91760"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58c2f62c34f5e387180003fa"),
            "_id" : ObjectId("5c480c7142ca260018e91757"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9175e"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9175d"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9175c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9175b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9175a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91759"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91758"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58cc6cd1e73be38618000552"),
            "_id" : ObjectId("5c480c7142ca260018e9174e"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91756"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91755"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91754"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91753"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91752"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91751"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91750"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9174f"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58cc6de9b1557a9918000454"),
            "_id" : ObjectId("5c480c7142ca260018e91745"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9174d"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9174c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9174b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9174a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91749"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91748"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91747"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91746"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("58dd7fd14fcd779438000065"),
            "_id" : ObjectId("5c480c7142ca260018e9173d"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91744"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91743"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91742"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91741"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91740"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9173f"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9173e"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5928b144cc4c8fff46000040"),
            "_id" : ObjectId("5c480c7142ca260018e91735"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9173c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9173b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9173a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91739"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91738"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91737"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91736"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("594d7a11214509f41a00257f"),
            "_id" : ObjectId("5c480c7142ca260018e9172d"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91734"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91733"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91732"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91731"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91730"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9172f"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9172e"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("596fe0bf46486a7e5600360b"),
            "_id" : ObjectId("5c480c7142ca260018e91724"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9172c"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9172b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9172a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91729"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91728"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91727"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91726"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91725"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("596fe17693b39c6c5600336d"),
            "_id" : ObjectId("5c480c7142ca260018e9171c"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91723"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91722"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91721"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91720"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9171f"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9171e"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9171d"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59ceb8c9fa5a56611700098e"),
            "_id" : ObjectId("5c480c7142ca260018e91712"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9171b"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e9171a"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91719"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91718"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91717"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91716"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91715"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_CROP",
                    "value" : "False",
                    "name" : "Video Crop",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91714"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91713"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59ceba760d228643170008e5"),
            "_id" : ObjectId("5c480c7142ca260018e9170a"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91711"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91710"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9170f"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9170e"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9170d"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e9170c"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e9170b"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59e660defa5a56611700d72d"),
            "_id" : ObjectId("5c480c7142ca260018e91701"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91709"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91708"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91707"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91706"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91705"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e91704"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91703"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e91702"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59e6616ad02db4551700d21f"),
            "_id" : ObjectId("5c480c7142ca260018e916f7"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e91700"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916ff"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916fe"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916fd"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916fc"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916fb"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916fa"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_CROP",
                    "value" : "False",
                    "name" : "Video Crop",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916f9"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916f8"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59e66854fa5a56611700d8b1"),
            "_id" : ObjectId("5c480c7142ca260018e916ef"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916f6"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916f5"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916f4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916f3"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916f2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916f1"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916f0"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("59e668a90d2286431700ef46"),
            "_id" : ObjectId("5c480c7142ca260018e916e7"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916ee"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916ed"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ec"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916eb"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ea"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916e9"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916e8"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5a3a22d4befa3f4d0c007309"),
            "_id" : ObjectId("5c480c7142ca260018e916df"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916e6"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916e5"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916e4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916e3"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916e2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916e1"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916e0"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5b35b632651bdc1e35d55663"),
            "_id" : ObjectId("5c480c7142ca260018e916d5"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916de"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916dd"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916dc"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916db"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916da"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916d9"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916d8"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916d7"),
                    "priority" : 20
                },
                {
                    "key" : "SHOW_OVERLAY_WHEN",
                    "value" : "delayed",
                    "name" : "Show Overlay when",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916d6"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5b35b64db21b17240c09a7df"),
            "_id" : ObjectId("5c480c7142ca260018e916cb"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916d4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916d3"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916d2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916d1"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916d0"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916cf"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916ce"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916cd"),
                    "priority" : 20
                },
                {
                    "key" : "SHOW_OVERLAY_WHEN",
                    "value" : "delayed",
                    "name" : "Show Overlay when",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916cc"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5b36d9a37ca6ee1c67fc7ae8"),
            "_id" : ObjectId("5c480c7142ca260018e916c3"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916ca"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916c9"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916c8"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916c7"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916c6"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916c5"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916c4"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5b36d9c1970118222f6e909c"),
            "_id" : ObjectId("5c480c7142ca260018e916ba"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916c2"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916c1"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916c0"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916bf"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916be"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916bd"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916bc"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916bb"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5bfca005a314133a89cc655f"),
            "_id" : ObjectId("5c480c7142ca260018e916b1"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916b9"),
                    "priority" : 20
                },
                {
                    "key" : "EC_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "0",
                    "name" : "EndCard Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916b8"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916b7"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916b6"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916b5"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916b4"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916b3"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "0",
                    "name" : "Video Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916b2"),
                    "priority" : 20
                }
            ]
        },
        {
            "template" : ObjectId("5c2f4b06907de96b0a50421e"),
            "_id" : ObjectId("5c480c7142ca260018e916a8"),
            "replacements" : [
                {
                    "key" : "CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916b0"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_BUTTON_DELAY_SECONDS",
                    "value" : "9999",
                    "name" : "Incentivized Close Button Delay",
                    "type" : "INT",
                    "_id" : ObjectId("5c480c7142ca260018e916af"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_TITLE_TEXT",
                    "value" : "Close this ad?",
                    "name" : "Incentivized Dialog Title Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ae"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_BODY_TEXT",
                    "value" : "Are you sure you want to skip this ad? You must finish watching to claim your reward.",
                    "name" : "Incentivized Dialog Body text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ad"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CLOSE_TEXT",
                    "value" : "Close",
                    "name" : "Incentivized Dialog Close Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ac"),
                    "priority" : 20
                },
                {
                    "key" : "INCENTIVIZED_CONTINUE_TEXT",
                    "value" : "Continue",
                    "name" : "Incentivized Dialog Continue Button Text",
                    "type" : "STRING",
                    "_id" : ObjectId("5c480c7142ca260018e916ab"),
                    "priority" : 20
                },
                {
                    "key" : "START_MUTED",
                    "value" : "False",
                    "name" : "Start Muted",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916aa"),
                    "priority" : 20
                },
                {
                    "key" : "VIDEO_PROGRESS_BAR",
                    "value" : "True",
                    "name" : "Video Progress Bar",
                    "type" : "BOOLEAN",
                    "_id" : ObjectId("5c480c7142ca260018e916a9"),
                    "priority" : 20
                }
            ]
        }
    ],
    "connection" : "all",
    "minVideoLength" : 0,
    "maxVideoLength" : 45,
    "forceViewIncentivized" : True,
    "forceView" : True,
    "adDelay" : 0,
    "tagFilters" : {
        "defaultAction" : "show"
    },
    "dateCreated" : None,
    "logRequests" : False,
    "logInstalls" : False,
    "orientation" : "both",
    "tags" : [
        "ios_content-unrated"
    ],
    "store_iab" : [],
    "type" : "publisher",
    "status" : "t",
    "is_deleted" : False,
    "__v" : 0
}

_placement_test_data_template = {
    "name": None,
    "reference_id": None,
    "account_id": None,
    "application_id": None,
    "orientation_override": "none",
    "is_skippable": False,
    "default_cpm_floor": None,
    "daily_delivery_limit": None,
    "supported_template_types": [
        "single_page_fullscreen",
        "multi_page_fullscreen"
    ],
    "is_incentivized": False,
    "data_revision": 1,
    "supported_ad_formats": [
        "vungle_local",
        "third_party",
        "vungle_mraid",
        "vungle_short_form"
    ],
    "is_archived": False,
    "is_auto_cached": True,
    "is_deleted": False,
    "dateModified": None,
    "created": None,
    "updated": None
}

_team_member_data_template = {
    "firstName": None,
    "lastName": None,
    "account": None,
    "email": None,
    "password": "$2a$10$ES8XrX.nHrIB6J7QYdelruureysQYcaVbweNJK80p.z2To8Smmf9G",
    "password_reset_token" : "465d90a5f05b2cfe593c",
    "secretKey" : "268ac39e7843fe792d1ee12301e7d248",
    "token" : "0f550a249133bb07bf03583cd988ed06315db8bf67bc4ee9763ffcae847a19a11ebbbdf5f001b44314598b08211e8daa",
    "loginCount": 0,
    "dateModified": None,
    "dateCreated": None,
    "admin": False,
    "alive": None,
    "emailOptIn": True,
    "avatar_url": "",
    "role": None,
    "is_deleted": False,
    "__v": 0
}

_sdk_candidate = {
    "status" : "active",
    "version" : "6.8.8",
    "release_date" : "11/25/3018",
    "release_notes" : [ 
        "We’ve updated the SDK to support iOS 12.", 
        "StoreKit support for MRAID ads."
    ],
    "links" : {
        "change_log" : "https://github.com/Vungle/iOS-SDK/blob/master/CHANGELOG.md",
        "get_started" : "https://support.vungle.com/hc/en-us/articles/360002925791",
        "sample_app" : "https://github.com/Vungle/iOS-SDK/tree/master",
        "swift" : "https://support.vungle.com/hc/en-us/articles/360002911212"
    },
    "downloads" : {
        "cocoapods" : "https://support.vungle.com/hc/en-us/articles/360002925791#Cocoapods",
        "sdk" : "https://cdn-lb.vungle.com/sdks/ios/Vungle632.zip"
    },
    "img" : "/img/ios_image.svg",
    "name" : "ios",
    "type" : "sdks",
    "config" : "sdk_config"
}