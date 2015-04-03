"""
Github repository related commands like listing repos in an org,
finding a repo, or other nonsense against the repo API.
"""

import logging

from will.plugin import WillPlugin
from will.decorators import respond_to

from plugins.git.base import GithubBaseMixIn

log = logging.getLogger('doof')


class GitHubStatsPlugin(WillPlugin, GithubBaseMixIn):

    @respond_to(
        'magic mirror in the cloud, who is the busiest repo of them all'
    )
    def most_popular_repo(self, message):
        """
        github: magic @doof on the cloud, who is the busiest repo of them all
        Most busy repos in mitodl/mitocw in last 4 weeks
        """
        self.reply(
            message,
            'Hold on, Perry the Judgapus, this is a LOT of API calls'
        )
        url = 'orgs/{0}/repos'
        repos = []
        for org in ['mitodl', 'mitocw']:
            repo_results, _ = self.get_all(False, url.format(org))
            repos.extend(repo_results)
        repos_by_commits = []
        for repo in repos:
            stats, _ = self.get_all(
                False,
                'repos/{full_name}/stats/participation'.format(
                    full_name=repo['full_name']
                )
            )
            if stats and stats.get('all'):
                all_commits = sum(stats['all'][:4])
                repos_by_commits.append((all_commits, repo['html_url']))
        repos_by_commits.sort(key=lambda tuple: tuple[0])
        repos_by_commits.reverse()
        self.reply(
            message,
            '{1} is the busiest of them all (with {0} commits)!'.format(
                *repos_by_commits[0]
            )
        )
        next_set = [
            '{1} ({0} commits)'.format(*x) for x in repos_by_commits[1:10]
        ]
        self.reply(
            message,
            'Followed shortly by:\n{runners_up}'.format(
                runners_up='\n'.join(next_set)
            )
        )
