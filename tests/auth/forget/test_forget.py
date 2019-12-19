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

@allure.epic('Mission Ctrl: Authentication')
@allure.feature('Forget password')
class TestForgot(object):

    @allure.story('Call forget with a valid e-mail address')
    @allure.severity('critical')       
    def test_forgot_with_valid_email_address(self):

        # Test execution
        forgot_payload = payload.forgot(pub_test_account['username'])

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)


    @allure.story('Call forget with an inexistent e-mail address')
    @allure.severity('critical')
    def test_forgot_with_inexistent_email_address(self):
        '''
        A HTTP 404 error is expected to be returned 
        '''
        forgot_payload = payload.forgot(username='foo_user@foo.com')

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.NOT_FOUND)
        assert_that(r.text, equal_to(''))
    

    @allure.story('Call forget with a malformed email address')
    @allure.severity('normal')
    @pytest.mark.parametrize('malformed_email', ['abc', '@', '@123.com', 'abc@'])    
    def test_forgot_with_malformed_email_address(self, malformed_email):
        '''
        An error message is expected to be returned 
        '''
        forgot_payload = payload.forgot(username = malformed_email)

        r = post(auth_forgot_endpoint, json=forgot_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"code": 601,
                                        "message": "body.username in body must be of type email: \"%s\"" % malformed_email}
                                    ))
    

    @allure.story('Call forget without payload')
    @allure.severity('minor')
    def test_forgot_without_payload(self):
        '''
        An error message is expected to be returend.
        '''
        
        r = post(auth_forgot_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"code": 602, "message": "body in body is required"}))


    @allure.story('Call forget without vungle version in the request payload')
    @allure.severity('minor')
    def test_forgot_without_vungle_version_in_headers(self):
        '''
        An error message is expected to be returned.
        '''

        forgot_payload = payload.forgot(username=test_accounts['pub']['username'])

        r = post(auth_forgot_endpoint, json = forgot_payload, headers=headers())

        # Verify status code
        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)
        
        assert_that(r.json(), equal_to({"code": 602, "message": "vungle-version in header is required"}))