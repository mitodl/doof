import requests
from requests.exceptions import RequestException

from will.plugin import WillPlugin
from will.decorators import respond_to


class RepliesPlugin(WillPlugin):

    @respond_to("^any new schemes\?")
    def schemeinator(self, message):
        """scheme: any new schemes?"""
        try:
            req = requests.get("http://randomword.setgetgo.com/get.php")
            word = req.text.replace('\n', '').replace('\r', '')
        except RequestException:
            word = "API-is-broken"
        self.reply(
            message,
            "Behold my new evil scheme, the {word}-Inator".format(word=word)
        )
