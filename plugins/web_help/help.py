from will.plugin import WillPlugin
from will.decorators import route


class WebHelp(WillPlugin):
    """
    Make a Web page version of help for ooc access.
    """

    @route('/help')
    def web_help(self):
        """
        web help: View help in browser by going to /help.
        """
        # help_data = self.load("help_files")
        help_modules = self.load("help_modules")

        help_text = "Here's what I know how to do:"

        for k in sorted(help_modules, key=lambda x: x[0]):
            help_data = help_modules[k]
            if help_data and len(help_data) > 0:
                help_text += "<br/><br/><b>%s</b>:" % k
                for line in help_data:
                    if line:
                        if ":" in line:
                            line = "&nbsp; <b>%s</b>%s" % (
                                line[:line.find(":")], line[line.find(":"):]
                            )
                        help_text += "<br/> %s" % line
        return help_text

    @route('/programmer_help')
    def programmer_help(self):
        """web programmer help: view programmer help in browser by going
        to/programmer_help.
        """
        all_regexes = self.load("all_listener_regexes")
        help_text = "Here's everything I know how to listen to:"
        help_text += "<ul>"
        for r in all_regexes:
            help_text += "<li>%s</li>" % r
        help_text += "</ul>"
        return help_text
