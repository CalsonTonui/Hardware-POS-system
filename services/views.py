from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Service


def service_list(request):
    services = Service.objects.all()

    search = request.GET.get('search', '').strip()

    if search:
        services = services.filter(
            name__icontains=search
        )

    context = {
        'services': services,
        'search': search,
        'service_count': Service.objects.count(),
        'active_service_count': Service.objects.filter(
            is_active=True
        ).count(),
        'inactive_service_count': Service.objects.filter(
            is_active=False
        ).count(),
    }

    return render(
        request,
        'services/service_list.html',
        context
    )


def service_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Service name is required.')
            return render(
                request,
                'services/service_form.html'
            )

        if not price:
            messages.error(request, 'Service price is required.')
            return render(
                request,
                'services/service_form.html'
            )

        try:
            Service.objects.create(
                name=name,
                description=description,
                price=price,
                is_active=is_active
            )

            messages.success(
                request,
                'Service added successfully.'
            )

            return redirect('service_list')

        except ValueError:
            messages.error(
                request,
                'Please enter a valid service price.'
            )

    return render(
        request,
        'services/service_form.html'
    )


def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Service name is required.')
            return render(
                request,
                'services/service_form.html',
                {'service': service}
            )

        if not price:
            messages.error(request, 'Service price is required.')
            return render(
                request,
                'services/service_form.html',
                {'service': service}
            )

        try:
            service.name = name
            service.description = description
            service.price = price
            service.is_active = is_active
            service.save()

            messages.success(
                request,
                'Service updated successfully.'
            )

            return redirect('service_list')

        except ValueError:
            messages.error(
                request,
                'Please enter a valid service price.'
            )

    return render(
        request,
        'services/service_form.html',
        {'service': service}
    )


def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        service.delete()

        messages.success(
            request,
            'Service deleted successfully.'
        )

        return redirect('service_list')

    return render(
        request,
        'services/service_confirm_delete.html',
        {'service': service}
    )