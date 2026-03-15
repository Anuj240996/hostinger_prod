from enum import Enum
import requests
import json


class BaseAPI:
    """
    
    
    """

    class RequestType(Enum):
        POST = "post"
        GET = "get"
        DELETE = "delete"

    def get_auth_header(self):
        return None

    def make_request(self, relative_url, request_type, **kwargs):
        if kwargs:
            if not kwargs.get("headers"):
                kwargs['headers'] = {}
        else:
            kwargs['headers'] = {}

        if self.get_auth_header():
            kwargs['headers']['Authorization'] = self.get_auth_header()

        if not kwargs['headers'].get('Content-Type'):
            kwargs['headers']['Content-Type'] = 'application/x-www-form-urlencoded'

        if kwargs.get('base_url'):
            url = kwargs['base_url'].format(relative_url)
        else:
            url = self.BASE_URL.format(relative_url)

        response = requests.request(request_type.value, url, headers=kwargs['headers'],
                                    data=kwargs)

        return response

