from will.plugin import WillPlugin
from will.mixins.room import RoomMixin
from will.decorators import route


class PayNoHeed(WillPlugin, RoomMixin):

    @route('/curtain/<room>/<phrase>')
    def room_say(self, room, phrase):
        if room.isdigit():
            room = room
        else:
            room = self.get_room_from_name_or_id(room)
        self.say(phrase, room=room)
