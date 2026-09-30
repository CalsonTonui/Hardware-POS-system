from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView
from .decorators import admin_required
from .forms import UserCreateForm, UserUpdateForm
from .models import User
from django.urls import reverse

class POSLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse('dashboard')

class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'

    def form_valid(self, form):
        user = form.get_user()

        if user.role != 'admin' or not user.is_superuser:
            messages.error(
                self.request,
                'Access denied. Administrator credentials are required.'
            )
            return redirect('admin_login')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('admin_dashboard')

@login_required
@admin_required
def admin_dashboard(request):

    context = {
        'user': request.user,
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )


@login_required
@admin_required
def user_list(request):

    users = User.objects.all().order_by('username')

    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
    }

    return render(
        request,
        'accounts/user_list.html',
        context
    )


@login_required
@admin_required
def user_add(request):

    if request.method == 'POST':

        form = UserCreateForm(request.POST)

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f'User "{user.username}" was created successfully.'
            )

            return redirect('user_list')

    else:

        form = UserCreateForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'accounts/user_form.html',
        context
    )


@login_required
@admin_required
def user_edit(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':

        form = UserUpdateForm(
            request.POST,
            instance=user
        )

        if form.is_valid():

            user = form.save()

            messages.success(
                request,
                f'User "{user.username}" was updated successfully.'
            )

            return redirect('user_list')

    else:

        form = UserUpdateForm(instance=user)

    context = {
        'form': form,
        'user_account': user,
    }

    return render(
        request,
        'accounts/user_form.html',
        context
    )


@login_required
@admin_required
def user_toggle_status(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':

        if user == request.user:

            messages.error(
                request,
                'You cannot deactivate your own administrator account.'
            )

            return redirect('user_list')

        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        if user.is_active:

            messages.success(
                request,
                f'User "{user.username}" has been activated.'
            )

        else:

            messages.success(
                request,
                f'User "{user.username}" has been deactivated.'
            )

    return redirect('user_list')


@login_required
@admin_required
def user_delete(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':

        if user == request.user:

            messages.error(
                request,
                'You cannot delete your own administrator account.'
            )

            return redirect('user_list')

        username = user.username

        user.delete()

        messages.success(
            request,
            f'User "{username}" was deleted successfully.'
        )

    return redirect('user_list')