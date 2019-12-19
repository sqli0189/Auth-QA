import jsonschema
from hamcrest import *

def assert_response_status_code(http_code, expected_status_code):
    assert_that(http_code, equal_to(expected_status_code), 
                'Verify the status code should be equal to %s' % expected_status_code)

def assert_response_headers(response_headers):

    content_type = 'application/json'
    assert_that(response_headers['content-type'], equal_to(content_type),
                'Verify content-type in the response headers should be equal to %s' % content_type)

    content_encoding = 'gzip'
    assert_that(response_headers['content-encoding'], equal_to('gzip'),
                'Verify content-encoding in the response headers should be equal to %s' % content_encoding)

def assert_valid_schema(response_json, schema):
    assert_that(jsonschema.validate(response_json, schema), none(), 
                'Verify the json response should follow the schema')

def assert_key_present(response_payload, key):
    error_code = 'NOT_PRESENT'
    assert_that(response_payload.pop(key, error_code), is_not(equal_to(error_code)),
                'Verify the field %s is present in the payload' % key)

def assert_key_not_present(response_payload, key):
    assert_that(response_payload.pop(key, 0), equal_to(0),
                'Verify the key %s is not present in the payload' % key)

def assert_match_regex_expression(source, pattern):
    assert_that(source, matches_regexp(pattern), 
                "Verify if the string '%s' matches the expression '%s'" % (source, pattern))