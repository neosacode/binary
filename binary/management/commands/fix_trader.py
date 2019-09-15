from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import User


class Command(BaseCommand):
    help = 'Calculate the binary bonus for active users'

    def handle(self, *args, **options):
        with transaction.atomic():
            users = User.objects.filter(status=User.STATUS.active).order_by('created')

            for user in users:
                charge = user.active_charge

                if not charge:
                    print(user.username)