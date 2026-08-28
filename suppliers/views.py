
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Supplier
from .forms import SupplierForm


def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')

    return render(
        request,
        'suppliers/supplier_list.html',
        {
            'suppliers': suppliers,
            'supplier_count': suppliers.count(),
        }
    )


def supplier_create(request):

    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Supplier added successfully.'
            )
            return redirect('supplier_list')

    else:
        form = SupplierForm()

    return render(
        request,
        'suppliers/supplier_form.html',
        {
            'form': form,
            'title': 'Add Supplier',
        }
    )


def supplier_detail(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    return render(
        request,
        'suppliers/supplier_detail.html',
        {
            'supplier': supplier,
        }
    )


def supplier_update(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    if request.method == 'POST':
        form = SupplierForm(
            request.POST,
            instance=supplier
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Supplier updated successfully.'
            )
            return redirect('supplier_list')

    else:
        form = SupplierForm(instance=supplier)

    return render(
        request,
        'suppliers/supplier_form.html',
        {
            'form': form,
            'title': 'Edit Supplier',
            'supplier': supplier,
        }
    )


def supplier_delete(request, pk):

    supplier = get_object_or_404(
        Supplier,
        pk=pk
    )

    if request.method == 'POST':
        supplier.delete()

        messages.success(
            request,
            'Supplier deleted successfully.'
        )

        return redirect('supplier_list')

    return render(
        request,
        'suppliers/supplier_confirm_delete.html',
        {
            'supplier': supplier,
        }
    )
