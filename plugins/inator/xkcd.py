import json
from urllib2 import urlopen, HTTPError
from StringIO import StringIO

from will.plugin import WillPlugin
from will.decorators import respond_to

class Xkcd(WillPlugin):
    """
    XKCD things
    """

    @respond_to("xkcd (?P<comic_id>[^\s]+)")
    def fetch_from_id(self, message, comic_id):
        """
        Fetch an XKCD comic from its ID
        """

        # Validate input
        try:
            comic_id = int(comic_id)
        except ValueError:
            self.reply(
                message,
                "That's not a valid xkcd comic number.."
            )
            return

        # Try to get the comic's information from the xkcd API
        try:
            xkcd_json = urlopen(
                "https://xkcd.com/{0}/info.0.json".format(comic_id)
            ).read()
        except HTTPError:
            self.reply(
                message,
                "I couldn't seem to find that comic.. Are you sure it exists?"
            )
            return

        # Parse the JSON and pull the image URL out
        try:
            parsed_json = json.load(StringIO(xkcd_json))
        except ValueError:
            self.reply(
                message,
                "Hm.. I'm having trouble parsing the JSON for this one:\n\n"
                "{0}".format(xkcd_json)
            )
            return
        try:
            image = parsed_json["img"]
        except KeyError:
            self.reply(
                message,
                "Hm.. I parsed the JSON, but I couldn't find the img key:\n\n"
                "{0}".format(str(parsed_json))
            )
            return

        self.reply(
            message,
            '<a href="{0}"><img src="{0}" /></a>'.format(image),
            html=True
        )
