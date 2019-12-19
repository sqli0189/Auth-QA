import pytest
import allure

from hamcrest import *
from http import HTTPStatus

from qa.utils.common import *
from qa.utils.assertions import *
from qa.utils import imapclient
from qa.settings import *

import qa.utils.db_access as db
import qa.utils.payload as payload
import qa.data.response_schema as response_schema


@allure.epic('Authentication')
@allure.feature('Re-send activation e-mail')
class TestResend(object):

    @allure.story('Resend e-mail with a valid username')
    @allure.severity('critical')
    def test_resend_with_valid_username(self):
        '''
        1. The response status code should be HTTP 200 OK;
        2. An empty payload should be returned in the response payload;
        2. The e-mail should be successfully sent to the user's mailbox;
        '''
        
        # Clear the inbox
        imapclient.clear_inbox(pub_test_account['username'], pub_test_account['password'])
            
        resend_payload = payload.resend(pub_test_account['username'])
        r = post(auth_resend_endpoint, json=resend_payload, headers=headers(vungle_version='1'))

        assert_that(r.status_code, HTTPStatus.OK)
        assert_valid_schema(r.json(), equal_to(response_schema.empty_schema))

        expected_sender = 'no-reply@vungle.com'
        expected_subject = 'Welcome to Vungle!'
        assert_that(imapclient.search_email(pub_test_account['username'],
                                            pub_test_account['password'],
                                            expected_subject, 
                                            expected_sender, 40)[0],
                    equal_to(True),
                    'Verify if the targe account is able to receive the notification')
       
    
    @allure.story('Resend e-mail with an inexistent user')
    @allure.severity('normal')
    def testN_resend_with_inexistent_username(self):
        '''
        A HTTP 404 error is expected to be returned in response status code
        '''
        resend_payload = payload.resend('foo@foo.com')

        r = post(auth_resend_endpoint, json=resend_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_that(r.status_code, HTTPStatus.NOT_FOUND)


    @allure.story('Resend e-mail with a malformed email as the username')
    @allure.severity('minor')   
    @pytest.mark.parametrize('email_addr', ['abc', '@', '@123.com', 'abc@'])
    def testN_resend_with_malformed_email_address(self, email_addr):
        '''
        An error message is expected to be returned in the response payload
        '''
        resend_payload = payload.resend(email_addr)

        r = post(auth_resend_endpoint, json=resend_payload, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        assert_valid_schema(r.json(), response_schema.error_message)

        assert_that(r.json(), equal_to({"code": 601,
                                        "message": "body.username in body must be of type email: \"%s\"" % email_addr}
                                    ))

    @allure.story('Invoke resend without payload in request body')
    @allure.severity('minor')
    def testN_resend_without_payload(self):
        '''
        An error message is expected to be returned in response payload
        '''
        r = post(auth_resend_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Invoke resend without vungle-version in request headers')
    @allure.severity('minor')
    def testN_resend_without_vungle_version_in_headers(self):
        '''
        An error message is expected to be returned in response payload
        '''

        resend_payload = payload.resend(test_accounts['pub']['username'])

        r = post(auth_resend_endpoint, json=resend_payload, headers=headers(vungle_version=None))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify response body
        assert_valid_schema(r.json(), response_schema.payload_check_error)
