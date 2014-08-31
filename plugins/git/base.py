"""
Base class for handling github type book keeping
"""
import os
import requests


class GithubBaseMixIn(object):
    """
    Adds methods for making api calls, sets up the requests.Session,
    and the API keys for both GHE and GHC
    """

    GHE_API_URL = 'https://github.mit.edu/api/v3/'
    GHC_API_URL = 'https://api.github.com/'

    GHE_API_KEY = os.environ.get('GHE_API_KEY', None)
    GHC_API_KEY = os.environ.get('GHC_API_KEY', None)

    @property
    def ghe_session(self):
        """
        Gets a requests.Session object initialized with
        the GitHub Enterprise base key, or None if no
        key is set.
        """
        if not self.GHE_API_KEY:
            return None
        if not hasattr(self, '_ghe_session'):
            self._ghe_session = requests.Session()
            self._ghe_session.headers = {
                'Authorization': 'token {0}'.format(self.GHE_API_KEY),
                'User-Agent': 'Doof'
            }
        return self._ghe_session

    @property
    def ghc_session(self):
        """
        Gets a requests.Session object initialized with
        the GitHub.com base key, or None if no
        key is set.
        """
        if not self.GHC_API_KEY:
            return None
        if not hasattr(self, '_ghc_session'):
            self._ghc_session = requests.Session()
            self._ghc_session.headers = {
                'Authorization': 'token {0}'.format(self.GHC_API_KEY),
                'User-Agent': 'Doof'
            }
        return self._ghc_session

    def get_all(self, use_ghe, url):
        """
        Iterate through all results returned by github since it
        maxes requests at 30 and return the entire list.
        """
        if use_ghe:
            session = self.ghe_session
        else:
            session = self.ghc_session
        results = None
        response = session.get(url)
        if response.status_code == 200:
            results = response.json()
            while response.links.get('next', False):
                response = session.get(response.links['next']['url'])
                results += response.json()
        return results
