"""
Runs checks for whether a course is setup properly in github.
Checks branchs, repo, hooks, team, etc
"""

from will.plugin import WillPlugin
from will.decorators import respond_to

from plugins.git.base import GithubBaseMixIn


class CoursePlugin(WillPlugin, GithubBaseMixIn):

    DEPLOYMENT_TEAMS = ['mitx-content-deployment', ]
    STAGING_HOST = 'gr-rp'
    PROD_HOST = 'prod-gr-rp'
    INATOR_HOST = 'gr-inator'

    def check_hook(self, use_ghe, owner, repo, host):
        """
        Checks that the git hook is in place for the
        hostname specified and is the form type
        """
        has_hook = False
        correct_type = False
        base_dns = '.mitx.mit.edu'

        hooks, err = self.get_all(
            use_ghe,
            'repos/{}/{}/hooks'.format(owner, repo)
        )
        if not hooks:
            return (False, False)
        for hook in hooks:
            url = hook['config'].get('url', None)
            if url:
                if '{0}{1}'.format(host, base_dns) in url:
                    has_hook = True
                    if 'form' == hook['config']['content_type'].lower():
                        correct_type = True
                    break
        return (has_hook, correct_type)

    def add_check_row(self, is_good, item):
        """
        Makes a tr with a checkmark or x mark
        """
        if is_good:
            status = '&#x2713;'
        else:
            status = '&#x2718;'
        return '<tr><td>{0}</td><td>{1}</td></tr>'.format(status, item)

    @respond_to('github course check for '
                '(?P<owner>[\w\-_]+)/(?P<repo>[\w\-_]+)')
    def course_check(self, message, owner, repo):
        """
        github: github course check for &lt;owner&gt;/&lt;repo&gt;
        """
        # Find the repo first
        url = 'repos/{0}/{1}'.format(owner, repo)
        is_ghe = True

        repo_dict, err = self.get_all(True, url)
        if not repo_dict:
            repo_dict, err = self.get_all(False, url)
            is_ghe = False
        if not repo_dict:
            self.reply(
                message,
                "All my searching for nothing, that repo doesn't exist for me."
            )
            return

        # Make start of reply table
        table = [('<table><thead><tr>'
                  '<td>Status</td>'
                  '<td>Item</td>'
                  '</tr></thead><tbody>'), ]
        # Check privacy
        table.append(self.add_check_row(
            repo_dict['private'], 'Repo is private'
        ))

        # Find out if it is studio
        if 'studio' in url.lower():
            table.append(self.add_check_row(
                True, 'Studio course and has github repo'
            ))
        else:
            table.append(self.add_check_row(
                True, 'XML based course'
            ))
            # Check that it has live branch
            branch, err = self.get_all(
                is_ghe,
                'repos/{0}/{1}/branches/live'.format(owner, repo)
            )
            has_live = False
            if branch:
                has_live = True
            table.append(self.add_check_row(has_live, 'Has live branch'))

            # Check hook to staging
            has_hook, type_check = self.check_hook(
                is_ghe, owner, repo, self.STAGING_HOST
            )
            table.append(self.add_check_row(
                has_hook, 'Has hook to staging.mitx.mit.edu'
            ))
            table.append(self.add_check_row(
                type_check, 'Correct hook type (form) for staging'
            ))
            # Check hook to inator
            has_hook, type_check = self.check_hook(
                is_ghe, owner, repo, self.INATOR_HOST
            )
            table.append(self.add_check_row(
                has_hook, 'Has hook to my beloved lms-inator.mitx.mit.edu'
            ))
            table.append(self.add_check_row(
                type_check, 'Correct hook type (form) for inator'
            ))

        # All repos need to have hook to prod
        has_hook, type_check = self.check_hook(
            is_ghe, owner, repo, self.PROD_HOST
        )
        table.append(self.add_check_row(
            has_hook, 'Has hook to lms.mitx.mit.edu'
        ))
        table.append(self.add_check_row(
            type_check, 'Correct hook type (form) for lms'
        ))
        # Get the teams to check for deploy
        team_list, err = self.get_all(
            is_ghe,
            'repos/{0}/{1}/teams'.format(owner, repo)
        )
        has_deploy_team = False
        html_team_list = ['<ul>', ]
        if team_list:
            for team in team_list:
                html_team_list.append(team['name'])
                if team['name'].lower() in self.DEPLOYMENT_TEAMS:
                    has_deploy_team = True
        html_team_list.append('</ul>')

        table.append(self.add_check_row(
            has_deploy_team,
            'Has deployment team'
        ))
        table.append('</tbody></table>')

        self.reply(
            message,
            '<b>{0}-inator checklist:</b><br />{0}<br />{1}'.format(
                repo,
                ''.join(table),
                ''.join(html_team_list)
            ),
            html=True
        )
