from aiogram import Router, F
from aiogram.filters.command import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.type_defs.base_types import MessageDataType
from bot.utils.message_manager import MessageManager

from panel.models import Users

from asgiref.sync import sync_to_async


router = Router()


@router.callback_query(F.data == 'back_to_main_menu')
@router.message(Command(commands=['start', 'help']))
async def start_help(event: Message | CallbackQuery, mn: MessageManager, state: FSMContext):
    await state.clear()
    msg_send_type = {Message: mn.send_message, CallbackQuery: mn.edit_message}
    await msg_send_type[type(event)](
        MessageDataType(
            mn.main_menu_texts.get_start_menu_text(),
            mn.main_menu_kb.main_menu_kb()
        )
    )
0

@router.callback_query(F.data == 'choose_language')
@router.message(Command(commands=['choose_language']))
async def choose_language(event: Message | CallbackQuery, mn: MessageManager):
    msg_send_type = {Message: mn.send_message, CallbackQuery: mn.edit_message}
    await msg_send_type[type(event)](
        MessageDataType(
            mn.main_menu_texts.get_choose_language_text(),
            mn.main_menu_kb.choose_language_kb()
        )
    )


@router.callback_query(F.data.startswith('choose_language_'))
async def choose_language_query(event: CallbackQuery, state: FSMContext, user: Users, mn: MessageManager):
    user.language_code = event.data.split('_')[-1]
    await sync_to_async(user.save)(update_fields=['language_code'])
    mn = MessageManager(
        event, 
        state, 
        user.language_code
    )
    return await start_help(event, mn, state)