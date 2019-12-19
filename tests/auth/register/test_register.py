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
@allure.feature('Register the new account')
class TestRegister(object):


    @allure.story('Register a new user with correct username and password')
    @allure.severity('critical')
    def test_register_with_correct_user_info(self):
        '''
        The register operation should succeed and the response should return HTTP 200 OK
        '''

        email = 'sample@foo.com.cn'
        try:
            register_payload = payload.register(username = email)
            r = post(auth_register_endpoint, json=register_payload, headers=headers())

            # Verify status code
            assert_response_status_code(r.status_code, HTTPStatus.OK)
            
            # Verify response body
            assert_that(r.json(), equal_to({}))
        finally:
            db.delete_account_info(email)


    @allure.story('Register a new user with malformed email address as the username')
    @allure.severity('normal')
    @pytest.mark.parametrize('malformed_mail_address', ['abc', '@', '@123.com', 'abc@'])
    def testN_register_with_malformed_email_address_as_username(self, malformed_mail_address):
        '''
        An error message is expected to be returned in response payload 
        '''
        register_payload = payload.register(username = malformed_mail_address)
        
        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"code": 601,
                                        "message": "body.username in body must be of type email: \"%s\"" % malformed_mail_address}
                                    ))

    @allure.story('Register a new user with the password less than 6 characters')
    @allure.severity('normal')
    def testN_register_with_less_than_6_chars_password(self):
        '''
        An error message is expected to be returned in response payload
        '''

        register_payload = payload.register(password='foo12')
        
        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"code": 604,
                                        "message": "body.password in body should be at least 6 chars long"}
                                        ))

    @allure.story('Call register without payload in request body')
    @allure.severity('minor')
    def testN_register_without_payload(self):
        '''
        An error message is expected to be returned in response payload
        '''

        r = post(auth_register_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"code": 602,
                                        "message": "body in body is required"
                                        }))

    @allure.story("Call register with a user who has already existed")
    @allure.severity('normal')
    def testN_register_with_an_existing_email_address(self):
        '''
        An error message is expected to be returned in response payload
        '''
        register_payload = payload.register(username=test_accounts['pub_admin']['username'])

        r = post(auth_register_endpoint, json=register_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.CONFLICT)
        assert_valid_schema(r.json(), response_schema.error_message)

        # Verify response body
        assert_that(r.json(), equal_to({"message": "email already exists"}))
    
    @allure.story('Call register without vungle version in request headers')
    @allure.severity('minor')
    def testN_register_without_vungle_version_in_headers(self):
        '''
        An error message is expected to be returned in response payload
        '''
        register_payload = payload.register()

        r = post(auth_register_endpoint, json=register_payload, headers=headers())

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)
        
        # Verify response body
        assert_that(r.json(), equal_to({"code": 602,
                                        "message": "vungle-version in header is required"
                                        }))