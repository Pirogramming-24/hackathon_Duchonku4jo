from django.shortcuts import render, redirect, get_object_or_404
from .models import Week
from .forms import WeekForm

def weeks_list(request):
    weeks = Week.objects.order_by("week_no")

    return render(request, "weeks/main.html", {
        "weeks": weeks
    })

def week_create(request):
    last_week = Week.objects.order_by("-week_no").first()
    next_week_no = last_week.week_no + 1 if last_week else 1

    if request.method == "POST":
        form = WeekForm(request.POST, next_week_no=next_week_no)
        if form.is_valid():
            week = form.save(commit=False)
            week.week_no = next_week_no
            week.save()
            return redirect("weeks:weeks_list")
    else:
        form = WeekForm(next_week_no=next_week_no)

    return render(request, "weeks/form.html", {"form": form, "next_week_no": next_week_no})

def week_delete(request, pk):
    week = get_object_or_404(Week, pk=pk)

    if request.method == "POST":
        week.delete()

    return redirect("weeks:weeks_list")