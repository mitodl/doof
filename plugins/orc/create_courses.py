"""
Creation of courses (xml and studio) via orcoursetrion
"""
from orcoursetrion.actions import create_export_repo, create_xml_repo
from orcoursetrion.lib import GitHubException
import requests
from will.plugin import WillPlugin
from will.decorators import respond_to


class OrcCourseCreation(WillPlugin):
    """
    Course creation tasks for doof to do
    """

    @respond_to(
        'create studio course (?P<course>[\w+\.\-]+) '
        'for (?P<term>[\w\-]+)(: )?(?P<description>.+)'
    )
    def create_studio_course(self, message, course, term, description):
        """create studio course (course name, i.e. 6.001) for (term, i.e. Spring_2015): description"""
        try:
            repo = create_export_repo(course, term, description)
        except requests.RequestException, ex:
            self.reply(
                message,
                "I have no idea how this happened, but I couldn't "
                "even get a response using this stupid orcoursetrion-inator. "
                "This is the error I got: {0}".format(unicode(ex))
            )
        except GitHubException, ex:
            self.reply(
                message,
                "Man, why can't just one of my plans work, Curse you "
                "Perry the Platypus!\n{0}".format(unicode(ex))
            )

        self.reply(
            message,
            "You're probably just as surprised as I am that my plan "
            "actually worked.  Here is the repo I just "
            "made for you: {0}".format(
                repo['html_url']
            )
        )

    @respond_to(
        'create xml course (?P<course>[\w+\.\-]+) '
        'for (?P<term>[\w\-]+) with team (?P<team>[\s\w+\.\-]+)'
        '(: )?(?P<description>.+)$'
    )
    def create_xml_course(self, message, course, term, team, description):
        """create xml course (course name, i.e. 6.001) for (term, i.e. Spring_2015) with team: description"""
        try:
            repo = create_xml_repo(course, term, team, description)
        except requests.RequestException, ex:
            self.reply(
                message,
                "I have no idea how this happened, but I couldn't "
                "even get a response using this stupid orcoursetrion-inator. "
                "This is the error I got:\n {0}".format(unicode(ex))
            )
        except GitHubException, ex:
            self.reply(
                message,
                "Man, why can't just one of my plans work, Curse you "
                "Perry the Platypus!\n{0}".format(unicode(ex))
            )

        self.reply(
            message,
            "You're probably just as surprised as I am that my plan "
            "actually worked.  Here is the repo I just "
            "made for you: {0}".format(
                repo['html_url']
            )
        )
