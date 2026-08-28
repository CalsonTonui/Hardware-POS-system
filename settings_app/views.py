from django.shortcuts import render, redirect
from django.contrib import messages

from .models import SystemSettings
from .forms import SettingsForm


def settings_view(request):

    settings, created = SystemSettings.objects.get_or_create(
        pk=1
    )

    if request.method == 'POST':

        form = SettingsForm(
            request.POST,
            instance=settings
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Settings updated successfully.'
            )

            return redirect('settings')

    else:

        form = SettingsForm(
            instance=settings
        )

    return render(
        request,
        'settings/settings.html',
        {
            'form': form,
            'settings': settings
        }
    )