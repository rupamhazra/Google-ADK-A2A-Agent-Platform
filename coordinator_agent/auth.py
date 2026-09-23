import copy

import httpx

import google.auth
from google.auth.transport.requests import Request


class GoogleCloudAuth(httpx.Auth):
    """
    Adds a Google Cloud OAuth bearer token to A2A requests.

    Credentials are loaded lazily inside the running coordinator
    rather than during deployment packaging.
    """

    requires_request_body = True

    def __init__(self):
        self._credentials = None

    def _get_credentials(self):
        if self._credentials is None:
            self._credentials, _ = google.auth.default(
                scopes=[
                    (
                        "https://www.googleapis.com/"
                        "auth/cloud-platform"
                    )
                ]
            )

        return self._credentials

    def auth_flow(self, request):
        credentials = self._get_credentials()

        if (
            not credentials.valid
            or credentials.expired
            or not credentials.token
        ):
            credentials.refresh(
                Request()
            )

        request.headers["Authorization"] = (
            f"Bearer {credentials.token}"
        )

        request.headers["Content-Type"] = (
            "application/json"
        )

        yield request

    def __getstate__(self):
        """
        Do not serialize live Google credential objects.
        Agent Runtime will load ADC after startup.
        """

        return {}

    def __setstate__(self, state):
        self._credentials = None

    def __deepcopy__(self, memo):
        """
        Return a new empty authentication handler during the
        Agent Runtime deployment deep-copy operation.
        """

        copied_auth = type(self)()
        memo[id(self)] = copied_auth

        return copied_auth


class CloneableAsyncClient(httpx.AsyncClient):
    """
    An AsyncClient that can survive Agent Runtime deepcopy
    and cloudpickle serialization.

    A normal AsyncClient contains a CookieJar RLock, which is
    not serializable. This class serializes configuration instead
    of serializing the live HTTP transport and lock objects.
    """

    def __init__(
        self,
        *,
        auth=None,
        timeout=120.0,
        headers=None,
    ):
        self._saved_auth = auth
        self._saved_timeout = timeout
        self._saved_headers = dict(
            headers or {}
        )

        super().__init__(
            auth=auth,
            timeout=timeout,
            headers=self._saved_headers,
        )

    def __getstate__(self):
        """
        Store only serializable client configuration.
        """

        return {
            "auth": self._saved_auth,
            "timeout": self._saved_timeout,
            "headers": self._saved_headers,
        }

    def __setstate__(self, state):
        """
        Recreate a fresh AsyncClient after deserialization.
        """

        self.__init__(
            auth=state.get("auth"),
            timeout=state.get(
                "timeout",
                120.0,
            ),
            headers=state.get(
                "headers",
                {},
            ),
        )

    def __deepcopy__(self, memo):
        """
        Return a newly constructed client instead of copying
        the internal CookieJar RLock.
        """

        copied_client = type(self)(
            auth=copy.deepcopy(
                self._saved_auth,
                memo,
            ),
            timeout=self._saved_timeout,
            headers=copy.deepcopy(
                self._saved_headers,
                memo,
            ),
        )

        memo[id(self)] = copied_client

        return copied_client