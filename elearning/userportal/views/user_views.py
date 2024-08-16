from ..models import *
from ..forms import *
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings


class UserDetailView(DetailView):
    models = PortalUser
    template_name = "userportal/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    login_url = "login"

    def get_object(self):
        username = self.kwargs.get("username")
        return get_object_or_404(PortalUser, username=username)


class UserListView(ListView):
    model = PortalUser
    paginate_by = settings.PAGINATION_PAGE_SIZE
    template_name = "userportal/user_list.html"
    context_object_name = "users"
    login_url = "login"

    def get_queryset(self):
        queryset = PortalUser.objects.filter(is_staff=False, is_superuser=False).only(
            "id", "username", "user_type"
        )
        keywords = self.request.GET.get("keywords")
        user_types = self.request.GET.getlist("user_type")
        if keywords:
            query_words = keywords.split()
            q_objects = Q()
            for word in query_words:
                q_objects |= (
                    Q(username__icontains=word)
                    | Q(first_name__icontains=word)
                    | Q(last_name__icontains=word)
                    | Q(title__icontains=word)
                )
            queryset = queryset.filter(q_objects)
        if user_types:
            queryset = queryset.filter(user_type__in=user_types)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET or None)
        return context
