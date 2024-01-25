from aiogram.fsm.state import StatesGroup, State


class SetMedia(StatesGroup):
    get_media = State()
