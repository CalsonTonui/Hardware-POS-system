import random
from .activity import log_activity
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .decorators import admin_required
from .forms import UserCreateForm, UserUpdateForm
from .models import User, UserCreationOTP, ActivityLog

# Direct app imports (no relative imports)
from expenses.models import Expense
from inventory.models import Inventory
from products.models import Product
from purchases.models import Purchase
from sales.models import Sale


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):
    is_expired = request.GET.get('expired') == '1'

    if request.user.is_authenticated:
        log_activity(
            request,
            'logout',
            f'User logged out: {request.user.get_full_name() or request.user.username}'
            + (' (session expired)' if is_expired else ''),
        )

    auth_logout(request)

    if is_expired:
        return redirect('/login/?expired=1')
    return redirect('login')


# =========================================================
# LOGIN VIEWS
# =========================================================

class POSLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser or user.role in ['admin', 'manager']:
            log_activity(
                self.request,
                'failed_login',
                f'Admin tried to login via cashier login: {user.username}',
            )
            messages.error(
                self.request,
                "Access Denied: Administrators must use the Admin Login link below."
            )
            return self.form_invalid(form)

        # Log the login AFTER the session is set up
        response = super().form_valid(form)
        # Now request.user is set — log with the real user
        log_activity(
            self.request,
            'login',
            f'Cashier logged in: {user.get_full_name() or user.username}',
        )
        return response

    def get_success_url(self):
        return reverse_lazy('cashier_dashboard')


class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser and user.role not in ['admin', 'manager']:
            log_activity(
                self.request,
                'failed_login',
                f'Cashier tried to login via admin login: {user.username}',
            )
            messages.error(
                self.request,
                "Access Denied: Administrator credentials required."
            )
            return self.form_invalid(form)

        response = super().form_valid(form)
        log_activity(
            self.request,
            'login',
            f'Admin logged in: {user.get_full_name() or user.username}',
        )
        return response

    def get_success_url(self):
        return reverse_lazy('admin_dashboard')


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# =========================================================
# ADMIN DASHBOARD
# =========================================================
@login_required
@admin_required
def admin_dashboard(request):
    from settings_app.models import SystemSettings

    today = timezone.localdate()
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_total = today_sales.aggregate(t=Sum('total_amount'))['t'] or 0

    total_stock = Inventory.objects.aggregate(t=Sum('quantity'))['t'] or 0

    # Low stock
    low_stock_items = Inventory.objects.select_related('product').filter(
        quantity__gt=0,
        quantity__lte=F('reorder_level')
    ).order_by('quantity')[:10]

    # Out of stock
    out_of_stock_items = Inventory.objects.select_related('product').filter(
        quantity=0
    ).order_by('product__name')[:10]

    # Backup status
    sys_settings, _ = SystemSettings.objects.get_or_create(pk=1)
    backup_is_due = sys_settings.backup_is_due()
    days_since_backup = sys_settings.days_since_last_backup()

    context = {
        'user': request.user,
        'user_count': User.objects.count(),
        'product_count': Product.objects.count(),
        'stock_count': total_stock,
        'purchase_count': Purchase.objects.count(),
        'sale_count': Sale.objects.count(),
        'expense_count': Expense.objects.count(),
        'today_total': today_total,
        'today_sale_count': today_sales.count(),
        'low_stock_items': low_stock_items,
        'low_stock_count': low_stock_items.count(),
        'out_of_stock_items': out_of_stock_items,
        'out_of_stock_count': out_of_stock_items.count(),

        # Backup
        'backup_is_due': backup_is_due,
        'days_since_backup': days_since_backup,
        'last_backup_date': sys_settings.last_backup_date,
    }
    return render(request, 'accounts/admin_dashboard.html', context)
# =========================================================
# USER LIST
# =========================================================

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by('username')

    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
        'admin_users': users.filter(role='admin').count(),
    }

    return render(request, 'accounts/user_list.html', context)


# =========================================================
# USER ADD — Step 1: Fill form + choose OTP method
# =========================================================

