from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from apps.pagsim.models import Charges
from apps.binary.models import BinaryTree
from apps.binary.choices import POSITION_CHOICES
from apps.users.models import User


class Command(BaseCommand):
    help = 'Positionate users in Binary Tree'

    def handle(self, *args, **options):
        with transaction.atomic():
            users = User.objects.filter(is_superuser=False).order_by('created')
            binary_exists = bool(BinaryTree.objects.first())

            for user in users:
                charge = user.active_charge

                if binary_exists:
                    has_position = BinaryTree.objects.filter(user=user).exists()

                    if has_position:
                        continue

                    sponsor_position = BinaryTree.objects.get(user=user.sponsor)
                    next_position = BinaryTree.objects.get(pk=sponsor_position.next_position)
                    side = POSITION_CHOICES.L

                    if next_position.children.count() == 1:
                        if next_position.children.first().position == POSITION_CHOICES.L:
                            side = POSITION_CHOICES.R

                    bt = BinaryTree()
                    bt.parent = next_position
                    bt.position = side
                    bt.user = user
                    bt.value = Decimal('0.00')

                    if charge:
                        bt.value = charge.plan.binary_points

                    bt.save()

                    print("Positioning user {} in Binary Tree".format(user.username))
                else:
                    bt = BinaryTree()
                    bt.user = user
                    bt.value = Decimal('0.00')

                    if charge:
                        bt.value = charge.plan.binary_points
                    
                    bt.save()
                    binary_exists = True

                    print("Positioning user {} as root of Binary Tree".format(user.username))
                
                
