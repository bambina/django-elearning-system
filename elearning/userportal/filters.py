from django_filters import FilterSet, CharFilter, NumberFilter
from django.contrib.auth import get_user_model


class UserFilter(FilterSet):
    username = CharFilter(lookup_expr="icontains")
    user_type = NumberFilter()

    class Meta:
        model = get_user_model()
        fields = ["username", "user_type"]
