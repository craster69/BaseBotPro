from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update

from typing import Callable, Dict, Any, Awaitable

from panel.models import Users

from bot.base_enums import LanguageEnum
from bot.utils.message_manager import MessageManager
from bot.utils.base_utils import get_enums, logger

from asgiref.sync import sync_to_async


class LoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        event = update.message or update.callback_query
        logger.info(
            f'[ ID: {event.from_user.id} | USERNAME: @{event.from_user.username} ] -> '
            f'[ {await self._event_type(event)} ] -> '
            f'[ {str(event.text)[:40] if update.message else event.data} ]'
        )
        return await handler(update, data)


    async def _event_type(self, event: Message | CallbackQuery) -> str:
        return {Message: 'MESSAGE', CallbackQuery: 'CALLBACK'}[type(event)]


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        event = update.message or update.callback_query
        self.tg_id, self.name, self.language_code = event.from_user.id, event.from_user.username, event.from_user.language_code
        self.user: Users | None = await Users.objects.filter(tg_id=self.tg_id).afirst()
        if not self.user:
            data['user'] = await self._create_user()
            logger.success(f'[ ID: {self.tg_id} | USERNAME: @{self.name} ] -> [ REGISTERED ]')
        else:
            data['user'] = await self._update_username()
        return await handler(update, data)

    @sync_to_async
    def _update_username(self) -> Users:
        if self.user.name != self.name:
            self.user.name = self.name
            self.user.save(update_fields=['name'])
        return self.user

    @sync_to_async
    def _create_user(self) -> Users:
        return Users.objects.create(
            tg_id=self.tg_id,
            name=self.name,
            language_code=self.language_code if self.language_code in get_enums(LanguageEnum) else LanguageEnum.EN.value
        )


class MessageManagerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: Dict[str, Any]
    ) -> Any:
        event = update.message or update.callback_query
        state, user = data.get('state'), data.get('user')
        if not data.get('mn'):
            message_manager = MessageManager(
                event, 
                state, 
                user.language_code
            )
            data['mn'] = message_manager
        
        return await handler(update, data)


middlewares: list[BaseMiddleware] = [
    LoggerMiddleware(),
    AuthMiddleware(),
    MessageManagerMiddleware()
]