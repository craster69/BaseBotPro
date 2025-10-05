from typing import Type, List

from enum import Enum

import json

from bot.type_defs.base_types import (
    KbDataType, 
    MessageDataType,
    BTNDataType
)
from bot.utils.cache_redis_message import CacheRedisMessage
from aiogram.types import InlineKeyboardButton as IB
from aiogram.types import InlineKeyboardMarkup as IM
from aiogram.types import InlineKeyboardMarkup as IKM
from aiogram.utils.keyboard import InlineKeyboardBuilder as BD

import sys

from loguru import logger

from os.path import abspath, dirname, join
import os

from panel.models import Users

import inspect

from django.core.paginator import Paginator, Page

from asgiref.sync import sync_to_async

import asyncio

from pathlib import Path


def get_format_number(number: float) -> str:
    integer_part = int(number)
    fractional_part = round(number - integer_part, 6)

    integer_str = f"{integer_part:,}".replace(",", " ")

    if fractional_part == 0:
        return integer_str

    fractional_str = f"{fractional_part:.6f}".split('.')[1].rstrip('0')
    
    if fractional_str == '':
        return integer_str

    return f"{integer_str},{fractional_str}"


def get_enums(_enums: Type[Enum]) -> List[str]:
    return [enum.value for enum in _enums]


def get_text(catalog: str, key: str, language_code: str, args: dict[str, any] = None, kb: bool = False) -> str:
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    file_path = PROJECT_ROOT / 'bot' / 'texts' / language_code / f'{catalog}_texts.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    type_text = 'message'
    
    if kb:
        type_text = 'kb'
    
    return data[type_text][key].format(**args) if args else data[type_text][key]


def get_languages() -> list[str]:
    """
    Возвращает список названий папок (языков), в которых есть хотя бы один .json файл.
    Пример: ['en', 'ru']
    """
    texts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'bot', 'texts')

    if not os.path.exists(texts_dir):
        return []

    languages = []
    for item in os.listdir(texts_dir):
        item_path = os.path.join(texts_dir, item)
        if os.path.isdir(item_path):
            # Проверяем, есть ли хотя бы один .json файл в папке
            has_json = any(f.endswith('.json') for f in os.listdir(item_path))
            if has_json:
                languages.append(item)

    return sorted(languages)


def build_keyboard(kb_data: KbDataType, language_code: str) -> IM:
    kb = BD()
    if kb_data.buttons:
        for button_row in kb_data.buttons:
            compile_row: list[IB] = []
            for btn in button_row:
                if isinstance(btn, BTNDataType):
                    compile_row.append(
                        IB(
                            text=get_text(btn.catalog, btn.key, language_code, btn.args, True),
                            callback_data=btn.callback
                        )
                    )
                else:
                    compile_row.append(btn)
            kb.row(*compile_row)

    if language_code and kb_data.back_callback:
        kb.row(
            IB(
                text=get_text(
                    'utils',
                    'back',
                    language_code,
                    kb=True
                ), 
                callback_data=kb_data.back_callback
            )
        )

    if language_code and kb_data.back_to_main_menu:
        kb.row(
            IB(
                text=get_text(
                    'utils',
                    'back_to_main_menu',
                    language_code,
                    kb=True
                ),
                callback_data='back_to_main_menu'
            )
        )

    return kb.as_markup()


def logging_setup():
    logger.remove()
    
    log_filename = "{time:DD-MM-YYYY}.log"
    log_folder = 'logs'
    log_directory = join(dirname(dirname(abspath(__file__))), log_folder)
    format_logs = (
        f"<magenta>{{time:DD-MM-YY HH:mm:ss}}</magenta> | "
        "<blue>{level}</blue> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
        "<level>{message}</level>"
    )
    logger.add(join(log_directory, log_filename), format=format_logs, rotation="00:00", compression="zip")
    logger.add(sys.stdout, colorize=True, format=format_logs, level="DEBUG")


def validate_message(func) -> any:
    async def wrapper(self, msg_data: MessageDataType, save: bool = True):
        if not msg_data.catalog:
            stack = inspect.stack()
            filename = stack[1].filename
            msg_data.catalog = '_'.join(filename.split('\\')[-1].split('_')[:-1])
        await func(self, CacheRedisMessage.unpack(msg_data), save)
        if self.msg_result:
            message_id, send_time = self.msg_result.message_id, self.msg_result.date.timestamp()
            await self.state.update_data(message_id=message_id, send_time=send_time)
        if save:
            self.user = await Users.objects.filter(tg_id=self.user.tg_id).afirst()
            await self.state.update_data(last_msg=CacheRedisMessage.pack(msg_data))
        return
    return wrapper


def chunked(lst: list[any], n: int) -> list[list[any]]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def get_data_pagination(queryset, page: int, page_size: int) -> tuple[Paginator, Page]:
    """
    Универсальная пагинация для любого QuerySet.
    """
    paginator = Paginator(queryset, page_size)

    current_page = paginator.page(page)
    
    return paginator, current_page


def get_pagination_kb(buttons: list[list[IB]], catalog: str, paginator: Paginator, current_page: Page):
    
    if paginator.num_pages > 1:
        left_btn = IB(text='◀️', callback_data=f'{catalog}_page_{current_page.number-1 if current_page.has_previous() else paginator.num_pages}')
        middle_btn = IB(text=f'{current_page.number}', callback_data=f'current_page_{current_page.number}')
        right_btn = IB(text='▶️', callback_data=f'{catalog}_page_{current_page.number+1 if current_page.has_next() else 1}')

        buttons.append([left_btn, middle_btn, right_btn])

    return buttons


def get_text_from_txt(path: str) -> str:
    with open(path, 'r') as file:
        text = '\n'.join([line.replace('\n', '') for line in file.readlines()])
        return text