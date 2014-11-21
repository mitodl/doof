"""
Commands for working with github issues
"""

from will.plugin import WillPlugin
from will.decorators import respond_to, rendered_template

from plugins.git.base import GithubBaseMixIn


class GitHubIssuesPlugin(WillPlugin, GithubBaseMixIn):
    """
    Bot related needs for issues
    """

    @respond_to('github issues for (?P<owner>[\d\w\-_]+)/(?P<repo>[\d\w\-_]+)')
    def issues_for_repo(self, message, owner, repo):
        """
        github: github issues for &lt;owner&gt;/&lt;repo&gt;
        """
        context = {}
        url = 'repos/{}/{}/issues?filter=all&state=open'.format(owner, repo)

        ghe_results, err = self.get_all(True, url)
        context['ghe_results'] = ghe_results
        context['ghe_error_message'] = err

        ghc_results, err = self.get_all(False, url)
        context['ghc_results'] = ghc_results
        context['ghc_error_message'] = err

        self.reply(
            message,
            rendered_template('gh_issues.html', context),
            html=True,
            notify=False,
            color='green'
        )
