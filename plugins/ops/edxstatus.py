import requests

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic


class EdxStatus(WillPlugin):

    EDX_STATUS = 'last_edx_status'
    EDX_STATUS_URL = 'http://status.edx.org/status/status.json'

    @periodic(second='36')
    def edx_is_up(self):
        status_json = requests.get(self.EDX_STATUS_URL).json()
        summary_status = status_json['summary_status'][0]['value']
        stored_status = self.load(self.EDX_STATUS)
        if summary_status != stored_status:
            if summary_status != 'operational':
                self.say('FYI everyone, edx.org is having trouble: {}\n'
                         'Last twitter update:\n{}'.format(
                             summary_status,
                             status_json['twitter'][0]['text']
                         ))
            else:
                self.say("Looks like edX is back up!")
            self.save(self.EDX_STATUS, summary_status)

    @respond_to('(?P<sudo>sudo )?edx status')
    def edx_status(self, message, sudo):
        """edx: edx status"""
        status_json = requests.get(self.EDX_STATUS_URL).json()
        if not sudo:
            self.reply(message, 'No')
            return
        response = ['<b>Since you asked forcefully, here is the status '
                    'for services on edx.org:<br /><ul>']
        for item in status_json['system_status']:
            if item['value'] == 'operational':
                status = '&#x2713;'
            else:
                status = '&#x2718;'
            response.append('<li>{0} - {1}</li>'.format(
                status, item['description']
            ))
        response.append('</ul>')

        self.reply(
            message,
            ''.join(response),
            html=True
        )
