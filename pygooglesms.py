"""
pygooglesms.py
Version: 1.0.1
Author: Reilly Steele
Modified: Feburary 3rd 2016

A super simple library used to send SMS messages from a google voice account.
Absolutely inspired by pygooglevoice, thanks Joe McCall & Justin Quick.

Usage:
    >>> from pygooglesms import GoogleSMS
    >>> gsms = GoogleSMS('email@gmail.com', 'password')
    >>> gsms.send('4445556666', 'yo dawg')
    >>>

Notes:
    You probably need to log in from the same IP manually before using this
    library, it does not handle any kind of 2 factor authentication.
"""

from bs4 import BeautifulSoup
import requests

LOGIN_PAGE_PRE = "https://accounts.google.com/ServiceLogin?service=grandcentral"
LOGIN_PAGE_AUTH = "https://accounts.google.com/ServiceLoginAuth"
GV_PAGE = "https://google.com/voice?pli=1&auth=%s"
SMS_PAGE = "https://www.google.com/voice/sms/send/"

class GoogleAuthError(Exception):
    """ Exception for failures during authentication attempts """
    def __init__(self, message, request):
        super(GoogleAuthError, self).__init__(message)
        self.message = message
        self.request = request

class GoogleVoiceError(Exception):
    """ Exception for failures unrelated to Authentication """
    pass

class InternalError(Exception):
    """ Exception for internal errors used to pass failure information """
    def __init__(self, payload):
        super(InternalError, self).__init__('InternalError')
        self.payload = payload


class GoogleSMS(object):
    """ Handles the login and sending of sms messages through google voice """
    _interesting_cookies = [
            "APISID", "HSID", "NID",
            "S", "SAPISID", "SID",
            "SSID", "_ga", "_gat",
            "GAPS", "LSID", "gv",
            "GALX"]

    def __init__(self, email, passwd):
        self.cookies = None
        self._rnr_se = None
        self.login(email, passwd)


    def _update_cookies(self, req):
        """ Takes a request and updates this object's cookies with any that are
        "interesting" and may be used by future requets """
        history = list(req.history)
        all_requests = history + [req,]
        for request in all_requests:
            for cookie in request.cookies.keys():
                if cookie in self._interesting_cookies:
                    self.cookies.set(cookie, request.cookies.get(cookie))

    def _request(self, method, url, params, no_validate=False):
        """ Issues a request using the object's cookies, expects only status
        code 200 unless otherwise specified """
        if method == "GET":
            request = requests.get(url, params=params, cookies=self.cookies)
        elif method == "POST":
            request = requests.post(url, params=params, cookies=self.cookies)

        if not no_validate and request.status_code != 200:
            raise RuntimeError(request)
        self._update_cookies(request)
        return request

    def _get(self, url, params=None):
        """ Convenience for get requests """
        return self._request("GET", url, params)

    def _post(self, url, params=None):
        """ Convenience for post requests """
        return self._request("POST", url, params)

    @staticmethod
    def _validate_gv(request):
        """ Validates the content of the GV page after the requests completes.
        This will raise an error if the logged in user does not have a google
        voice number configured """
        soup = BeautifulSoup(request.text, "html.parser")

        scripts = soup.findAll("script")
        gc_data_script = scripts[-1]
        gc_data_text = gc_data_script.text
        if "'formatted'" not in gc_data_text:
            raise GoogleVoiceError('No GoogleVoice number found, have you '
                'configured GoogleVoice?')
        # TODO: extract phone number

    def login(self, email, passwd):
        """ Logs the user in to google voice and gathers the info required to
        send sms messages, can be called again to switch accounts """
        self.cookies = requests.cookies.RequestsCookieJar()
        self._rnr_se = None

        try:
            request = self._get(LOGIN_PAGE_PRE)
        except InternalError as error:
            raise GoogleAuthError('Could not load Google login', error.payload)

        params = {}
        soup = BeautifulSoup(request.text, "html.parser")
        form_children = soup.find("form").findChildren()
        for child in form_children:
            name = child.get("name")
            if name is not None:
                params[name] = child.get("value")

        params["Email"] = email
        params["Passwd"] = passwd

        try:
            request = self._post(LOGIN_PAGE_AUTH, params)
        except InternalError as error:
            raise GoogleAuthError("Could not authenticate", error.payload)

        sid = self.cookies.get("SID")
        if sid is None:
            raise GoogleAuthError("No auth token provided by server (Bad "
                    "account?)", None)

        try:
            request = self._post(GV_PAGE % sid)
            self._validate_gv(request)
        except InternalError as error:
            raise GoogleVoiceError('Could not load GoogleVoice', error.payload)

        soup = BeautifulSoup(request.text, "html.parser")
        self._rnr_se = soup.find(attrs={"name":"_rnr_se"}).get("value")

    def send(self, phone_number, text):
        """ Sends an SMS message """
        if self._rnr_se is None:
            raise GoogleVoiceError("Not logged in")

        params = {'phoneNumber' : phone_number,
                'text' : text,
                '_rnr_se' : self._rnr_se,
                'sendErrorSms' : 0}
        self._post(SMS_PAGE, params)
