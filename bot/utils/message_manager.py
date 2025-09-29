from aiogram.types import (
    Message,
    CallbackQuery,
    InputMediaPhoto, 
    InputMediaVideo
)
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.config import bot
from bot.type_defs.base_types import MessageDataType, MediaContentForMsgDataType
from bot.utils.base_utils import build_keyboard, get_text, validate_message
from bot.routers.main.texts import MainMenuTexts
from bot.routers.main.keyboards import MainMenuKb

from dataclasses import asdict


class MessageManager:
    def __init__(
        self,
        event: Message | CallbackQuery, 
        state: FSMContext,
        language_code: str
    ) -> None:
        self.event = event
        self.state = state
        self.language_code = language_code
        self.main_menu_texts = MainMenuTexts(language_code)
        self.main_menu_kb = MainMenuKb()


    async def send_message(self, msg_data: MessageDataType) -> None:
        if isinstance(self.event, CallbackQuery):
            await self.event.answer('')
            self.event = self.event.message

        self.msg_result = await self._generate_msg_result(msg_data)


    async def edit_message(self, msg_data: MessageDataType) -> None:
        message_id: int = (await self.state.get_data()).get('message_id')
        try:
            self.msg_result = await self._generate_msg_result(msg_data)
        except TelegramBadRequest as _ex:
            if 'message is not modified' in str(_ex):
                await self.event.answer('')
                self.msg_result = self.event.message
            else:
                if isinstance(self.event, Message):
                    await self.event.delete()
                await self._msg_delete(message_id)
                await self.send_message(msg_data, False)


    async def _msg_delete(self, message_id: int) -> None:
        chat_id = self.event.message.chat.id if isinstance(self.event, CallbackQuery) else self.event.chat.id
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass


    async def _generate_msg_result(self, msg_data: MessageDataType) -> Message:
        keyboard = None
        if msg_data.keyboard:
            keyboard = build_keyboard(msg_data.keyboard, self.language_code)
        return await {
            msg_data.media.photo: {
                Message: lambda: self.event.answer_photo(photo=msg_data.media.photo, caption=msg_data.text, reply_markup=keyboard),
                CallbackQuery: lambda: self.event.message.edit_media(media=InputMediaPhoto(media=msg_data.media.photo, caption=msg_data.text), reply_markup=keyboard)
            },
            msg_data.media.video: {
                Message: lambda: self.event.answer_video(video=msg_data.media.video, caption=msg_data.text, reply_markup=keyboard),
                CallbackQuery: lambda: self.event.message.edit_media(media=InputMediaVideo(media=msg_data.video, caption=msg_data.text), reply_markup=keyboard)
            },
            None: {
                Message: lambda: self.event.answer(text=msg_data.text, reply_markup=keyboard),
                CallbackQuery: lambda: self.event.message.edit_text(text=msg_data.text, reply_markup=keyboard)
            }
        }[self._select_content_key(msg_data.media)][type(self.event)]()


    def _select_content_key(self, media_content: MediaContentForMsgDataType | None) -> any:
        media_values = [el for el in asdict(media_content).values() if el]
        return media_values[0] if media_values else None
    