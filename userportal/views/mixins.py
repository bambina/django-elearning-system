class QueryParamsMixin:
    """Mixin to add query params to context"""

    def get_context_data(self, **kwargs):
        """Add query params to context"""
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        if "page" in query_params:
            del query_params["page"]
        context["query_params"] = query_params.urlencode()
        return context