@login_required
@admin_required
def user_add(request):
    """Create a new user directly — no OTP required."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)

                # Set the temporary password
                user.set_password('ChangeMe@123')
                user.must_change_password = True

                # Activate if is_active is set
                if 'is_active' in request.POST:
                    user.is_active = True

                user.save()

                messages.success(
                    request,
                    f'User "{user.username}" created successfully! '
                    f'Temporary password: ChangeMe@123 — '
                    f'user must change it on first login.'
                )
                log_activity(
                    request,
                    'user_added',
                    f'User created: {user.username} (role: {user.role})',
                    target_type='User',
                    target_id=user.id,
                )
                return redirect('user_list')

            except Exception as e:
                messages.error(request, f'Error creating user: {e}')
        else:
            # Show which fields failed
            errors = []
            for field, field_errors in form.errors.items():
                for err in field_errors:
                    errors.append(f"{field}: {err}")
            messages.error(request, "Please fix: " + " | ".join(errors))

    else:
        form = UserCreateForm()


    return render(request, 'accounts/user_form.html', {'form': form})

# =========================================================
# USER ADD — Step 2: Verify OTP
# =========================================================

@login_required
@admin_required
def user_verify_otp(request):
    """Step 2: Admin enters the OTP to complete user creation."""
    otp_id = request.session.get('pending_otp_id')
    if not otp_id:
        messages.error(request, 'No pending registration found.')
        return redirect('user_add')

    try:
        otp_record = UserCreationOTP.objects.get(id=otp_id, is_used=False)
    except UserCreationOTP.DoesNotExist:
        messages.error(request, 'OTP record not found.')
        return redirect('user_add')

    if otp_record.is_expired():
        messages.error(request, 'OTP expired. Please start over.')
        otp_record.delete()
        request.session.pop('pending_otp_id', None)
        return redirect('user_add')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        if entered_otp != otp_record.otp_code:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('user_verify_otp')

        try:
            new_user = User.objects.create_user(
                username=otp_record.username,
                email=otp_record.email or '',
                first_name=otp_record.first_name,
                last_name=otp_record.last_name,
                phone=otp_record.phone,
                role=otp_record.role,
                is_active=otp_record.is_active,
            )
            new_user.set_password('ChangeMe@123')
            new_user.must_change_password = True  # NEW
            new_user.save()

            otp_record.is_used = True
            otp_record.save()
            request.session.pop('pending_otp_id', None)

            messages.success(
                request,
                f'User "{new_user.username}" created! '
                f'Temporary password: ChangeMe@123 — user will be prompted to change on first login.'
            )

            return redirect('user_list')
        except Exception as e:
            messages.error(request, f'Error creating user: {e}')
            return redirect('user_add')

    return render(request, 'accounts/user_verify_otp.html', {'record': otp_record})


# =========================================================
# HELPERS
# =========================================================

def mask_email(email):
    """user@example.com -> u***@example.com"""
    if not email or '@' not in email:
        return email
    name, domain = email.split('@', 1)
    if len(name) <= 1:
        return f"*@{domain}"
    return f"{name[0]}{'*' * (len(name) - 1)}@{domain}"


def mask_phone(phone):
    """0712345678 -> 0712***678"""
    if not phone or len(phone) < 6:
        return phone
    return f"{phone[:4]}***{phone[-3:]}"


# =========================================================
# USER EDIT
# =========================================================

@login_required
@admin_required
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            user_obj = form.save()
            messages.success(
                request,
                f'User "{user_obj.username}" was updated successfully.'
            )
            log_activity(
                request,
                'user_edited',
                f'User edited: {user_obj.username}',
                target_type='User',
                target_id=user_obj.id,
            )
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user_obj)

    context = {
        'form': form,
        'user_account': user_obj,
    }
    return render(request, 'accounts/user_form.html', context)


# =========================================================
# USER TOGGLE STATUS
# =========================================================

@login_required
@admin_required
def user_toggle_status(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(
                request,
                'You cannot deactivate your own administrator account.'
            )
            return redirect('user_list')

        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=['is_active'])

        log_activity(
            request,
            'user_activated' if user_obj.is_active else 'user_deactivated',
            f'User {"activated" if user_obj.is_active else "deactivated"}: {user_obj.username}',
            target_type='User',
            target_id=user_obj.id,
        )

        if user_obj.is_active:
            messages.success(request, f'User "{user_obj.username}" has been activated.')
        else:
            messages.success(request, f'User "{user_obj.username}" has been deactivated.')

    return redirect('user_list')


# =========================================================
# USER DELETE
# =========================================================

@login_required
@admin_required
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(
                request,
                'You cannot delete your own administrator account.'
            )
            return redirect('user_list')

        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{username}" was deleted successfully.')

        log_activity(
            request,
            'user_deleted',
            f'User deleted: {username}',
        )

    return redirect('user_list')


# =========================================================
# ROOT REDIRECT
# =========================================================

def root_redirect(request):
    """Redirect root URL to login (or dashboard if already authenticated)."""
    if request.user.is_authenticated:
        if request.user.role in ['admin', 'manager']:
            return redirect('admin_dashboard')
        elif request.user.role == 'cashier':
            return redirect('sales:pos')
        else:
            return redirect('dashboard')
    return redirect('login')

@login_required
def cashier_dashboard(request):
    """Cashier's personal dashboard with their own stats."""
    today = timezone.localdate()

    # Cashier's own sales
    my_sales = Sale.objects.filter(cashier=request.user)
    my_today_sales = my_sales.filter(sale_date__date=today)
    my_month_sales = my_sales.filter(
        sale_date__year=today.year,
        sale_date__month=today.month
    )

    today_total = my_today_sales.aggregate(t=Sum('total_amount'))['t'] or 0
    today_count = my_today_sales.count()

    month_total = my_month_sales.aggregate(t=Sum('total_amount'))['t'] or 0
    month_count = my_month_sales.count()

    # Cash vs M-Pesa breakdown for today
    today_cash = my_today_sales.filter(payment_method='Cash').aggregate(
        t=Sum('total_amount')
    )['t'] or 0
    today_mpesa = my_today_sales.filter(payment_method='M-Pesa').aggregate(
        t=Sum('total_amount')
    )['t'] or 0

    # Low stock alerts (global for awareness)
    low_stock = Inventory.objects.select_related('product').filter(
        quantity__gt=0,
        quantity__lte=F('reorder_level')
    )[:5]

    # Recent cashier sales
    recent_sales = my_sales.select_related('product').order_by('-sale_date')[:5]

    context = {
        'today_total': today_total,
        'today_count': today_count,
        'month_total': month_total,
        'month_count': month_count,
        'today_cash': today_cash,
        'today_mpesa': today_mpesa,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
        'product_count': Product.objects.count(),
    }
    return render(request, 'accounts/cashier_dashboard.html', context)

