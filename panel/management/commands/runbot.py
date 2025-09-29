from django.core.management.base import BaseCommand

from bot.main import main as run_bot

import asyncio

class Command(BaseCommand):
    def handle(self, *args, **options):
        asyncio.run(run_bot())