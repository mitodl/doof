"""
Listen to the chat and interject blather if certain keywords
are mentioned.
"""

import random

import requests
from will.plugin import WillPlugin
from will.decorators import hear


class InatorHear(WillPlugin):
    """
    Random Doofenshmirtz hear responses
    """

#    @hear('daily meet.*')
#    def dailyupdates(self,message):
#        self.say('Number: <a href="tel:+8662427949p4919652245">'
#                 '866-242-7949</a> Conference Code: 4919652245 '
#                 'Time: 9.30AM',
#                 html=True,
#                 color='purple',
#                 message=message)

    @hear('oo+h')
    def ohmy(self, message):
        """impersonate a second-grader"""
        self.say('ooooooohhh', message=message)

    @hear('hmm+')
    def hmm(self, message):
        """let's bring the conversation back around to me"""
        response_list = [
            'Hmm indeed, let us contemplate my childhood in Drusselstein',
            'Hmmm, do you think my theme song is too short?  '
            'I was thinking of adding "Home of the Inatoranator"',
            'Hmm, I was just thinking how much I hate my lousy brother',
            'Hmm, I was just wondering too. About how awesome the '
            'gnomepocalypse was',
            "That's a deep thought. Please tell us more.",
            ]
        self.say(random.choice(response_list), message=message)

    # This is stolen from edX's alton bot: https://github.com/edx/alton/pull/22
    @hear("alot")
    def alot(self, message):
        """show off a picture of an alot when someone is talking about one"""
        data = {"q": "alot", "v": "1.0", "safe": "active", "rsz": "8"}
        response = requests.get(
            "http://ajax.googleapis.com/ajax/services/search/images",
            params=data
        )
        results = response.json()["responseData"]["results"]
        if len(results) > 0:
            url = random.choice(results)["unescapedUrl"]
            self.say("%s" % url, message=message)

    @hear('surely')
    def surely(self, message):
        """70s jokes are back!"""
        self.say("Don't call me Shirley", message=message)

    @hear(r'( to me\.?|lgtm)$')
    def to_me(self, message):
        """get a song stuck in your head"""
        if should_i(10):
            self.say("To me, to meee, TO MEEEE!", message=message)

def should_i(percent):
    """Do something sometimes."""
    return random.choice(range(100)) < percent
