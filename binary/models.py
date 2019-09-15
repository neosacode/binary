from collections import Counter, OrderedDict
import uuid
from decimal import Decimal

from django.db import models
from django.db import connection
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .choices import POSITION_CHOICES
from .utils import dictfetchall
from .exceptions import TreeUniqueOwner, NodeMustHaveParent


GET_TREE_FAMILY_RAW_QUERY = """
    WITH RECURSIVE tree AS (
        SELECT 
            0 as level,
            binary_binarytree.id,
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            WHERE binary_binarytree.user_id = '{user_id}'::uuid

        UNION ALL

        SELECT 
            tree.level + 1,
            binary_binarytree.id, 
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            INNER JOIN tree ON tree.id = binary_binarytree.parent_id
    )
    SELECT * FROM tree
    ORDER BY 
    tree.level,
    tree.position;
"""

SEARCH_USER_IN_TREE_RAW_QUERY = """
    WITH RECURSIVE tree AS (
        SELECT 
            0 as level,
            binary_binarytree.id,
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            WHERE binary_binarytree.user_id = '{user_id}'::uuid

        UNION ALL

        SELECT 
            tree.level + 1,
            binary_binarytree.id, 
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            INNER JOIN tree ON tree.id = binary_binarytree.parent_id
    )
    SELECT * FROM tree
    WHERE tree.user_id = '{search_user_id}'::UUID
    ORDER BY 
    tree.level,
    tree.position;
"""

BINARY_value_IN_TREE_RAW_QUERY = """
    WITH RECURSIVE tree AS (
        SELECT 
            0 as level,
            binary_binarytree.id,
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            WHERE binary_binarytree.user_id = '{user_id}'::uuid

        UNION ALL

        SELECT 
            tree.level + 1,
            binary_binarytree.id, 
            binary_binarytree.parent_id,
            binary_binarytree.user_id,
            binary_binarytree.position,
            binary_binarytree.value
        FROM binary_binarytree
            INNER JOIN tree ON tree.id = binary_binarytree.parent_id
    )
    SELECT sum(tree.value) "value" FROM tree WHERE tree.level <= {depth};
"""


class Report(TimeStampedModel, models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    statement = models.ForeignKey(
        'exchange_core.Statement',
        related_name='binary_report',
        on_delete=models.DO_NOTHING
    )
    left_value = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0.00')
    )
    right_value = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0.00')
    )
    lower_side = models.CharField(
        max_length=1,
        choices=POSITION_CHOICES,
        default=POSITION_CHOICES.L
    )

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")


class BinaryTree(TimeStampedModel, models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.DO_NOTHING
    )
    position = models.CharField(
        max_length=1,
        choices=POSITION_CHOICES,
        default=POSITION_CHOICES.O
    )
    value = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        default=Decimal('0.00')
    )
    user = models.ForeignKey('exchange_core.Users', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (("parent", "position"),)
        verbose_name = _("Binary tree")
        verbose_name_plural = _("Binary tree")

    @property
    def left_value(self):
        node = BinaryTree.objects.filter(parent__pk=self.pk, position=POSITION_CHOICES.L)

        if not node.exists():
            return Decimal('0.00')
        
        l_sum = Report.objects.filter(lower_side=POSITION_CHOICES.L, statement__user=self.user).aggregate(discount=Sum('left_value'))['discount'] or Decimal('0.00')
        r_sum = Report.objects.filter(lower_side=POSITION_CHOICES.R, statement__user=self.user).aggregate(discount=Sum('right_value'))['discount'] or Decimal('0.00')
        discount_value = l_sum + r_sum
        
        node = node.first()

        with connection.cursor() as cursor:
            cursor.execute(BINARY_value_IN_TREE_RAW_QUERY.format(user_id=node.user.pk, depth=5))
            rows = dictfetchall(cursor)
            return rows[0]['value'] - discount_value

    @property
    def right_value(self):
        node = BinaryTree.objects.filter(parent__pk=self.pk, position=POSITION_CHOICES.R)

        if not node.exists():
            return Decimal('0.00')

        l_sum = Report.objects.filter(lower_side=POSITION_CHOICES.L, statement__user=self.user).aggregate(discount=Sum('left_value'))['discount'] or Decimal('0.00')
        r_sum = Report.objects.filter(lower_side=POSITION_CHOICES.R, statement__user=self.user).aggregate(discount=Sum('right_value'))['discount'] or Decimal('0.00')
        discount_value = l_sum + r_sum

        node = node.first()

        with connection.cursor() as cursor:
            cursor.execute(BINARY_value_IN_TREE_RAW_QUERY.format(user_id=node.user.pk, depth=5))
            rows = dictfetchall(cursor)
            return rows[0]['value'] - discount_value


    @property
    def total_left_value(self):
        node = BinaryTree.objects.filter(parent__pk=self.pk, position=POSITION_CHOICES.L)

        if not node.exists():
            return Decimal('0.00')

        node = node.first()

        with connection.cursor() as cursor:
            cursor.execute(BINARY_value_IN_TREE_RAW_QUERY.format(user_id=node.user.pk, depth=5))
            rows = dictfetchall(cursor)
            return rows[0]['value']

    @property
    def lower_side_value(self):
        if self.total_left_value > self.total_right_value:
            lower_side_value = self.total_right_value
        else:
            lower_side_value = self.total_left_value
        return lower_side_value


    @property
    def total_right_value(self):
        node = BinaryTree.objects.filter(parent__pk=self.pk, position=POSITION_CHOICES.R)

        if not node.exists():
            return Decimal('0.00')

        node = node.first()

        with connection.cursor() as cursor:
            cursor.execute(BINARY_value_IN_TREE_RAW_QUERY.format(user_id=node.user.pk, depth=5))
            rows = dictfetchall(cursor)
            return rows[0]['value']


    @property
    def family(self):
        with connection.cursor() as cursor:
            cursor.execute(GET_TREE_FAMILY_RAW_QUERY.format(user_id=self.user.pk))
            family = dictfetchall(cursor)

        return family

    @property
    def descendants(self):
        return self.family[1:]

    @property
    def next_position(self):
        if self.children.count() < 2:
            return self.pk
        
        level = self.get_level()

        if not level:
            level = self.descendants[-1]['level']
            descendants = self.get_nodes(level)
            return descendants[0].get('id')
        
        return self.get_position(level)

    def has_children(self):
        return len(self.family) > 1

    def get_level(self):
        descendants = Counter(node.get('level') for node in self.descendants)
        descendants = OrderedDict(sorted(descendants.items()))

        for level, qty in descendants.items():
            if not qty == (2 ** level):
                return level

    def get_position(self, level):
        for descendant in self.descendants:
            if descendant.get('level') != (level - 1):
                continue

            parent = BinaryTree.objects.get(id=descendant.get('id'))

            if parent.children.count() < 2:
                return parent.id

    def get_nodes(self, level):
        return [children for children in self.descendants 
                if children.get('level') == level]

    def node_exists(self, search_user):
        with connection.cursor() as cursor:
            cursor.execute(SEARCH_USER_IN_TREE_RAW_QUERY.format(user_id=self.user.pk, search_user_id=search_user.pk))
            if len(dictfetchall(cursor)) > 0:
                return True

        return False

    def save(self, *args, **kwargs):
        owner = BinaryTree.objects.filter(position=POSITION_CHOICES.O)

        if self.position != POSITION_CHOICES.O and not self.parent:
            raise NodeMustHaveParent()

        if self.position == POSITION_CHOICES.O and owner:
            raise TreeUniqueOwner()

        super().save(*args, **kwargs)
