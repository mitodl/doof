"""
Github repository related commands like listing repos in an org,
finding a repo, or other nonsense against the repo API.
"""

import logging
from requests.exceptions import RequestException

from will.plugin import WillPlugin
from will.decorators import respond_to

from plugins.git.base import GithubBaseMixIn

log = logging.getLogger('doof')


class GitHubReposPlugin(WillPlugin, GithubBaseMixIn):

    DOOF_REQ_EXCEPT = ("Well, that didn't work. And now we "
                       "have a two-ton ball of tin foil "
                       "going at 200 miles a hour heading "
                       "directly at us!")

    def get_repos_by_user(self, use_ghe, user):
        """
        Returns a dictionary of private and public repos
        for a given user or org, or fails and returns None
        """
        repos = None
        repos_dict = {}
        if use_ghe:
            url = self.GHE_API_URL
        else:
            url = self.GHC_API_URL

        # Try org repos first, then users
        repos = self.get_all(use_ghe, '{}orgs/{}/repos'.format(url, user))
        if repos:
            repos_dict['is_user'] = False
        else:
            repos = self.get_all(use_ghe, '{}users/{}/repos'.format(url, user))
            if repos:
                repos_dict['is_user'] = True

        if not repos:
            return None

        repos_dict['private'] = [x['name']
                                 for x in repos
                                 if x['private']]
        repos_dict['public'] = [x['name']
                                for x in repos
                                if not x['private']]
        return repos_dict

    @respond_to('github repos for (?P<user>[\w\-_]+)')
    def list_user_repos(self, message, user):
        """
        github: github repos for ___.
        """
        ghe_message = ''
        ghe_repos_dict = {}

        if not self.ghe_session:
            ghe_message = ('You forget to give me the Github Enterprise Key. '
                           "Now THAT'S what I call getting the boot!")
        try:
            ghe_repos_dict = self.get_repos_by_user(True, user)
        except RequestException:
            ghe_message = self.DOOF_REQ_EXCEPT

        if not ghe_repos_dict:
            ghe_message = ("There are no GHE repos for that thing you "
                           "entered. I know what you're thinking, but "
                           "this is neither ironic nor funny.")
        else:
            if ghe_repos_dict['is_user']:
                user_type = 'User'
            else:
                user_type = 'Org'
            ghe_message = (
                '{0} was a {1}\nPrivate Repos:\n{2}\n\n'
                'Public Repos:\n{3}'.format(
                    user,
                    user_type,
                    '\n'.join(ghe_repos_dict['private']),
                    '\n'.join(ghe_repos_dict['public'])
                )
            )

        ghc_message = ''
        ghc_repos_dict = {}
        if not self.ghe_session:
            ghc_message = ("You forget to give me the Github.com Key. "
                           "I trusted you and you just cast me aside like "
                           "a... like... like an old newspaper. He didn't "
                           "even wrap fish in me. Now THAT'S what I call "
                           "getting the boot!")
        try:
            ghc_repos_dict = self.get_repos_by_user(False, user)
        except RequestException:
            ghc_message = self.DOOF_REQ_EXCEPT

        if not ghc_repos_dict:
            ghc_message = ("There are no github.com repos for that thing you "
                           "entered. I could keep looking, but I doubt it "
                           "will help.")
        else:
            if ghc_repos_dict['is_user']:
                user_type = 'User'
            else:
                user_type = 'Org'
            ghc_message = (
                '{0} was a {1}\nPrivate Repos:\n{2}\n\n'
                'Public Repos:\n{3}'.format(
                    user,
                    user_type,
                    '\n'.join(ghc_repos_dict['private']),
                    '\n'.join(ghc_repos_dict['public'])
                )
            )

        self.reply(
            message,
            ("Here are the amazing results of my github-inator:\n"
             "Github Enterprise:\n{0}\nGithub.com:\n{1}").format(
                ghe_message, ghc_message
            )
        )
