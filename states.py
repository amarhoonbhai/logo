from aiogram.dispatcher.filters.state import State, StatesGroup

class CollageStates(StatesGroup):
    waiting_for_images = State()
    waiting_for_grid = State()
    waiting_for_background = State()
    waiting_for_border = State()