import pytest
import allure

from hamcrest import *
from http import HTTPStatus

from qa.utils.common import *
from qa.utils import imapclient

import qa.utils.db_access as db
import qa.utils.payload as payload
from qa.utils.assertions import *

import qa.data.response_schema as response_schema

from qa.settings import *

@allure.epic('Authentication')
@allure.feature('Register a new account')
class TestRegister(object):


    @allure.story('Register a new user with correct username & password')
    @allure.severity('critical')
    @pytest.mark.parametrize('account_type_val', ['publisher', 'advertiser', 'both'])
    def test_register_with_correct_user_info(self, account_type_val):
        '''
        1. The response status code should be HTTP 200 OK;
        2. An empty payload should be returned in the response payload;
        3. The new account should be inserted into the MongoDB;
        '''
        email = new_test_account['username']
        password = new_test_account['password']
        try:
            
            imapclient.clear_inbox(email, password)

            register_payload = payload.register(username = email, password=password, account_type=account_type_val)
            r = post(auth_register_endpoint, json=register_payload, headers=headers())

            # Verify status code
            assert_response_status_code(r.status_code, HTTPStatus.OK)            # Verify response body
            assert_that(r.json(), equal_to({}))

            # Verify the account info saved in MongoDB
            account_info = db.get_account_info(email)
            assert_that(account_info['contactEmail'], equal_to(email))
            assert_that(account_info['accountType'], equal_to(account_type_val))

            # Verify an email should be sent to new user's mailbox
            expected_sender = 'no-reply@vungle.com'
            expected_subject = 'Welcome to Vungle!'
            assert_that(imapclient.search_email(email, password, expected_subject, expected_sender, 40)[0], equal_to(True),
                        'Verify if the user is able to receive the notification.')
        finally:
            db.delete_account_info(email)
    
    
    @allure.story('Register a new user with incorrect account type')
    @allure.severity('minor')
    @pytest.mark.parametrize('incorrect_account_type', ['pub', 'advertiser0', 'foo'])
    def testN_register_with_incorrect_account_type(self, incorrect_account_type):
        '''
        1. The response status code should be HTTP 200 OK;
        2. An error message should be returned in the response payload;
        '''
        
        email = 'sample@foo.com.cn'

        try:

            register_payload = payload.register(username = email, account_type=incorrect_account_type)

            r = post(auth_register_endpoint, json=register_payload, headers=headers())

            # Verify status code
            assert_response_status_code(r.status_code, HTTPStatus.OK)            # Verify response body
            assert_valid_schema(r.json(), response_schema.payload_check_error)

        finally:
            db.delete_account_info(email)


    @allure.story('Register a new user with malformed email address as the username')
    @allure.severity('normal')
    @pytest.mark.parametrize('malformed_mail_address', ['abc', '@', '@123.com', 'abc@'])
    def testN_register_with_a_malformed_email_address(self, malformed_mail_address):
        '''
        1. The response status code should be HTTP 400;
        2. An error message is expected to be returned in response payload 
        '''
        register_payload = payload.register(username = malformed_mail_address, account_type='publisher')
        
        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify response body
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Call register without payload in request body')
    @allure.severity('minor')
    def testN_register_without_payload(self):
        '''
        1. The response status code should be HTTP 400;
        2. An error message is expected to be returned in response payload;
        '''

        r = post(auth_register_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify response body
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story("Call register with a user who has already existed")
    @allure.severity('normal')
    def testN_register_with_an_existing_email_address(self):
        '''
        1. The response status code should be HTTP 409 (Conflict);
        2. An error message is expected to be returned in response payload;
        '''
        register_payload = payload.register(username=test_accounts['pub_admin']['username'], account_type='both')

        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.CONFLICT)
        # Verify response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)
    

    @allure.story('Call register without vungle version in request headers')
    @allure.severity('minor')
    def testN_register_without_vungle_version_in_headers(self):
        '''
        1. The response status code should be HTTP 409 (Conflict);
        2. An error message is expected to be returned in response payload;
        '''
        register_payload = payload.register(account_type='both')

        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version=None))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)