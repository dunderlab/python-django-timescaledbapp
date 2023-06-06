"""
======
aioAPI
======

This module provides an asynchronous wrapper for interacting with RESTful APIs.
It uses the aiohttp package to perform asynchronous HTTP requests, and allows
for batch retrieval and submission of data.

Classes:
--------
aioAPI:
    A class that provides the core functionality for interacting with an API.
    It is initialized with a base URL and optionally a JWT token for
    authorization. It can perform GET and POST requests to the API endpoints
    asynchronously and supports batch retrieval and submission of data.

inset (nested in aioAPI):
    A nested class in aioAPI that is used to interact with a specific API
    endpoint. It is initialized with an endpoint and provides methods to adjust
    the page size of the data, as well as to retrieve and submit data in
    batches. It is accessed through the overloading of the __getattr__ method
    in the aioAPI class.

Usage:
------
To use this module, you first create an instance of the aioAPI class, then you
can access the API endpoints as attributes of the instance. For example:

api = aioAPI("https://api.example.com", token="my_token")
endpoint_data = await api.my_endpoint.get()

In this case, 'my_endpoint' is an endpoint of the API. The 'get' method
performs a GET request to the endpoint and returns the retrieved data. To
retrieve the data in batches, an additional 'batch_size' argument can be
supplied to the 'get' method.
"""

import inspect
import logging
import math
import json
import asyncio
from typing import Any, Optional, Union, AsyncGenerator

import aiohttp

METHODS = ['post', 'put', '', 'get', 'delete', 'options', 'head']


# ----------------------------------------------------------------------
def batches(seq: list[Any], batch_size: int) -> list[Any]:
    """
    Generates batches from the input sequence.

    Parameters
    ----------
    seq : list
        The input sequence to be batched.
    batch_size : int
        The size of each batch.

    Yields
    ------
    list
        A batch of elements from the input sequence.

    Examples
    --------
    >>> list(batches([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]
    """
    n_batches = math.ceil(len(seq) / batch_size)
    for i in range(n_batches):
        start = i * batch_size
        end = (i + 1) * batch_size
        yield seq[start:end]


