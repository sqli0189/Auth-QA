import json

from qa.utils import db_access as db

# Load config
config = None

_json_config_file = 'config.json'

with open(_json_config_file) as config_file:
    config = json.load(config_file)

auth_test_cfg = config['test_env']['auth']

test_env_type = config['test_env']['type']

test_accounts = config['test_accounts']

pub_test_account = test_accounts['pub']
adv_test_account = test_accounts['adv']
both_test_account = test_accounts['both']
pub_admin_test_account = test_accounts['pub_admin']

# Valid vungle source values - Mission Ctrl needs it
vungle_src_values = ['pub', 'adv', 'admin', 'foo']

#Auth API Endpoints#
auth_status_endpoint = 'https://%s/status' % auth_test_cfg['host']
auth_login_endpoint = 'https://%s/login' % auth_test_cfg['host']
auth_auth_endpoint = 'https://%s/auth' % auth_test_cfg['host']
auth_register_endpoint = 'https://%s/register' % auth_test_cfg['host']
auth_reset_endpoint = 'https://%s/reset' % auth_test_cfg['host']
auth_forgot_endpoint = 'https://%s/forgot' % auth_test_cfg['host']
auth_resend_endpoint = 'https://%s/resend' % auth_test_cfg['host']
auth_confirm_endpoint = 'https://%s/confirm' % auth_test_cfg['host']


# Below variables are used to save api token sent from /login endpoint.
def _get_user_token(username, password):
    from qa.utils.common import post, headers
    from qa.utils import payload
    login_payload = payload.login(username, password)

    r = post(auth_login_endpoint, json=login_payload, headers=headers(vungle_src='pub'))
    if r.status_code != 200:
        raise Exception("Failed to sign in with the credentitial: username=%s, password=%s" % (username, password))
    return r.json()['token']

# Below variables are used to save api token that are required by other API endpoints
pub_api_token = _get_user_token(pub_test_account['username'], pub_test_account['password'])
adv_api_token = _get_user_token(adv_test_account['username'], adv_test_account['password'])
both_api_token = _get_user_token(both_test_account['username'], both_test_account['password'])
pub_admin_api_token = _get_user_token(pub_admin_test_account['username'], pub_admin_test_account['password'])


# Below variables are used to save account id retrieved from the MongoDB
pub_account_id = str(db.get_account_id(pub_test_account['username']))
adv_account_id = str(db.get_account_id(adv_test_account['username']))
both_account_id = str(db.get_account_id(both_test_account['username']))
pub_admin_account_id = str(db.get_account_id(pub_admin_test_account['username']))