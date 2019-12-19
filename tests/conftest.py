import pytest
import logging

import qa.utils.db_access as db

from qa.utils import payload
from qa.settings import *
from qa.utils.common import *

@pytest.fixture(scope="function")
def new_registered_user():

    username = 'temp_user@foo.com'
    password = 'temp1234'

    db.delete_account_info(username)

    register_data = payload.register(username=username, password=password)
    r = post(auth_register_endpoint, json=register_data, headers=headers(vungle_src='pub'))
        
    if r.status_code == 200:
        token = db.get_user_activation_token(username)
    else:
        raise Exception("new_registered_user(): Failed to register new user.")
    
    yield (username, password, token)

    db.delete_account_info(username)

# Create multiple users for pub account
@pytest.fixture(scope='class')
def multiple_users_for_pub():

    users_data = [{'first_name':'Tom', 'last_name':'Li', 'email_address': 'tom.li@foo.com'},
                  {'first_name':'Tom', 'last_name':'Liu', 'email_address': 'tom.liu@foo.com'},
                  {'first_name':'Tim', 'last_name':'Zhang', 'email_address': 'tim.zh@foo.com'}]

    user_ids = db.insert_multiple_users_data(pub_account_id, users_data)

    yield user_ids

    db.delete_all_team_members(pub_account_id, pub_test_account['username'])

# Create a new user to be deleted for both account
@pytest.fixture(scope='function')
def new_user_for_delete():
    f_name = 'Lady'
    l_name = 'Gaga'
    email = 'gaga@singer.cc'

    user_id = db.insert_user_data(both_account_id, f_name, l_name, email)

    yield {'user_id': user_id}

    db.delete_all_team_members(both_account_id, both_test_account['username'])

# Genereate environment.properties for allure reporting framework
@pytest.fixture(scope="session")
def allure_env(tmpdir_factory, metadata):
    env_file = tmpdir_factory.mktemp('test_env').join('environment.properties')
    with open(env_file, 'w+') as env:
        env.writelines('Auth_Host_Url=%s\n' % auth_test_cfg['host'])
        env.writelines('Auth_API_Version=%s\n' % auth_test_cfg['version'])
        env.writelines('Test_Environment=%s\n' % test_env_type)
        env.writelines('Test_Execution_Platform=%s\n' % metadata['Platform'])
        env.writelines('Python_Version=%s\n' % metadata['Python'])
    return str(env_file)

# Read command options from commandline
@pytest.fixture(scope="session", autouse=True)
def write_allure_env(request, allure_env):
    from os.path import isdir, join
    from shutil import copyfile
    # Copy environment to alluredir
    yield
    # We will not generate environment.property if user doesn't specify alluredir
    alluredir = request.config.getoption('--alluredir')
    if alluredir is None:
        return
    # Copy environment file to the allure dir
    if isdir(alluredir):
        copyfile(allure_env, join(alluredir, 'environment.properties'))