from companies.models import Company


def company_context(request):
    if not request.user.is_authenticated or request.user.is_staff:
        return {"current_company": None}
    return {
        "current_company": Company.objects.filter(created_by=request.user).order_by("-created_at").first(),
    }
