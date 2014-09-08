import operator
import requests
from requests.exceptions import RequestException

from will.plugin import WillPlugin
from will.decorators import respond_to, hear


class RepliesPlugin(WillPlugin):

    def get_jid(self, nick_or_name):
        jid = None
        for jid, info in self.internal_roster.items():
            if (info['nick'] == nick_or_name or
                    nick_or_name in info['name'] or
                    info['nick'] == nick_or_name.lstrip('@')):
                jid = jid
                break
        return jid

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

    @respond_to("award (?P<num_gnomes>\d)+ garden gnomes? to "
                "(?P<user_name>.*)")
    def garden_gnomes(self, message, num_gnomes=1, user_name=None):
        """
        garden_gnomes: award special recognition
        """
        gnomes = self.load("garden_gnomes", {})
        # Look up user in roster
        user_id = self.get_jid(user_name)
        if not user_id:
            self.reply('Unable to find {0}'.format(user_name))

        user_gnomes = int(gnomes.get(user_id, 0))
        if not user_gnomes:
            gnomes[user_id] = int(num_gnomes)
        else:
            gnomes[user_id] = int(num_gnomes) + user_gnomes
        self.save("garden_gnomes", gnomes)

        self.say("Awarded {0} gnomes to {1}.".format(
            num_gnomes,
            user_name
        ), message=message)

    @respond_to("garden gnome tally")
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
