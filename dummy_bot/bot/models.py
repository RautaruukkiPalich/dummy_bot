
class TelegramUser:

    def __init__(self, message):
        self._group_id = str(message.chat.id),
        self._user_id = str(message.from_user.id),
        self._username = message.from_user.username,
        self._fullname = message.from_user.full_name,

    @property
    def group_id(self):
        return self._group_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def fullname(self):
        return self._fullname
