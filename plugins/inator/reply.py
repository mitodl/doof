import operator
import requests
from requests.exceptions import RequestException

from will.plugin import WillPlugin
from will.decorators import respond_to, hear


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

    @respond_to("award (?P<num_gnomes>\d)+ garden gnomes? to "
                "(?P<user_name>.*)")
    def garden_gnomes(self, message, num_gnomes=1, user_name=None):
        """
        garden_gnomes: award special recognition
        """
        gnomes = self.load("garden_gnomes", {})
        user_gnomes = int(gnomes.get(user_name, 0))
        if not user_gnomes:
            gnomes[user_name] = int(num_gnomes)
        else:
            gnomes[user_name] = int(num_gnomes) + user_gnomes
        self.save("garden_gnomes", gnomes)
        self.say("Awarded {0} gnomes to {1}.".format(
            num_gnomes,
            user_name
        ), message=message)

    @respond_to("garden gnome tally")
    def gold_star_tally(self, message):
        """
        garden_gnomes: tally
        """
        gnomes = self.load("garden_gnomes", {})
        sorted_gnomes = sorted(gnomes.iteritems(), key=operator.itemgetter(1),
                               reverse=True)
        response = ['Garden gnomepocalypse leader board: <br /><ol>']
        for users in sorted_gnomes:
            response.append('<li>{1} - {0}</li>'.format(*users))

        self.reply(
            message,
            ''.join(response),
            html=True
        )

    @hear("thanks?( you)?")
    def thank_you_gnome(self, message):
        user = message.sender['nick']
        gnomes = self.load('garden_gnomes', {})
        user_gnomes = int(gnomes.get(user, 0))
        if not user_gnomes:
            gnomes[user] = 1
        else:
            gnomes[user] = 1 + user_gnomes
        self.save('garden_gnomes', gnomes)

    @hear("please")
    def please_gnome(self, message):
        user = message.sender['nick']
        gnomes = self.load('garden_gnomes', {})
        user_gnomes = int(gnomes.get(user, 0))
        if not user_gnomes:
            gnomes[user] = 1
        else:
            gnomes[user] = 1 + user_gnomes
        self.save('garden_gnomes', gnomes)
