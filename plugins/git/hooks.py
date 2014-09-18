"""
Commands for github hooks.
"""
from urlparse import urlparse

from will.plugin import WillPlugin
from will.decorators import respond_to

from plugins.git.base import GithubBaseMixIn


class GitHubHooksPlugin(WillPlugin, GithubBaseMixIn):

    def make_hook_table(self, hooks):
        """
        Make a nice html table with the hooks
        """
        hook_table = [('<table><thead><tr>'
                       '<td>Name</td>'
                       '<td>url</td>'
                       '<td>events</td>'
                       '<td>type</td>'
                       '<td>active</td>'
                       '</tr></thead><tbody>'), ]
        for hook in hooks:
            # Parse url to sanitize username and pass
            if hook['config'].get('url'):
                hook_url = urlparse(hook['config']['url'])
                hook['config']['url'] = ('{0.scheme}://{0.hostname}{0.path}'
                                         '?{0.query}'.format(hook_url))
            else:
                hook['config']['url'] = "n/a"

            if not hook['config'].get('content_type'):
                hook['config']['content_type'] = 'n/a'

            hook['events'] = ' '.join(hook['events'])
            hook_table.append('<tr>'
                              '<td>{name}</td>'
                              '<td>{config[url]}</td>'
                              '<td>{events}</td>'
                              '<td>{config[content_type]}</td>'
                              '<td>{active}</td>'
                              '</tr>'.format(**hook))
        hook_table.append('</tbody></table>')
        return ''.join(hook_table)

    @respond_to('github hooks for (?P<owner>[\d\w\-_]+)/(?P<repo>[\d\w\-_]+)')
    def hooks_for_repo(self, message, owner, repo):
        """
        github: github hooks for &lt;owner&gt;/&lt;repo&gt;
        """
        ghe_message = None
        ghc_message = None

        url = 'repos/{}/{}/hooks'.format(owner, repo)
        ghe_results, err = self.get_all(True, url)

        if ghe_results:
            ghe_message = '<b>GHE Triggers for repo:</b><br />{}<br />'.format(
                self.make_hook_table(ghe_results)
            )
        else:
            ghe_message = err

        ghc_results, err = self.get_all(False, url)

        if ghc_results:
            ghc_message = (
                '<b>Github.com Triggers for repo:</b><br />{}<br />'.format(
                    self.make_hook_table(ghc_results)
                )
            )
        else:
            ghc_message = err

        self.reply(
            message,
            '{0}{1}'.format(ghe_message, ghc_message),
            html=True,
            notify=False,
            color='green'
        )

    @respond_to('github global thermonuclear war '
                '(?P<owner>[\d\w\-_]+)/(?P<repo>[\d\w\-_]+) '
                '(?P<hook_host>[\d\w\-_\.]+) (?P<fire_number>\d+)',
                admin_only=True)
    def test_hook(self, message, owner, repo, hook_host, fire_number):
        """
        github: global thermonuclear war (admin only)
        """
        url = 'repos/{}/{}/hooks'.format(owner, repo)
        ghe_results, err = self.get_all(True, url)
        ghc_results, err = self.get_all(False, url)
        if ghc_results and ghe_results:
            self.reply(message,
                       "Ambiguous repo, and I don't know how to handle that")
            return
        if not ghc_results and not ghe_results:
            self.reply(message, "I wasn't able to find any player to engage "
                       "in thermonuclear war with (shrug).")
            return
        hooks = ghc_results or ghe_results
        target = None
        for hook in hooks:
            # Parse url to sanitize username and pass
            if hook['config'].get('url'):
                hook_url = urlparse(hook['config']['url'])
                if hook_host == hook_url.hostname:
                    if not target:
                        target = hook
                        break
                    else:
                        self.reply(message, 'Too many targets for ze missles')
                        return
        if ghc_results:
            target_session = self.ghc_session
            target_url = self.GHC_API_URL
        else:
            target_session = self.ghe_session
            target_url = self.GHE_API_URL
        # Finally have our target, make ready for war
        good_missles = 0
        for _ in range(fire_number):
            response = target_session.post(
                '{url}repos/{owner}/{repo}/hooks/{hook_id}/tests'.format(
                    url=target_url, owner=owner, repo=repo, hook_id=hook['id']
                )
            )
            if response.status_code == 204:
                good_missles += 1
        if good_missles == fire_number:
            self.reply(message,
                       'All {0} missles were fired successfully at the target '
                       '(boom) (dance) (chucknorris)'.format(fire_number))
        else:
            self.reply(
                message,
                'We had {0} duds (fwp) (facepalm) (taft) (omg)'.format(
                    fire_number-good_missles
                )
            )
