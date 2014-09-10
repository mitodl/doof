import operator
import requests
from requests.exceptions import RequestException

from will.plugin import WillPlugin
from will.decorators import respond_to, hear


class RepliesPlugin(WillPlugin):

    def get_jid(self, nick_or_name):
        result = None
        for jid, info in self.internal_roster.items():
            if (info['nick'] == nick_or_name or
                    nick_or_name.lower() in info['name'].lower() or
                    info['nick'] == nick_or_name.lstrip('@')):
                result = jid
                break
        return result

    def plus_one_gnome(self, nick):
        user_id = self.get_jid(nick)

        gnomes = self.load('garden_gnomes', {})
        user_gnomes = int(gnomes.get(user_id, 0))
        if not user_gnomes:
            gnomes[user_id] = 1
        else:
            gnomes[user_id] = 1 + user_gnomes
        self.save('garden_gnomes', gnomes)

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

    @respond_to("(award|issue|grant) (?P<num_gnomes>[^\s]+) (garden )?gnomes? "
                "to (?P<user_name>.*)")
    def garden_gnomes(self, message, num_gnomes=1, user_name=None):
        """
        garden_gnomes: award special recognition
        """
        # Input sanitation and syntax hints
        if num_gnomes in {'a', 'one'}:
            num_gnomes = 1
        try:
            num_gnomes = float(num_gnomes)
        except ValueError:
            self.reply(
                message,
                "What? How many garden gnomes?"
            )
            return
        if num_gnomes%1:
            self.reply(
                message,
                "Do you really expect me to go cutting up garden gnomes!?"
            )
            return
        num_gnomes = int(num_gnomes)
        if num_gnomes < 0:
            self.reply(
                message,
                "No, I won't take away garden gnomes. These people have "
                "earned them through hard work and dedication."
            )
            return
        elif num_gnomes == 0:
            self.reply(
                message,
                "Not even one garden gnome? What a shame."
            )
            return

        gnomes = self.load("garden_gnomes", {})
        # Look up user in roster
        user_id = self.get_jid(user_name)
        if not user_id:
            self.reply(
                message,
                "Sorry, I don't know who {0} is.".format(user_name)
            )
            return

        user_gnomes = int(gnomes.get(user_id, 0))
        if not user_gnomes:
            gnomes[user_id] = int(num_gnomes)
        else:
            gnomes[user_id] = int(num_gnomes) + user_gnomes
        self.save("garden_gnomes", gnomes)

        if num_gnomes == 1:
            self.say("Awarded a gnome to {0}.".format(
                user_name
            ), message=message)
        else:
            self.say("Awarded {0} gnomes to {1}.".format(
                num_gnomes,
                user_name
            ), message=message)

    @respond_to("(garden )?gnomes? tally")
    def garden_gnome_tally(self, message):
        """
        garden_gnomes: tally
        """
        gnomes = self.load("garden_gnomes", {})
        sorted_gnomes = sorted(gnomes.iteritems(), key=operator.itemgetter(1),
                               reverse=True)
        response = ['Garden gnomepocalypse leader board: <br /><ol>']
        for users in sorted_gnomes:
            user = self.get_user_by_jid(users[0])
            if not user:
                continue
            response.append('<li>{0} - {1}</li>'.format(
                users[1],
                user['name']
            ))

        self.reply(
            message,
            ''.join(response),
            html=True
        )

    @hear("thanks?( you)?")
    def thank_you_gnome(self, message):
        self.plus_one_gnome(message.sender['nick'])

    @hear("please")
    def please_gnome(self, message):
        self.plus_one_gnome(message.sender['nick'])