@login_required
def force_password_change(request):
    """Force user to change their temporary password on first login."""
    user = request.user

    # If user already changed, redirect away
    if not user.must_change_password:
        if user.role in ['admin', 'manager']:
            return redirect('admin_dashboard')
        elif user.role == 'cashier':
            return redirect('cashier_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        # Validation
        if not user.check_password(old_password):
            messages.error(request, 'Your current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'The two new passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif old_password == new_password1:
            messages.error(request, 'New password cannot be the same as the old password.')
        else:
            # Change password
            user.set_password(new_password1)
            user.must_change_password = False
            user.save()

            log_activity(
                request,
                'password_changed',
                f'Password changed by: {user.username}',
                target_type='User',
                target_id=user.id,
            )

            # Keep the user logged in after password change
            update_session_auth_hash(request, user)

            messages.success(
                request,
                'Password changed successfully! Welcome to Carolivan Hardware POS.'
            )

            # Redirect based on role
            if user.role in ['admin', 'manager']:
                return redirect('admin_dashboard')
            elif user.role == 'cashier':
                return redirect('cashier_dashboard')
            return redirect('dashboard')

    return render(request, 'accounts/force_password_change.html')

@login_required
@admin_required
def activity_log(request):
    """Display all activity logs with filters."""
    from datetime import timedelta

    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')

    # ---- Filters ----
    user_id = request.GET.get('user', '')
    action = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '').strip()

    if user_id:
        logs = logs.filter(user_id=user_id)
    if action:
        logs = logs.filter(action=action)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    if search:
        logs = logs.filter(description__icontains=search)

    # Limit to 500 for performance
    total_count = logs.count()
    logs = logs[:500]

    # Users for filter
    users = User.objects.filter(
        activity_logs__isnull=False
    ).distinct().order_by('username')

    # Action choices for filter
    action_choices = ActivityLog.ACTION_CHOICES

    # Stats
    today = timezone.localdate()
    today_count = ActivityLog.objects.filter(timestamp__date=today).count()
    week_ago = today - timedelta(days=7)
    week_count = ActivityLog.objects.filter(timestamp__date__gte=week_ago).count()

    context = {
        'logs': logs,
        'users': users,
        'action_choices': action_choices,
        'total_count': total_count,
        'today_count': today_count,
        'week_count': week_count,

        'filter_user': user_id,
        'filter_action': action,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'filter_search': search,
    }
    return render(request, 'accounts/activity_log.html', context)