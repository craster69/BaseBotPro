from aiogram.types import InlineKeyboardButton as IB, InlineKeyboardMarkup as IKM

from bot.type_defs.base_types import KbDataType, BTNDataType
from bot.utils.base_utils import get_languages


class MainMenuKb:
    def main_menu_kb(self) -> KbDataType:
        return KbDataType(
            buttons=[
                [
                    BTNDataType(
                        catalog='start_menu',
                        key='choose_language',
                        callback='choose_language'
                    )
                ]
            ]
        )


    def choose_language_kb(self) -> KbDataType:
        return KbDataType(
            buttons=[
                [
                    BTNDataType(
                        catalog='start_menu',
                        key=lang,
                        callback=f'choose_language_{lang}'
                    )
                ]
                for lang in get_languages()
            ],
            back_to_main_menu=True
        )