"""
Base class for handling github type book keeping
"""
import os

import requests
from requests.exceptions import RequestException


class GithubBaseMixIn(object):
    """
    Adds methods for making api calls, sets up the requests.Session,
    and the API keys for both GHE and GHC
    """

    GHE_API_URL = 'https://github.mit.edu/api/v3/'
    GHC_API_URL = 'https://api.github.com/'

    GHE_API_KEY = os.environ.get('GHE_API_KEY', None)
    GHC_API_KEY = os.environ.get('GHC_API_KEY', None)

    DOOF_REQ_EXCEPT = ("Well, that didn't work. And now we "
                       "have a two-ton ball of tin foil "
                       "going at 200 miles a hour heading "
                       "directly at us!")

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

    def repo_exists(self, use_ghe, owner, repo):
        """
        Returns true if the passed in repo exists
        """
        if use_ghe:
            session = self.ghe_session
            api_url = self.GHE_API_URL
        else:
            session = self.ghc_session
            api_url = self.GHC_API_URL

        repo = session.get('{0}repos/{1}/{2}'.format(
            api_url, owner, repo
        ))
        if repo.status_code == 404:
            return False
        else:
            return True

    def get_all(self, use_ghe, url):
        """
        Iterate through all results returned by github since it
        maxes requests at 30 and return the entire list.

        Args:
            use_ghe (bool): Use Enterprise or .com
            url (string): URL of API call without host

        Returns:
            tuple of Results of API call appended with all pages if it exceeds
            the total count and any error message that may have occurred
        """
        if use_ghe:
            session = self.ghe_session
            api_url = self.GHE_API_URL
            site_name = "Github Enterprise"
        else:
            session = self.ghc_session
            api_url = self.GHC_API_URL
            site_name = "Github.com"

        if not session:
            return(
                None,
                "You forgot to give me the {} API key. I trusted "
                "you and you just cast me aside like "
                "a... like... like an old newspaper. He didn't "
                "even wrap fish in me. Now THAT'S what I call "
                "getting the boot!".format(site_name)
            )

        results = None
        try:
            response = session.get('{0}{1}'.format(api_url, url))
            if response.status_code == 200:
                results = response.json()
                while response.links.get('next', False):
                    response = session.get(response.links['next']['url'])
                    results += response.json()
        except RequestException:
            return (None, self.DOOF_REQ_EXCEPT)

        error_message = None
        if not results:
            error_message = (
                'No results on {}. How completely unexpected. '
                'And by unexpected, I mean COMPLETELY EXPECTED!'
                ).format(site_name)
        return results, error_message
