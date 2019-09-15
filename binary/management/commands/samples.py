import uuid
import json
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.urls import reverse

from apps.pagsim.models import Charges
from apps.binary.models import BinaryTree
from apps.binary.choices import POSITION_CHOICES
from apps.financial.models import Plans
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create samples for users'

    def handle(self, *args, **options):
        with transaction.atomic():
            sponsor = User.objects.first()
            sponsor.status = 'active'
            sponsor.wallet = '3KRGxJLyFH7mLJG3yvwymADnDoDFzfJ73D'
            sponsor.save()
            
            plan = Plans.objects.first()
            expiry_date = datetime.now() + timedelta(days=settings.PAGSIM_EXPIRY_DAYS)

            c = Charges()
            c.amount = plan.down
            c.expiry_date = expiry_date
            c.description = "{} PLAN PAYMENT BY {}".format(plan.name, sponsor.username)
            c.identifier = uuid.uuid4().hex
            c.return_url = 'http://localhost:8000{}'.format(reverse('financial-payment-received'))
            c.plan = plan
            c.user = sponsor
            c.request = json.dumps([1, 2, 3])
            c.response = json.dumps([1, 2, 3])
            c.wallet = '3KRGxJLyFH7mLJG3yvwymADnDoDFzfJ73D'
            c.transaction_status = 1
            c.status = 1
            c.save()

            for i in range(0, 500):
                user = User()
                user.first_name = 'Demo'
                user.last_name = i
                user.username = 'demo{}'.format(i)
                user.sponsor = sponsor
                user.set_password('123456')
                user.email = 'demo{}@example.com'.format(i)
                user.status = 'active'
                user.save()

                c = Charges()
                c.amount = plan.down
                c.expiry_date = expiry_date
                c.description = "{} PLAN PAYMENT BY {}".format(plan.name, user.username)
                c.identifier = uuid.uuid4().hex
                c.return_url = 'http://localhost:8000{}'.format(reverse('financial-payment-received'))
                c.plan = plan
                c.user = user
                c.request = json.dumps([1, 2, 3])
                c.response = json.dumps([1, 2, 3])
                c.wallet = '3KRGxJLyFH7mLJG3yvwymADnDoDFzfJ73D'
                c.transaction_status = 1
                c.status = 1
                c.save()

                print("Creating user Demo {}".format(i))