"""
Commands for github hooks.
"""

from requests.exceptions import RequestException
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
                hook['config']['url'] = "Not Web hook"

            if not hook['config'].get('content_type'):
                hook['config']['content_type'] = 'no type'

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

    @respond_to('github hooks for (?P<owner>[\w\-_]+)/(?P<repo>[\w\-_]+)')
    def hooks_for_repo(self, message, owner, repo):
        """
        github: github hooks for &lt;owner&gt;/&lt;repo&gt;
        """
        ghe_message = None
        ghc_message = None

        if not self.ghe_session:
            ghe_message = ('You forget to give me the Github Enterprise Key. '
                           "Now THAT'S what I call getting the boot!")
        url = '{}repos/{}/{}/hooks'.format(self.GHE_API_URL, owner, repo)
        try:
            ghe_results = self.get_all(True, url)
        except RequestException:
            ghe_message = self.DOOF_REQ_EXCEPT

        if ghe_results:
            ghe_message = '<b>GHE Triggers for repo:</b><br />{}<br />'.format(
                self.make_hook_table(ghe_results)
            )

        if not self.ghc_session:
            ghc_message = ("You forget to give me the Github.com Key. "
                           "I trusted you and you just cast me aside like "
                           "a... like... like an old newspaper. He didn't "
                           "even wrap fish in me. Now THAT'S what I call "
                           "getting the boot!")

        url = '{}repos/{}/{}/hooks'.format(self.GHC_API_URL, owner, repo)
        try:
            ghc_results = self.get_all(True, url)
        except RequestException:
            ghc_message = self.DOOF_REQ_EXCEPT

        if ghc_results:
            ghc_message = (
                '<b>Github.com Triggers for repo:</b><br />{}<br />'.format(
                    self.make_hook_table(ghc_results)
                )
            )
        if not ghe_message:
            ghe_message = "No hooks or repo doesn't exist at GHE"
        if not ghc_message:
            ghc_message = "No hooks or repo doesn't exist at github.com"

        self.reply(
            message,
            '{0}{1}'.format(ghe_message, ghc_message),
            html=True,
            notify=False,
            color='green'
        )
