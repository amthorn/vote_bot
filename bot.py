import json

from ciscosparkapi import CiscoSparkAPI
from config import BOT_TOKEN


class SparkHook:
    def __init__(self, *args, **kwargs):
        self.api = CiscoSparkAPI(BOT_TOKEN)

    def handle(self, request):
        me = self.api.people.me()
        bot_id = me.id

        mentioned = request['data'].get('mentionedPeople', [])

        if bot_id not in mentioned:
            return 'OK'


        message_id = request['data']['id']
        raw_message = self.api.messages.get(message_id).text
        message = raw_message.replace(me.displayName, "", 1).strip()
        if message == raw_message and raw_message.startswith("Vote "):
            message = raw_message.replace("Vote ", "", 1)

        if message.startswith("new vote"):
            options = [i.strip() for i in message.replace("new vote", "", 1).strip().split(' ')]
            votes = {}
            for i in options:
                votes[i] = []

            json.dump(votes, open('votes.json', 'w'))
            self.api.messages.create(
                roomId=request['data']['roomId'],
                markdown="Let the voting begin. Tag me with your case-sensitive vote!"
            )
        elif message == 'talley':
            votes = json.load(open('votes.json', 'r'))
            self.api.messages.create(roomId=request['data']['roomId'], markdown=self.as_markdown(votes))
        else:
            votes = json.load(open('votes.json', 'r'))
            if message in votes:
                votes[message].append(self.api.people.get(request['data']['personId']).displayName)
                votes[message] = list(set(votes[message]))
                json.dump(votes, open('votes.json', 'w'))
                self.api.messages.create(roomId=request['data']['roomId'], markdown=self.as_markdown(votes))
            else:
                self.api.messages.create(
                    roomId=request['data']['roomId'],
                    markdown="'" + str(message) + "' not a valid option, please use one of: " + ', '.join(list(votes.keys()))
                )

        return 'OK'

    def as_markdown(self, votes):
        message = ''
        for k, v in votes.items():
            message += str(k) + ': ' + str(len(v)) + ((' (' + ', '.join(v) + ')\n\n') if len(v) else '\n\n')
        return message

