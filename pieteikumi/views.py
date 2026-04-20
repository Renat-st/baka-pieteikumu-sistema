from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Pieteikums, Statuss, Workflow, PieteikumaTips


@login_required
def pieteikumu_saraksts(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    if request.user.is_staff:
        qs = Pieteikums.objects.all()
    else:
        qs = Pieteikums.objects.filter(
            Q(lietotajs=request.user) | Q(assigned_to=request.user)
        ).distinct()

    if q:
        qs = qs.filter(
            Q(nosaukums__icontains=q) |
            Q(apraksts__icontains=q)
        )

    if status:
        qs = qs.filter(statuss__nosaukums=status)

    qs = qs.order_by('-id')

    all_visible = Pieteikums.objects.all() if request.user.is_staff else Pieteikums.objects.filter(
        Q(lietotajs=request.user) | Q(assigned_to=request.user)
    ).distinct()

    total_count = all_visible.count()
    new_count = all_visible.filter(statuss__nosaukums='Jauns').count()
    in_progress_count = all_visible.filter(statuss__nosaukums='Procesā').count()
    done_count = all_visible.filter(statuss__nosaukums='Pabeigts').count()

    stats_by_type = all_visible.values('tips__nosaukums').annotate(total=Count('id')).order_by('-total')
    stats_by_assigned = all_visible.values('assigned_to__username').annotate(total=Count('id')).order_by('-total')

    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pieteikumi': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'statusi': Statuss.objects.all(),
        'total_count': total_count,
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'stats_by_type': stats_by_type,
        'stats_by_assigned': stats_by_assigned,
    }
    return render(request, 'pieteikumi/saraksts.html', context)


@login_required
def jauns(request):
    if request.method == 'POST':
        status_obj = get_object_or_404(Statuss, id=request.POST['statuss'])
        tips_obj = get_object_or_404(PieteikumaTips, id=request.POST['tips'])

        assigned_user = None
        if request.user.is_staff:
            assigned_id = request.POST.get('assigned_to')
            if assigned_id:
                assigned_user = get_object_or_404(User, id=assigned_id)

        Pieteikums.objects.create(
            nosaukums=request.POST['nosaukums'],
            apraksts=request.POST['apraksts'],
            statuss=status_obj,
            lietotajs=request.user,
            assigned_to=assigned_user,
            tips=tips_obj
        )
        return redirect('/')

    return render(request, 'pieteikumi/form.html', {
        'title': 'Jauns pieteikums',
        'statusi': Statuss.objects.all(),
        'tipsi': PieteikumaTips.objects.all(),
        'users': User.objects.all(),
    })


@login_required
def rediget(request, id):
    pieteikums = get_object_or_404(Pieteikums, id=id)

    if pieteikums.lietotajs != request.user and not request.user.is_staff and pieteikums.assigned_to != request.user:
        return HttpResponse("Nav atļauts", status=403)

    if request.method == 'POST':
        jaunais_statuss = get_object_or_404(Statuss, id=request.POST['statuss'])
        jaunais_tips = get_object_or_404(PieteikumaTips, id=request.POST['tips'])

        allowed = Workflow.objects.filter(
            pieteikuma_tips=jaunais_tips,
            start_statuss=pieteikums.statuss,
            end_statuss=jaunais_statuss
        ).exists()

        if pieteikums.statuss != jaunais_statuss and not allowed:
            return HttpResponse("Nederīga statusa maiņa", status=400)

        pieteikums.nosaukums = request.POST['nosaukums']
        pieteikums.apraksts = request.POST['apraksts']
        pieteikums.statuss = jaunais_statuss
        pieteikums.tips = jaunais_tips

        if request.user.is_staff:
            assigned_id = request.POST.get('assigned_to')
            if assigned_id:
                pieteikums.assigned_to = get_object_or_404(User, id=assigned_id)
            else:
                pieteikums.assigned_to = None

        pieteikums.save()
        return redirect('/')

    return render(request, 'pieteikumi/form.html', {
        'title': 'Rediģēt pieteikumu',
        'pieteikums': pieteikums,
        'statusi': Statuss.objects.all(),
        'tipsi': PieteikumaTips.objects.all(),
        'users': User.objects.all(),
    })


@login_required
def dzest(request, id):
    pieteikums = get_object_or_404(Pieteikums, id=id)

    if pieteikums.lietotajs != request.user and not request.user.is_staff:
        return HttpResponse("Nav atļauts", status=403)

    if request.method == 'POST':
        pieteikums.delete()
        return redirect('/')

    return render(request, 'pieteikumi/dzest.html', {
        'pieteikums': pieteikums
    })


def registracija(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})