"""
Commands for working with github issues
"""
import json
import logging

from will.plugin import WillPlugin
from will.decorators import respond_to, rendered_template

from plugins.git.base import GithubBaseMixIn


log = logging.getLogger(__name__)


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

    @respond_to('github copy issues from '
                '(?P<src_gh>ghc|ghe)/(?P<src_owner>[\d\w\-_]+)/'
                '(?P<src_repo>[\d\w\-_]+)'
                ' to '
                '(?P<dst_gh>ghc|ghe)/(?P<dst_owner>[\d\w\-_]+)/'
                '(?P<dst_repo>[\d\w\-_]+)',
                admin_only=True)
    def copy_issues(
            self, message, src_gh, src_owner,
            src_repo, dst_gh, dst_owner, dst_repo
    ):
        """
        github: github copy issues from
        &lt;ghc|ghe&gt;/&lt;src_owner&gt;/&lt;src_repo&gt
        to &lt;ghc|ghe&gt;/&lt;src_owner&gt;/&lt;src_repo&gt
        """
        url = 'repos/{}/{}/issues?filter=all&state=open'.format(
            src_owner, src_repo
        )
        is_ghe = True if src_gh == 'ghe' else False

        src_results, err = self.get_all(is_ghe, url)

        if not src_results:
            self.reply(message, "Could not find any issues in source to copy")

        if dst_gh == 'ghe':
            dst_session = self.ghe_session
            base_url = self.GHE_API_URL
        else:
            dst_session = self.ghc_session
            base_url = self.GHC_API_URL
        url = '{base_url}repos/{dst_owner}/{dst_repo}/issues'.format(
            base_url=base_url, dst_owner=dst_owner, dst_repo=dst_repo
        )

        failed_issues = []
        for open_issue in src_results:
            copied_issue = {
                'title': open_issue['title'],
                'body': open_issue['body'],
                'labels': [x['name'] for x in open_issue['labels']],
            }

            issue_create = dst_session.post(url, data=json.dumps(copied_issue))
            if issue_create.status_code != 201:
                log.error(issue_create.text)
                failed_issues.append(open_issue)
        if len(failed_issues) != 0:
            context = {'failed_issues': failed_issues}
            self.reply(
                message,
                rendered_template('gh_copy_issues.html', context),
                html=True,
                notify=True,
                color='red'
            )
        else:
            self.reply(
                message,
                'Alright, time to get to work, my issues-transferinator '
                'was successful, but now the key holder needs to unwatch '
                'all {0} issues'.format(len(src_results)),
            )
