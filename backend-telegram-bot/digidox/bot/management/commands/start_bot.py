from django.core.management.base import BaseCommand
from django.conf import settings
from bot.main import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.polling()