########################################################################
class aioAPI:
    """
    An asynchronous API wrapper class.

    Parameters
    ----------
    url : str, optional
        The base URL of the API.
    token : str, optional
        JWT token for API authorization.
    auth : Any, optional
        Authorization information.

    Attributes
    ----------
    HTTP_SERVICE : str
        The base URL of the API.
    AUTH : Any
        Authorization information.
    headers : dict[str, str]
        Headers to include in the API request.
    __endpoints__ : dict[str, Any]
        Endpoints of the API.
    """

    # ----------------------------------------------------------------------
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None, auth: Optional[Any] = None):
        if url and not url.endswith("/"):
            url = "{}/".format(url)
        if url:
            self.HTTP_SERVICE: str = url
        self.AUTH = auth
        if token:
            self.headers: dict[str, str] = {'Authorization': "Bearer {}".format(token)}
        else:
            self.headers: dict[str, str] = {}
        self.headers['Content-Type'] = 'application/json'
        self.__endpoints__ = self.endpoints()
        assert self.__endpoints__, "No endpoints detected. Please ensure the API is operational."

    # ----------------------------------------------------------------------
    async def endpoints(self) -> Optional[dict[str, Any]]:
        """
        Retrieve the API endpoints.

        Returns
        -------
        dict[str, Any] or None
            A dictionary containing the endpoints if the response status is 200, None otherwise.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.HTTP_SERVICE, auth=self.AUTH) as response:
                if response.status == 200:
                    return await response.json()

    # ----------------------------------------------------------------------
    async def request(self, call: str, mode: str, data: Union[dict[str, Any], str], url: Optional[str] = None) -> Optional[dict[str, Any]]:
        """
        Make an API request.

        Parameters
        ----------
        call : str
            The API endpoint.
        mode : str
            The HTTP method (e.g., 'get', 'post').
        data : dict[str, Any] or str
            The data to send with the request.
        url : str, optional
            An optional URL to override the default.

        Returns
        -------
        dict[str, Any] or None
            A dictionary containing the response data if the response status is 200 or 201, None otherwise.
        """
        timeout = aiohttp.ClientTimeout(total=5 * 60)

        params = {}

        if mode == 'post':
            data = json.dumps(data)
            timeout = aiohttp.ClientTimeout(total=100 * 60)

        if mode == 'get' and data:
            timeout = aiohttp.ClientTimeout(total=5 * 60)
            params, data = data, params

        if not url:
            url = self.HTTP_SERVICE + call + "/"

        if mode in ['delete', 'patch', 'put']:
            url = f'{url}{data["id"]}/'
            data = json.dumps(data)

        async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
            async with getattr(session, mode)(url, params=params, data=data, auth=self.AUTH) as response:
                if response.status in [200, 201]:
                    resp = await response.json()
                    if 'next' in resp and resp['next'] and 'get' == mode:
                        resp = self.request_generator(resp, mode)
                    return resp
                elif response.status == 204 and mode == 'delete':
                    return True
        logging.warning(f"Error {response.status}: {response.reason}")
        logging.warning(f"{response.json()}")
        return None

    # ----------------------------------------------------------------------
    async def request_generator(self, resp: dict[str, Any], mode: str) -> AsyncGenerator[dict[str, Any], None]:
        """
        Asynchronous generator to recursively request next page data based on the response from the server.

        Parameters
        ----------
        resp : dict
            Initial response from the server.
        mode : str
            Request method (get or post).

        Yields
        ------
        dict
            The JSON response from the server.

        """
        yield resp
        resp = await self.request_yield(mode, resp['next'])
        while resp and resp['next']:
            yield resp
            resp = await self.request_yield(mode, resp['next'])
        yield resp

    # ----------------------------------------------------------------------
    async def request_yield(self, mode: str, url: str) -> Optional[dict[str, Any]]:
        """
        Asynchronous function to send request to server and fetch JSON data.

        Parameters
        ----------
        mode : str
            Request method (get or post).
        url : str
            The URL to which the request is to be sent.

        Returns
        -------
        dict, optional
            The JSON response from the server if the status code is 200 or 201. None otherwise.

        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with getattr(session, mode)(url, auth=self.AUTH) as response:
                if response.status in [200, 201]:
                    return await response.json()

    # ----------------------------------------------------------------------
    async def next(self, data):
        """"""
        if inspect.isasyncgen(data) or (isinstance(data, dict) and data.get('next', False)):
            return await anext(data)
        else:
            return data

    # ----------------------------------------------------------------------
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
        """
        Asynchronous function to fetch a page's JSON data using aiohttp client session.

        Parameters
        ----------
        session : aiohttp.ClientSession
            Active aiohttp client session.
        url : str
            URL of the page to fetch.

        Returns
        -------
        dict
            The JSON response from the server.

        """
        headers = {'Content-Type': 'application/json'}
        async with session.get(url, headers=headers) as response:
            return await response.json()

    # ----------------------------------------------------------------------
    async def fetch_all_pages(self, pages: list[str]) -> list[dict[str, Any]]:
        """
        Asynchronous function to fetch all page's JSON data concurrently.

        Parameters
        ----------
        pages : list of str
            List of URLs of pages to fetch.

        Returns
        -------
        list of dict
            List of JSON responses from the server for all pages.

        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in pages:
                tasks.append(self.fetch_page(session, url))
                return await asyncio.gather(*tasks)

    # ----------------------------------------------------------------------
    def __getattr__(cls, endpoint: str):
        """
        Overloaded method to handle access to nonexistent attributes.

        It is used to create a new instance of the nested 'inset' class with the specified endpoint when an attribute with that name is accessed.

        Parameters
        ----------
        endpoint : str
            The name of the endpoint.

        Returns
        -------
        inset
            An instance of the nested 'inset' class with the specified endpoint.
        """

        ########################################################################
        class inset:
            """
            Class to manage the interaction with a specific endpoint.

            This class provides several functionalities to interact with the endpoint,
            including adjusting the page size, submitting and retrieving data in batches,
            and making asynchronous requests.

            Parameters
            ----------
            endpoint : str
                The endpoint to interact with.
            """

            # ----------------------------------------------------------------------
            def __init__(self, endpoint: str):
                """
                Initialize the inset instance with a specific endpoint.
                """
                self.endpoint = endpoint

            # ----------------------------------------------------------------------
            def adjust_page_size(self, data: dict[str, Any], batch_size: Optional[int] = None) -> list[dict[str, Any]]:
                """
                Adjusts the page size based on the specified batch size.

                Parameters
                ----------
                data : dict
                    The original data with the original page size.
                batch_size : int, optional
                    The batch size to divide the data into. If not specified, no adjustment is done.

                Returns
                -------
                list of dict
                    A list of new requests with the adjusted page size.
                """
                original_page_size = data['page_size']
                request_count = math.ceil(original_page_size / batch_size)
                initial_index = (data.get('page', 1) - 1) * original_page_size
                new_initial_page = math.ceil(initial_index / batch_size) + 1
                all_requests = []
                for i in range(new_initial_page, new_initial_page + request_count):
                    new_request = data.copy()
                    new_request['page_size'] = batch_size
                    new_request['page'] = i
                    all_requests.append(new_request)
                return all_requests

            # ----------------------------------------------------------------------
            async def submit_data_in_batches(self, data_list: list[dict[str, Any]], method: str, batch_size: int, url: Optional[str] = None) -> list[dict[str, Any]]:
                """
                Submits the data in batches asynchronously.

                Parameters
                ----------
                data_list : list of dict
                    The list of data to be submitted.
                method : str
                    The HTTP method to use for the request ('get' or 'post').
                batch_size : int
                    The size of the batches to divide the data into.
                url : str, optional
                    The URL to send the request to. If not specified, the endpoint URL is used.

                Returns
                -------
                list of dict
                    The responses from the server.
                """
                tasks = []
                for batch_data in batches(data_list, batch_size):
                    task = asyncio.create_task(cls.request(self.endpoint, method, batch_data, url))
                    tasks.append(task)
                return await asyncio.gather(*tasks)

            # ----------------------------------------------------------------------
            async def retrieve_data_in_batches(self, data_list: list[dict[str, Any]], method: str, url: Optional[str] = None) -> list[dict[str, Any]]:
                """
                Retrieves data in batches asynchronously.

                Parameters
                ----------
                data_list : list of dict
                    The list of data to be retrieved.
                method : str
                    The HTTP method to use for the request ('get' or 'post').
                url : str, optional
                    The URL to send the request to. If not specified, the endpoint URL is used.

                Returns
                -------
                list of dict
                    The responses from the server.
                """
                tasks = []
                for batch_data in data_list:
                    task = asyncio.create_task(cls.request(self.endpoint, method, batch_data, url))
                    tasks.append(task)
                return await asyncio.gather(*tasks)

            # ----------------------------------------------------------------------
            def __getattr__(self, method: str):
                """
                Overloaded method to make asynchronous requests.

                Parameters
                ----------
                method : str
                    The HTTP method to use for the request ('get' or 'post').

                Returns
                -------
                function
                    An asynchronous function to be used for making the request.
                """
                async def f(data: dict[str, Any] = {}, files: dict[str, Any] = {}, batch_size: Optional[int] = None, url: Optional[str] = None) -> Union[dict[str, Any], list[dict[str, Any]]]:
                    if batch_size is None:
                        return await cls.request(self.endpoint, method, data, url)
                    if method == 'post':
                        return await self.submit_data_in_batches(data_list=data, method=method, batch_size=batch_size, url=url)
                    if method == 'get':
                        data = self.adjust_page_size(data, batch_size)
                        responses = await self.retrieve_data_in_batches(data_list=data, method=method, url=url)
                        return [await anext(d) for d in responses]
                return f

        return inset(endpoint)
