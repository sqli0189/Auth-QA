def login(username="foo@foo.com", password="foo"):
    data = {"username" : username, "password": password}
    return data

def resend(username="foo.foo.com"):
    data = {"username": username}
    return data

def register(username='foo@foo.com', name='foo', account_name='foo', password='#foofoo123', country='United States', account_type='pub', token='recaptcha_token'):
    data = { "username": username, 
             "name": name, 
             "account_name": account_name,
             "password": password,
             "country": country,
             "account_type": account_type,
             "token": token
            }
    return data

def forgot(username='foo@foo.com'):
    data = {"username": username}
    return data

def confirm(token='zzzzzzzzzzzzzzzzzzz33b57e36d98cc9bf91cbfa4zzz1d69b5cbe9c92bczzc0fc9ca8717bfc108zzzzzzzzzzzzzzzzz'):
    data = {"token": token}
    return data

def reset(username, password_reset_token, password):
    data = {"username": username,
            "password_reset_token": password_reset_token,
            "password": password}
    return data

def application(owner, platform, app_name, is_coppa, 
                store_id="", store_cat="", is_paid=False, is_manual=False, store_url="", thumbnail=""):
    data = {"owner": owner,
            "platform": platform,
            "name": app_name,
            "store": 
            {
                "id": store_id,
                "category": store_cat,
                "isPaid": is_paid,
                "isManual": is_manual,
                "url": store_url,
                "thumbnail": thumbnail
            },
            "isCoppa": is_coppa}

    return data

def placement(placement_name, placement_type, app_id, allow_end_cards = True, is_skippable = False):
    data = { "name": placement_name,
             "type": placement_type,
             "application": app_id,
             "allowEndCards": allow_end_cards,
             "isSkippable": is_skippable
           }
    return data

def user(account_id, name, email, access):
    data = {
            "account": account_id,
            "name": name,
            "email": email,
            "role": access
          }
    return data