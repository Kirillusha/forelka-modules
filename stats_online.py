# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class StatusLoggerModule(loader.Module):
    strings = {
        "name": "StatusLoggerModule",
        "user_not_found": "Пользователь не найден.",
        "status_logged": "Статус пользователя зафиксирован.",
        "activity_chart": "График активности пользователя:\n"
    }

    def __init__(self):
        self.config = loader.ModuleConfig()
        self.statuses = {}  # Словарь для хранения статусов пользователей

    async def log_status(self, user_id: int, is_online: bool):
        """Логирует статус пользователя."""
        if user_id not in self.statuses:
            self.statuses[user_id] = []
        current_time = datetime.now()
        self.statuses[user_id].append((current_time, is_online))
        logger.info(f"Logged status for user {user_id}: {'online' if is_online else 'offline'}")

    async def get_activity_chart(self, user_id: int):
        """Генерирует график активности пользователя."""
        if user_id not in self.statuses:
            return None

        times = []
        online_status = []

        for timestamp, status in self.statuses[user_id]:
            times.append(timestamp)
            online_status.append(1 if status else 0)

        plt.figure(figsize=(10, 5))
        plt.plot(times, online_status, marker='o')
        plt.title(f"Статус активности пользователя {user_id}")
        plt.xlabel("Время")
        plt.ylabel("Статус (1 = онлайн, 0 = оффлайн)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_file = f"activity_chart_{user_id}.png"
        plt.savefig(chart_file)
        plt.close()
        return chart_file

    @loader.command
    async def trackstatus(self, message: Message):
        """Фиксирует статус выбранного юзера.

        Использование:
        .trackstatus @username
        """
        user = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if user:
            user_id = utils.get_user_id(user)  # Допустим, это функция для получения ID

            if user_id:
                # В данном случае, используется код для получения онлайн-статуса
                is_online = await utils.get_user_status(user_id)
                await self.log_status(user_id, is_online)
                await message.respond(self.strings["status_logged"])
            else:
                await message.respond(self.strings["user_not_found"])
        else:
            await message.respond("Пожалуйста, укажите имя пользователя.")

    @loader.command
    async def activitychart(self, message: Message):
        """Показывает график активности пользователя.

        Использование:
        .activitychart @username
        """
        user = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if user:
            user_id = utils.get_user_id(user)

            if user_id:
                chart_file = await self.get_activity_chart(user_id)
                if chart_file:
