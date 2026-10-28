import os
from datetime import datetime

from django.http import FileResponse, Http404
from django.conf import settings as django_settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import SystemSettings
from .forms import SettingsForm
from accounts.decorators import admin_required
from accounts.activity import log_activity

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
@login_required
@admin_required
def backup_database(request):
    """Download a copy of the SQLite database file."""

    # Get the DB path from settings
    db_path = django_settings.DATABASES['default']['NAME']

    # Check that it exists
    if not os.path.exists(str(db_path)):
        raise Http404("Database file not found.")

    # Build a nice filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"carolivan_pos_backup_{timestamp}.sqlite3"

    # Mark the backup as done in settings
    settings_obj, _ = SystemSettings.objects.get_or_create(pk=1)
    settings_obj.mark_backup_done()

    # Log it
    log_activity(
        request,
        'settings_updated',
        f'Database backed up: {filename}',
        target_type='Settings',
        target_id=settings_obj.id,
    )

    # Return the file as a download
    response = FileResponse(
        open(str(db_path), 'rb'),
        as_attachment=True,
        filename=filename,
    )

    return response


@login_required
@admin_required
def mark_backup_done(request):
    """Mark a backup as complete (for manual backups)."""
    if request.method == 'POST':
        settings_obj, _ = SystemSettings.objects.get_or_create(pk=1)
        settings_obj.mark_backup_done()

        log_activity(
            request,
            'settings_updated',
            'Marked database backup as complete (manual)',
            target_type='Settings',
            target_id=settings_obj.id,
        )

        messages.success(
            request,
            'Backup marked as complete. '
            f'Next reminder in {settings_obj.backup_reminder_days} days.'
        )

    return redirect('admin_dashboard')