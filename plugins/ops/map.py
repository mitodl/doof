from will.plugin import WillPlugin
from will.decorators import respond_to


class OpsMap(WillPlugin):
    """
    Random Doofenshmirtz hear responses
    """

    @respond_to('map')
    def map(self, message):
        """map: map of MITx"""
        self.reply(
            message,
            '<a href="http://public.mitx.mit.edu/docs/'
            'great_map_of_mitx.mit.edu.png"><img width=200 '
            'src="http://public.mitx.mit.edu/docs/'
            'great_map_of_mitx.mit.edu.png" /></a>',
            html=True
        )
