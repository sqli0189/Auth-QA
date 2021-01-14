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
@allure.feature('New user confirm to login')
class TestConfirm(object):


    @allure.story('Confirm to sign in with correct token')
    @allure.severity('critical')
    def test_confirm_with_correct_token(self, new_registered_user):
        '''
        1. The response status code should be HTTP 200 OK;
        '''

        # Get the token of new user
        user_name = new_registered_user[0]
        user_token = new_registered_user[2]

        confirm_payload = payload.confirm(token = user_token)

        r = post(auth_confirm_endpoint, json=confirm_payload, headers=headers(vungle_version='1'))

        # Build expected response
        expected_response_payload = {'username': user_name}

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.OK)
        # Verify the response payload
        assert_that(r.json(), has_entries(expected_response_payload))


    @allure.story('Call confirm endpoint without payload information')
    @allure.severity('normal')
    def testN_confirm_without_payload(self):
        '''
        An error message is expected to be returned
        '''
        r = post(auth_confirm_endpoint, json=None, headers=headers(vungle_version='1'))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.UNAUTHORIZED)
        #Verify response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)


    @allure.story('Call confirm endpoint without vungle-version in request headers')
    @allure.severity('minor')
    def testN_confirm_without_vungle_version_in_headers(self):
        '''
        An error message is expected to be returned.
        '''
        confirm_payload = payload.confirm(token='zzzzzzzzz')

        r = post(auth_confirm_endpoint, json=confirm_payload, headers=headers(vungle_version=None))

        # Verify status code
        assert_response_status_code(r.status_code, HTTPStatus.BAD_REQUEST)
        # Verify the response payload
        assert_valid_schema(r.json(), response_schema.payload_check_error)