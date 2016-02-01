import sys
import unittest
import pygooglesms
from pygooglesms import GoogleSMS


class TestPyGoogleSMS(unittest.TestCase):
    GOOD_LOGIN = 'CHANGEME'
    GOOD_PASSWD = 'CHANGEME'
    TEST_NUMBER = 'CHANGEME'

    BAD_LOGIN = 'nobody@gmail.com'
    BAD_PASSWD = 'terrible'

    BAD_AUTH_MSG = 'No auth token provided by server (Bad account?)'
    NOT_LOGGED_IN_MSG = 'Not logged in'

    def test_good_login(self):
        GoogleSMS(self.GOOD_LOGIN, self.GOOD_PASSWD)

    def test_bad_login(self):
        try:
            GoogleSMS(self.BAD_LOGIN, self.BAD_PASSWD)
        except pygooglesms.GoogleAuthError as error:
            if error.message == self.BAD_AUTH_MSG:
                return
            raise error

    def test_bad_login_good_user(self):
        try:
            GoogleSMS(self.GOOD_LOGIN, self.BAD_PASSWD)
        except pygooglesms.GoogleAuthError as error:
            if error.message == self.BAD_AUTH_MSG:
                return
            raise error

    def test_sms_with_bad_login(self):
        sms = GoogleSMS(self.GOOD_LOGIN, self.GOOD_PASSWD)
        try:
            sms.login(self.BAD_LOGIN, self.BAD_PASSWD)
        except Exception:
            pass
        try:
            sms.send(self.TEST_NUMBER, 'test_message')
        except pygooglesms.GoogleVoiceError as error:
            if error.message == self.NOT_LOGGED_IN_MSG:
                return
            raise error

    def test_sms_with_good_login(self):
        sms = GoogleSMS(self.GOOD_LOGIN, self.GOOD_PASSWD)
        sms.send(self.TEST_NUMBER, 'test_message')
        # some way to validate this? send message to self?

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPyGoogleSMS)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    error = len(result.errors) + len(result.failures)
    sys.exit(error)
