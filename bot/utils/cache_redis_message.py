from bot.type_defs.base_types import (
    KbDataType, 
    MessageDataType, 
    MediaContentForMsgDataType, 
    BTNDataType
)

from dataclasses import asdict

from aiogram.types import InlineKeyboardButton as IB


class CacheRedisMessage:
    @classmethod
    def pack(cls, msg_data: MessageDataType) -> dict:
        if msg_data.keyboard and msg_data.keyboard.buttons:
            for row_index in range(0, len(msg_data.keyboard.buttons)):
                new_row = []
                for btn in msg_data.keyboard.buttons[row_index]:
                    if isinstance(btn, BTNDataType):
                        new_row.append(asdict(btn))
                    elif isinstance(btn, IB):
                        new_row.append(btn.json())
                    else:
                        new_row.append(btn)
                msg_data.keyboard.buttons[row_index] = new_row
            msg_data.keyboard = asdict(msg_data.keyboard)
            
        return asdict(msg_data)


    @classmethod
    def unpack(cls, msg_data: MessageDataType) -> MessageDataType:
        if isinstance(msg_data.keyboard, dict):
            msg_data.keyboard = KbDataType(**msg_data.keyboard)
            if msg_data.keyboard.buttons:
                for row_index in range(0, len(msg_data.keyboard.buttons)):
                    new_row = []
                    for btn in msg_data.keyboard.buttons[row_index]:
                        try:
                            new_row.append(BTNDataType(**btn))
                        except:
                            new_row.append(btn)
                    msg_data.keyboard.buttons[row_index] = new_row
        if isinstance(msg_data.media, dict):
            msg_data.media = MediaContentForMsgDataType(**msg_data.media)
        return msg_data