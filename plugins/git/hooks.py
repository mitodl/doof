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

        ghc_results, err = self.get_all(True, url)

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
