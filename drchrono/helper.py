from social_django.models import UserSocialAuth


def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token

def make_api_request(EndpointClass):
    """
    Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
    proved that the OAuth setup is working
    """
    # We can create an instance of an endpoint resource class, and use it to fetch details
    access_token = get_token()
    api = EndpointClass(access_token)
    # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
    # account probably only has one doctor in it.
    return next(api.list())