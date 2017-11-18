import boto3

class Mail:
    def __init__(self, to, subject):
        self.destination = {'ToAddresses': [to]}
        self.message = {'Subject': {'Data': subject}}
        self._html = None
        self._text = None
        self._format = 'html'

    def html(self, html):
        self._html = html

    def text(self, text):
        self._text = text

    def send(self):
        body = self._html

        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'
            self.message['Body'] = {'Text': {'Data': self._text}}

        client = boto3.client('ses',  region_name='us-east-1')


        return client.send_email(
            Source='robert.dewilder@gmail.com',
            Destination=self.destination,
            Message=self.message
        )
