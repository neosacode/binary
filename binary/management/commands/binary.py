from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.binary.choices import POSITION_CHOICES
from apps.binary.models import BinaryTree, Report
from apps.pagsim.models import Charges
from apps.users.models import User
from apps.financial.models import Statement
from apps.core.bonus import inactive_user


class Command(BaseCommand):
    help = 'Calculate the binary bonus for active users'

    def handle(self, *args, **options):
        with transaction.atomic():
            users = User.objects.filter(status=User.STATUS.active).order_by('created')

            for user in users:
                bt = BinaryTree.objects.get(user=user)
                lower_side_value = min([bt.left_value, bt.right_value])

                l_bt = BinaryTree.objects.filter(parent__user=user, position=POSITION_CHOICES.L)
                r_bt = BinaryTree.objects.filter(parent__user=user, position=POSITION_CHOICES.R)

                if not l_bt.exists() or not r_bt.exists() or lower_side_value <= Decimal('0.00'):
                    print('Skipping user {}'.format(user.username))
                    continue

                charge = Charges.objects.get(user=user, transaction_status=1, status=1)

                # Value to receive
                value = round(lower_side_value * (charge.plan.binary / 100), 8)

                # Inactive user if the plan limit has been achived
                value = inactive_user(charge, value)

                if value <= Decimal('0.00'):
                    continue

                statement = Statement()
                statement.user = user
                statement.value = value
                statement.charge = charge
                statement.description = 'Binary Bonus'
                statement.save()

                report = Report()
                report.left_value = bt.left_value
                report.right_value = bt.right_value
                report.statement = statement

                if lower_side_value == bt.left_value:
                    report.lower_side = POSITION_CHOICES.L
                if lower_side_value == bt.right_value:
                    report.lower_side = POSITION_CHOICES.R

                report.save()

                print('Paying {} to {} of binary bonus'.format(value, user.username))