from betamax import Betamax
from requests import Session
from unittest import TestCase

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


class TestGitHubAPI(TestCase):
    def setUp(self):
        self.session = Session()
        #self.headers.update(...)

    # Set the cassette in a line other than the context declaration
    def test_user(self):
        with Betamax(self.session) as vcr:
            vcr.use_cassette('user')
            resp = self.session.get('https://api.github.com/user',
                                    auth=('user', 'pass'))
            assert resp.json()['login'] is not None

    # Set the cassette in line with the context declaration
    def test_repo(self):
        with Betamax(self.session).use_cassette('repo'):
            resp = self.session.get(
                'https://api.github.com/repos/sigmavirus24/github3.py'
                )
            assert resp.json()['owner'] != {}
