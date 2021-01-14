import pytest
import allure

from hamcrest import *
from http import HTTPStatus

from qa.utils.common import *

import qa.utils.db_access as db
import qa.utils.payload as payload
from qa.utils.assertions import *

import qa.data.response_schema as response_schema

from qa.settings import *

@allure.epic('Authentication')
@allure.feature('Login')
class TestLogin(object):

    @allure.story('Login with valid username and password')
    @allure.severity('blocker')
    @pytest.mark.parametrize('account_type, username, password, expected_account_type', [
                             ('pub', test_accounts['pub']['username'], test_accounts['pub']['password'], 'publisher'),
                             ('adv', test_accounts['adv']['username'], test_accounts['adv']['password'], 'advertiser'),
                             ('both', test_accounts['both']['username'], test_accounts['both']['password'], 'both'),
                             ('pub_admin', test_accounts['pub_admin']['username'], test_accounts['pub_admin']['password'], 'publisher')
                             ])
    def test_login_with_valid_user(self, account_type, username, password, expected_account_type):
        '''
        1.  The response status code should be HTTP 200 OK;
        2.  The user should be able to login into the system and get correct access token;
        '''
        # Send post request
        r = post(auth_login_endpoint, json = payload.login(username, password), headers = headers(vungle_src='pub'))
        
        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        
        # Verify response body
        expected_response_payload = {'username': username,
                                     'account_type': expected_account_type
                                    }
        assert_that(r.json(), has_entries(expected_response_payload))
        assert_that(r.json(), has_key('token'))

    
    @allure.story('Login with the valid vungle source value')
    @allure.severity('blocker')
    @pytest.mark.parametrize('val', ['auth', 'pub', 'grow', 'ctrl', 'admin'])
    def test_login_with_valid_vungle_source_val(self, val):
        '''
        1.  The response status code should be HTTP 200 OK;
        2.  The user should be able to login into the system and get correct access token;
        '''

        r = post(auth_login_endpoint, 
                 json=payload.login(test_accounts['pub']['username'], test_accounts['pub']['password']), 
                 headers=headers(vungle_src=val))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        
        # Verify response body
        expected_response_payload = {'username': test_accounts['pub']['username'],
                                    'account_type': 'publisher'
                                    }
        assert_that(r.json(), has_entries(expected_response_payload))
        assert_that(r.json(), has_key('token'))
    
    @allure.story('If the value of the field vungle-source is api, the token should be returned.')
    @allure.severity('minor')
    def test_login_with_valid_vungle_source_val_api(self):
        '''
        1.  The response status code should be HTTP 200 OK;
        2.  The user should be able to login into the system and get correct access token;
        '''

        r = post(auth_login_endpoint, 
                 json=payload.login(test_accounts['pub']['username'], test_accounts['pub']['password']), 
                 headers=headers(vungle_src='api'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        
        # Verify response body
        assert_that(r.json(), has_key('token'))
    

    @allure.story('Login in with an inactivated user')
    @allure.severity('normal')
    def testN_login_with_inactivated_user(self, new_registered_user):
        '''
        1. The response status code should be HTTP 403;
        2. An error message should be returned in the response payload
        '''

        username = new_registered_user[0]
        password = new_registered_user[1]

         # Send post request
        r = post(auth_login_endpoint, json=payload.login(username, password), headers=headers(vungle_src='pub'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.FORBIDDEN)
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Call login endpoint without request payload')
    @allure.severity('minor')    
    def testN_login_without_payload(self):
        '''
        1. The response status code should be HTTP 400 Bad Request;
        2. An error message should be returned in the response payload;
        '''
        
        # Send post request with empty data
        r = post(auth_login_endpoint, json=None, headers=headers(vungle_src='pub'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Login with an incorrect password')
    @allure.severity('blocker')
    def testN_login_with_incorrect_password(self):
        '''
        1. The response status code should be unauthorized;
        2. The user should not be allowed to login in and an error message should be returned.
        '''
        account_type = 'pub'
        incorrect_password = 'foo_12345'

        r = post(auth_login_endpoint, 
                 json=payload.login(test_accounts[account_type]['username'],incorrect_password), 
                 headers=headers(vungle_src=account_type))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.FORBIDDEN)
        assert_valid_schema(r.json(), response_schema.payload_check_error)
    

    @allure.story('Log into system without vungle source in the request header')
    @allure.severity('minor')
    def testN_login_without_vungle_source_in_headers(self):
        '''
        1. An error message should be returned in the resposne payload;
        2. The response status code should be HTTP 400 bad request;
        '''
        login_payload = payload.login(test_accounts['pub']['username'], 
                                      test_accounts['pub']['password'])
        
        r = post(auth_login_endpoint, json=login_payload, headers=headers())

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)
    

    @allure.story('Log into system with an inexistent user account')
    @allure.severity('minor')
    def testN_login_with_inexistent_user(self):
        '''
        1. The response status code should be unauthorized;
        2. The user should not be allowed to sign in and an error message should be returned in response payload
        '''
        r = post(auth_login_endpoint, json=payload.login('foo@foo.com', 'foo1234'), 
                 headers=headers(vungle_src='pub'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.FORBIDDEN)
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('In request headers, set an invalid value to the vungle source and sign in')
    @allure.severity('minor')
    def testN_login_with_invalid_vungle_src_val(self):
        '''
        1. The response status code should be HTTP 400;
        2. User should not be allowed to sign in and an error message should be returned.
        '''
        login_payload = payload.login(test_accounts['pub']['username'], 
                                      test_accounts['pub']['password'])
        
        invalid_src_param = 'foo'
        r = requests.post(auth_login_endpoint, json=login_payload, headers=headers(vungle_src=invalid_src_param))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)
    

    @allure.story('In request headers, set an invalid value to the vungle source and sign in')
    @allure.severity('minor')
    def testN_login_without_vungle_version(self):
        '''
        
        '''
        login_payload = payload.login(test_accounts['pub']['username'], 
                                      test_accounts['pub']['password'])
        
        r = requests.post(auth_login_endpoint, json=login_payload, headers=headers(vungle_version=None))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)