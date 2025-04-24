from abc import ABC, abstractmethod
import requests
from requests.models import Response
from typing import Union, Dict, List
import xml.etree.ElementTree as ET


class BaseRequester(ABC):
    def __init__(self, base_url, response_type, timeoutInSeconds):
        self.base_url = base_url
        self.response_type = response_type
        self.timeout = timeoutInSeconds

        self.session = requests.Session()
        self.authenticated = False

    @abstractmethod
    def authenticate(self):
        pass

    def request(self, endpoint, method='GET', data=None):
        if not self.authenticated:
            self.authenticate()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        method = method.upper()

        try:
            if method == 'GET':
                response = self.session.get(url, params=data, timeout=self.timeout)
            elif method == 'POST':
                response = self.session.post(url, params=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

#            # Requested Url
#            print("Requested Url:")
#            print(response.url)
#
#            # Response headers
#            print("Response Headers:")
#            for key, value in response.headers.items():
#                print(f"{key}: {value}")
#
#            # Request headers
#            print("\nRequest Headers:")
#            for key, value in response.request.headers.items():
#                print(f"{key}: {value}")

            response.raise_for_status()

            return self.parse_response(response)

        except requests.RequestException as e:
            print("error", response.status_code, response.text)
            print(f"Request error: {e}")
            return None

    def parse_response(self, response: Response) -> Union[Dict, List, str, ET.Element, ET.ElementTree]:
        match self.response_type:
            case 'json':
                return response.json()
            case 'xml':
                return response.xml()
            case _:
                return response.text()
