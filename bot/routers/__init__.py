from aiogram import Router

from .main.handlers import router as main_router



routers: list[Router] = [
    main_router
]

__all__ = ['routers']