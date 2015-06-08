"""
Commands for working with github issues
"""
import json
import logging
import datetime

from will.plugin import WillPlugin
from will.decorators import respond_to, rendered_template, periodic

from plugins.git.base import GithubBaseMixIn


log = logging.getLogger(__name__)


class GitHubIssuesPlugin(WillPlugin, GithubBaseMixIn):
    """
    Bot related needs for issues
    """
    STATUS_OTHER = 0
    STATUS_NEEDS_REVIEW = 1
    STATUS_WORK_IN_PROGRESS = 2
    STATUS_QUESTION = 3
    STATUS_WAITING_ON_AUTHOR = 4

    STATUS_MERGED = 5
    STATUS_CLOSED = 6

    def issues_to_review(self):
        """Return a list of issues that need reviewing"""

        return [pr for pr in self.issues_open() if pr['status'] == self.STATUS_NEEDS_REVIEW]

    def issues_recently_merged(self):
        orgs = (
            ('mitodl', False),
            ('starteam', False),
            ('mitocw', False),
            ('mitx-devops', True)
        )
        prs = []
        for org in orgs:
            data, _ = self.get_all(
                org[1],
                'search/issues?q=user:{org} merged:>={today} type:pr'.format(
                    org=org[0],
                    today=datetime.datetime.now().date().isoformat()
                )
            )
            if data and data.get('items'):
                prs.extend(data['items'])

        def status_for_pr(pr):
            return self.STATUS_MERGED

        def with_status(pr):
            pr['status'] = status_for_pr(pr)
            return pr

        return [with_status(pr) for pr in prs]
        
    def issues_open(self):
        """Return a list of open issues"""
        orgs = (
            ('mitodl', False),
            ('starteam', False),
            ('mitocw', False),
            ('mitx-devops', True)
        )
        prs = []
        for org in orgs:
            data, _ = self.get_all(
                org[1],
                'search/issues?q=user:{org} is:open type:pr'.format(
                    org=org[0],
                    today=datetime.datetime.now().date().isoformat()
                )
            )
            if data and data.get('items'):
                prs.extend(data['items'])

        def status_for_pr(pr):
            # We should probably standardize on one
            review_labels = ('review-needed', 'Needs Review')
        
            for label_info in pr['labels']:
                for review_label in review_labels:
                    if label_info['name'] == review_label:
                        return self.STATUS_NEEDS_REVIEW
                if label_info['name'] == "work in progress":
                    return self.STATUS_WORK_IN_PROGRESS
                if label_info['name'] == "question":
                    return self.STATUS_QUESTION
                if label_info['name'] == "Waiting on Author":
                    return self.STATUS_WAITING_ON_AUTHOR
            return self.STATUS_OTHER

        def with_status(pr):
            pr['status'] = status_for_pr(pr)
            return pr

        return [with_status(pr) for pr in prs]

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

    @respond_to('github prs for review')
    def prs_need_review(self, message):
        """github: github prs for review"""
        # Search all PRs for odl and ocw on github.com and mitx-devops
        # on ghe.
        # orgs are a tuple of the name, and a boolean that is true if
        # it is on git hub enterprise, false is on github.com
        prs = self.issues_to_review()
        if len(prs) == 0:
            self.reply(
                message,
                (
                    "Stupid github-inator didn't return anything, either "
                    "you guys are way too nice, or my inator broke down "
                    "and I need to find a new switch or something to fix it."
                )
            )
            return

        self.reply(
            message,
            rendered_template('need_review.html', {'pull_requests': prs}),
            html=True,
            notify=True
        )

    @periodic(minute='*/10')
    def review_issue_wrangling(self):
        """
        Check for new PRs that need reviews and ones that have been reviewed
        """
        storage_key = 'old-prs'
        room = 'ODL engineering'

        current_prs = {x['html_url']: x for x in (self.issues_open() + self.issues_recently_merged())}
        old_prs = self.load(storage_key, [])

        def transition(from_statuses, to_statuses):
            from_set = {x['html_url'] for x in old_prs if x['status'] in from_statuses}
            to_set = {html_url for html_url, x in current_prs.items() if x['status'] in to_statuses}
            return to_set.intersection(from_set)

        def transition_new(from_statuses, to_statuses):
            # transitions between one of from_statuses to one of to_statuses,
            # or from nothing to to_statuses
            from_set = {x['html_url'] for x in old_prs}
            to_set = {html_url for html_url, x in current_prs.items() if x['status'] in to_statuses}
            return transition(from_statuses, to_statuses) + (to_set - from_set)

        all_statuses = {self.STATUS_OTHER,
                        self.STATUS_NEEDS_REVIEW,
                        self.STATUS_WORK_IN_PROGRESS,
                        self.STATUS_QUESTION,
                        self.STATUS_WAITING_ON_AUTHOR,
                        self.STATUS_MERGED,
                        self.STATUS_CLOSED}
        
        for pr_url in transition({self.STATUS_NEEDS_REVIEW}, {self.STATUS_MERGED}):
            self.say(
                'Congratulations {username} <a href="{url}">{title}</a> has '
                'been merged.'.format(
                    username=old_prs[pr_url]['user']['login'],
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )

        for pr_url in transition({self.STATUS_NEEDS_REVIEW}, {self.STATUS_CLOSED}):
            self.say(
                'PR for review <a href="{url}">{title}</a> '
                'was closed without being merged!'.format(
                    username=old_prs[pr_url]['user']['login'],
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )
        for pr_url in transition({self.STATUS_NEEDS_REVIEW}, {self.STATUS_WAITING_ON_AUTHOR}):
            self.say(
                'Note to {username}: PR <a href="{url}">{title}</a> was reviewed and is waiting '
                'for you.'.format(
                    username=old_prs[pr_url]['user']['login'],
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )
            
        for pr_url in transition({self.STATUS_NEEDS_REVIEW}, {self.STATUS_QUESTION}):
            self.say(
                'Attention! {username} has a question about PR <a href="{url}">{title}</a>'
                '.'.format(
                    username=old_prs[pr_url]['user']['login'],
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )
            
        for pr_url in transition({self.STATUS_WAITING_ON_AUTHOR}, {self.STATUS_NEEDS_REVIEW}):
            self.say(
                '{username} has finished looking over the PR and <a href="{url}">{title}</a>'
                ' needs review again.'.format(
                    username=old_prs[pr_url]['user']['login'],
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )
            
        for pr_url in transition({self.STATUS_QUESTION}, all_statuses - {self.STATUS_QUESTION}):
            self.say(
                'Question for PR <a href="{url}">{title}</a> was answered!'.format(
                    url=old_prs[pr_url]['html_url'],
                    title=old_prs[pr_url]['title']
                    ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )            

        for pr_url in transition_new(all_statuses - {self.STATUS_NEEDS_REVIEW,
                                                     self.STATUS_WAITING_ON_AUTHOR},
                                 {self.STATUS_NEEDS_REVIEW}):
            self.say(
                'Alert! Alert! New PR hot off the presses.<br>'
                '<a href="{url}">{title}</a> by {username}'.format(
                    url=current_prs[pr_url]['html_url'],
                    title=current_prs[pr_url]['title'],
                    username=current_prs[pr_url]['user']['login']
                ),
                html=True,
                notify=True,
                room=self.get_room_from_name_or_id(room)
            )

        # TODO: what should happen for other transition states?
            
        self.save(storage_key, current_prs)
