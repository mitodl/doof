from will.plugin import WillPlugin
from will.decorators import reply


class OpsMap(WillPlugin):
    """
    Random Doofenshmirtz hear responses
    """

    @reply('map')
    def map(self, message):
        """map: map of MITx"""
        self.reply(
            message,
            '<img src="http://public.mitx.mit.edu/docs/'
            'great_map_of_mitx.mit.edu.png" />',
            html=True
        )
