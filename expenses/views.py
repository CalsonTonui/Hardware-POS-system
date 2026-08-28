from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum

from .models import Expense
from .forms import ExpenseForm


def expense_list(request):

    expenses = Expense.objects.all()

    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
    }

    return render(
        request,
        'expenses/expense_list.html',
        context
    )


def expense_add(request):

    if request.method == 'POST':

        form = ExpenseForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Expense added successfully.'
            )

            return redirect('expense_list')

    else:

        form = ExpenseForm()

    return render(
        request,
        'expenses/expense_form.html',
        {
            'form': form,
            'title': 'Add Expense'
        }
    )


def expense_edit(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk
    )

    if request.method == 'POST':

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Expense updated successfully.'
            )

            return redirect('expense_list')

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        'expenses/expense_form.html',
        {
            'form': form,
            'title': 'Edit Expense'
        }
    )


def expense_delete(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk
    )

    if request.method == 'POST':

        expense.delete()

        messages.success(
            request,
            'Expense deleted successfully.'
        )

        return redirect('expense_list')

    return render(
        request,
        'expenses/expense_confirm_delete.html',
        {
            'expense': expense
        }
    )