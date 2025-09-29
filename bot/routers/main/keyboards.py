from aiogram.types import InlineKeyboardButton as IB, InlineKeyboardMarkup as IKM

from bot.type_defs.base_types import KbDataType, BTNDataType


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
                        key='ru',
                        callback=f'choose_language_ru'
                    ),
                    BTNDataType(
                        catalog='start_menu',
                        key='en',
                        callback=f'choose_language_en'
                    )
                ],
            ],
            back_to_main_menu=True
        )