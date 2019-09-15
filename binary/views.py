from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from apps.users.models import User

from .models import BinaryTree
from .choices import POSITION_CHOICES


@method_decorator(login_required, name='dispatch')
class TreeView(TemplateView):
    template_name = 'binary/tree.html'

    def get(self, request):
        default_node = BinaryTree.objects.filter(user=request.user) 
        BT_0 = self.search_node(request, default_node)

        BT_1_1 = self.get_position(BT_0, POSITION_CHOICES.L)
        BT_1_2 = self.get_position(BT_0, POSITION_CHOICES.R)

        BT_2_1 = self.get_position(BT_1_1, POSITION_CHOICES.L)
        BT_2_2 = self.get_position(BT_1_1, POSITION_CHOICES.R)
        BT_2_3 = self.get_position(BT_1_2, POSITION_CHOICES.L)
        BT_2_4 = self.get_position(BT_1_2, POSITION_CHOICES.R)

        BT_3_1 = self.get_position(BT_2_1, POSITION_CHOICES.L)
        BT_3_2 = self.get_position(BT_2_1, POSITION_CHOICES.R)
        BT_3_3 = self.get_position(BT_2_2, POSITION_CHOICES.L)
        BT_3_4 = self.get_position(BT_2_2, POSITION_CHOICES.R)
        BT_3_5 = self.get_position(BT_2_3, POSITION_CHOICES.L)
        BT_3_6 = self.get_position(BT_2_3, POSITION_CHOICES.R)
        BT_3_7 = self.get_position(BT_2_4, POSITION_CHOICES.L)
        BT_3_8 = self.get_position(BT_2_4, POSITION_CHOICES.R)

        data = {
            'BT_0': BT_0,
            'BT_1_1': BT_1_1,
            'BT_1_2': BT_1_2,
            'BT_2_1': BT_2_1,
            'BT_2_2': BT_2_2,
            'BT_2_3': BT_2_3,
            'BT_2_4': BT_2_4,
            'BT_3_1': BT_3_1,
            'BT_3_2': BT_3_2,
            'BT_3_3': BT_3_3,
            'BT_3_4': BT_3_4,
            'BT_3_5': BT_3_5,
            'BT_3_6': BT_3_6,
            'BT_3_7': BT_3_7,
            'BT_3_8': BT_3_8,
            'page_title': _('Binary Tree')
        }

        return render(request, self.template_name, data)

    def search_node(self, request, default_node):
        search_user = request.GET.get('search_user', '').strip()
        users = User.objects.filter(username=search_user)

        if search_user and default_node.exists() and users.exists():
            user = users.first()

            if default_node.first().node_exists(user):
                return BinaryTree.objects.filter(user=user)

        return default_node


    def get_position(self, parent, side):
        if parent and parent.exists():
            return BinaryTree.objects.filter(parent=parent.first(), position=side)


@method_decorator(login_required, name='dispatch')
class ChangeOutpouringSideView(TemplateView):
    def get(self, request):
        side = request.GET.get('side')

        if side and side in ['left', 'right', 'auto']:
            user = request.user
            user.outpouring_side = side
            user.save()

            messages.success(request, _("Outpouring side successfully changed!"))

        return redirect(reverse('binary-tree'))


@method_decorator(login_required, name='dispatch')
class SearchNodeView(TemplateView):
    def post(self, request):
        username = request.POST.get('s')

        try:
            user = User.objects.get(username=username)
            return redirect(reverse('binary-tree') + '?search_user=' + user.username)
        except:
            return redirect(reverse('binary-tree'))