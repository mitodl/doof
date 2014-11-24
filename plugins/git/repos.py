"""
Github repository related commands like listing repos in an org,
finding a repo, or other nonsense against the repo API.
"""

import logging

from will.plugin import WillPlugin
from will.decorators import respond_to

from plugins.git.base import GithubBaseMixIn

log = logging.getLogger('doof')


class GitHubReposPlugin(WillPlugin, GithubBaseMixIn):

    def get_repos_by_user(self, use_ghe, user):
        """
        Returns a dictionary of private and public repos
        for a given user or org, or fails and returns None
        """
        repos = None
        repos_dict = {}

        # Try org repos first, then users
        repos, err = self.get_all(use_ghe, 'orgs/{}/repos'.format(user))

        if repos:
            repos_dict['is_user'] = False
        else:
            repos, err = self.get_all(use_ghe, 'users/{}/repos'.format(user))
            if repos:
                repos_dict['is_user'] = True

        if not repos:
            return None, err

        repos_dict['private'] = sorted(
            [x for x in repos if x['private']]
        )
        repos_dict['public'] = sorted(
            [x for x in repos if not x['private']]
        )
        return repos_dict, err

    def format_repo_list(self, repos):
        """
        Returns a HTML unordered list of repos with links
        to the repo page
        """
        html_repo_list = ['<ul>', ]
        for repo in repos:
            html_repo_list.append(
                '<li><a href="{html_url}">{name}</a></li>'.format(**repo)
            )
        html_repo_list.append('</ul>')
        return html_repo_list

    @respond_to('github repos for (?P<user>[\d\w\-_]+)')
    def list_user_repos(self, message, user):
        """
        github: github repos for ___.
        """
        ghe_repos_dict, err = self.get_repos_by_user(True, user)

        if not ghe_repos_dict and err:
            ghe_message = err
        else:
            if ghe_repos_dict['is_user']:
                user_type = 'User'
            else:
                user_type = 'Org'
            ghe_message = (
                '{0} was a {1}<br />Private Repos:<br />{2}'
                '<br /><br />Public Repos:<br />{3}'.format(
                    user,
                    user_type,
                    ''.join(
                        self.format_repo_list(ghe_repos_dict['private'])
                    ),
                    ''.join(self.format_repo_list(ghe_repos_dict['public']))
                )
            )

        ghc_message = ''
        ghc_repos_dict, err = self.get_repos_by_user(False, user)

        if not ghc_repos_dict and err:
            ghc_message = err
        else:
            if ghc_repos_dict['is_user']:
                user_type = 'User'
            else:
                user_type = 'Org'
            ghc_message = (
                '{0} was a {1}<br />Private Repos:<br />{2}'
                '<br /><br />Public Repos:<br />{3}'.format(
                    user,
                    user_type,
                    ''.join(
                        self.format_repo_list(ghc_repos_dict['private'])
                    ),
                    ''.join(self.format_repo_list(ghc_repos_dict['public']))
                )
            )

        self.reply(
            message,
            ("Here are the amazing results of my github-inator:<br />\n"
             "<b>Github Enterprise:</b><br />\n{0}\n<br />"
             "<b>Github.com:</b><br />\n{1}").format(
                ghe_message, ghc_message
            ),
            html=True
        )

    @respond_to("^(github)? find repos? for course "
                "(?P<course_name>[\-\d\.\w]+).+")
    def find_repos_for_course(self, message, course_name):
        """github: find repos for course ___"""

        ghe_message = None
        ghc_message = None

        # First massage string into repo format
        course_name = course_name.replace('.', '')
        if course_name[-1].lower() in ['x', 'r']:
            course_name = course_name[:-1]
        course_name = 'content-mit-{}'.format(course_name)

        # Search GHE and the GHC
        url = 'search/repositories?q={}'.format(course_name)
        ghe_results, err = self.get_all(True, url)
        if err:
            ghe_message = err

        ghc_results, err = self.get_all(False, url)
        if err:
            ghc_message = err

        num_repos = 0
        if len(ghe_results.get('items', 0)) > 0:
            num_repos += len(ghe_results['items'])
            html_repo_list = self.format_repo_list(ghe_results['items'])
            ghe_message = (
                'Found {0} repos at  for course on GHE:\n<br />{1}'.format(
                    len(ghe_results['items']), '\n'.join(html_repo_list)
                )
            )
        if len(ghc_results.get('items', 0)) > 0:
            num_repos += len(ghc_results['items'])
            html_repo_list = self.format_repo_list(ghc_results['items'])
            ghc_message = (
                'Found {0} repos at  for course on GHC:\n<br />{1}'.format(
                    len(ghc_results['items']), '\n'.join(html_repo_list)
                )
            )
        scare_message = ''
        notify = False
        color = 'green'
        if num_repos > 2:
            scare_message = (
                '<b>Seriously!? Why so many repos for one '
                'course?! Sounds like you need my '
                'repo-delete-inator</b><br />'
            )
            color = 'red'
            notify = True
        self.reply(
            message,
            '{0}{1}{2}'.format(scare_message, ghe_message, ghc_message),
            html=True,
            notify=notify,
            color=color
        )
