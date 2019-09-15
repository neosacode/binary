from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.users.models import User
from apps.financial.models import Statement
from apps.core.bonus import inactive_user


class Command(BaseCommand):
    help = 'Calculate the binary bonus for active users'

    def handle(self, *args, **options):
        with transaction.atomic():
            users = User.objects.filter(status=User.STATUS.active).order_by('created')

            for user in users:
                charge = user.active_charge

                description = 'Trader Bonus'
                st = Statement.objects.filter(user=user, description=description, created__date=timezone.now())

                if st.exists():
                    continue

                value = round(charge.plan.down * (charge.plan.daily_income / 100), 8)
                
                # Inactive user if the plan limit has been achived
                pay_value = inactive_user(charge, value)

                if pay_value <= Decimal('0.00'):
                    continue

                statement = Statement()
                statement.description = description
                statement.value = pay_value
                statement.user = user
                statement.charge = charge
                statement.save()

                print('Paying {} of trader bonus to {}'.format(pay_value, user.username))
