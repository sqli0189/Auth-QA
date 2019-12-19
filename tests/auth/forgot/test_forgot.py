import pytest
import allure

from hamcrest import *
from http import HTTPStatus

from qa.utils.common import *

import qa.utils.db_access as db
import qa.utils.payload as payload
import qa.utils.imapclient as imapclient

from qa.utils.assertions import *

import qa.data.response_schema as response_schema

from qa.settings import *

@allure.epic('Authentication')
@allure.feature('Forget Password')
class TestForgot(object):

    @allure.story('Call forget with a valid e-mail address')
    @allure.severity('critical')       
    def test_forgot_with_valid_email_address(self):
        '''
        1. The response status code should be HTTP 200 OK;
        2. An empty payload should be returned in the response payload;
        2. The e-mail should be successfully sent to the user's mailbox;
        '''
        # Clear the inbox
        imapclient.clear_inbox(pub_test_account['username'], pub_test_account['password'])

        # Test execution
        forgot_payload = payload.forgot(pub_test_account['username'])

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers())

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        assert_valid_schema(r.json(), response_schema.empty_schema)

        expected_sender = 'no-reply@vungle.com'
        expected_subject = 'Password Change'
        assert_that(imapclient.search_email(pub_test_account['username'],
                                            pub_test_account['password'],
                                            expected_subject, 
                                            expected_sender, 40)[0],
                    equal_to(True),
                    'Verify if the targe account is able to receive the notification')


    @allure.story('Call forgot with an inexistent e-mail address')
    @allure.severity('critical')
    def testN_forgot_with_inexistent_email_address(self):
        '''
        1. The response status code should be HTTP 404;
        2. An error message is expected to be returned in the response payload;
        '''
        forgot_payload = payload.forgot(username='foo_user@foo.com')

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.NOT_FOUND)
        # Verify the response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)
    

    @allure.story('Call forgot with a malformed email address')
    @allure.severity('normal')
    @pytest.mark.parametrize('malformed_email', ['abc', '@', '@123.com', 'abc@'])    
    def testN_forgot_with_malformed_email_address(self, malformed_email):
        '''
        1. The response status code should be HTTP 400;
        2. An error message is expected to be returned in the response payload;
        '''
        forgot_payload = payload.forgot(username = malformed_email)

        r = post(auth_forgot_endpoint, json=forgot_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)    


    @allure.story('Call forgot without payload')
    @allure.severity('minor')
    def testN_forgot_without_payload(self):
        '''
        1. The response status code should be HTTP 400;
        2. An error message is expected to be returend in the response payload;
        '''
        
        r = post(auth_forgot_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify the response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Call forgot without vungle version in the request payload')
    @allure.severity('minor')
    def testN_forgot_without_vungle_version_in_headers(self):
        '''
        1. The response status code should be HTTP 400;
        2. An error message is expected to be returned in the response payload;
        '''

        forgot_payload = payload.forgot(username=test_accounts['pub']['username'])

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers(vungle_version=None))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify the response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)