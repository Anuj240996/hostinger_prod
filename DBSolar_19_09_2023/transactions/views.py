import json
import logging
from decimal import Decimal
from operator import itemgetter

from ci_info import vendor

logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.views.generic import (
    View,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from customer.models import Customer
from customer.staff_access import (
    associate_assigned_customer_pk_list,
    associate_assert_customer_pk_allowed,
    associate_forbid_transactions_write,
    is_associate_staff,
)
from dashboard.models import staff_Notification
from .models import (
    PurchaseBill,
    Supplier,
    Vendor,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails, PurchaseSerial, FinalSaleItem, FinalSale, FinalBillDetails, ReturnSale, ReturnBillDetails,
    ReturnSaleItem, Vendor
)
from .forms import (
    SelectSupplierForm,
    # SelectVendorForm,
    PurchaseItemFormset,
    PurchaseDetailsForm,
    SupplierForm,
    VendorForm,
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm, SelectSaleForm, SaleItemFormset_bill, VendorForm
)
from inventory.models import Stock, FavoriteListStock
from product.models import (
    Product,
    Category,
    SubCategory,
    Unit,
    category_for_fk_id,
    subcategory_for_fk_id,
)
from transactions.templatetags.indian_filters import as_bill_date
from django.db.models import (
    Q,
    Prefetch,
    Sum,
    Value,
    OuterRef,
    Subquery,
    IntegerField,
    Count,
)
from django.db.models.functions import Coalesce

# # shows a lists of all suppliers
# class SupplierListView(ListView):
#     model = Supplier
#     template_name = "suppliers/suppliers_list.html"
#     queryset = Supplier.objects.filter(is_deleted=False)
#     paginate_by = 10

# class SupplierListView(ListView):
#     model = Supplier
#     template_name = "suppliers/suppliers_list.html"
#     context_object_name = 'object_list'
#     paginate_by = 10
#
#     def get_queryset(self):
#         show_all = self.request.GET.get('show_all')
#
#         # Apply ordering to the queryset to prevent pagination issues
#         if show_all == '1':
#             return Supplier.objects.filter(is_deleted=False).order_by('name')  # Order by 'name' or any other field
#         return Supplier.objects.filter(status=True, is_deleted=False).order_by('name')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['is_paginated'] = True  # Ensure this is set
#         return context
#

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404

#
# class SupplierListView(ListView):
#     model = Supplier
#     template_name = "suppliers/suppliers_list.html"
#     context_object_name = 'object_list'
#     # paginate_by = 10  # Adjust this to the number of records you want per page
#
#     def get_queryset(self):
#         show_all = self.request.GET.get('show_all')
#         if show_all == '1':
#             # Returning all active suppliers, ordered by 'name'
#             return Supplier.objects.filter(is_deleted=False).order_by('name')
#         # Returning only active suppliers with status True
#         return Supplier.objects.filter(status=True, is_deleted=False).order_by('name')

#
# class SupplierListView(LoginRequiredMixin, ListView):
#     model = Supplier
#     template_name = "suppliers/suppliers_list.html"
#     context_object_name = 'object_list'
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get_queryset(self):
#         queryset = Supplier.objects.all()
#         category = self.request.GET.get('category')
#         show_all = self.request.GET.get('show_all')
#
#         # Filter by category if selected
#         if category:
#             queryset = queryset.filter(category_id=category)
#
#         # Filter by active/inactive status based on toggle switch
#         if show_all == '1':
#             queryset = queryset.filter(status=True)
#         return queryset.order_by('name')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Add categories to the context for the dropdown
#         context['categories'] = Category.objects.all()
#         return context

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    context_object_name = 'object_list'
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_queryset(self):
        queryset = Supplier.objects.all()
        category = self.request.GET.get("category")
        show_all = self.request.GET.get("show_all")
        if category:
            queryset = queryset.filter(category_id=category)
        if show_all == "1":
            queryset = queryset.filter(status=True)
        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Stable order; avoids ambiguous dropdown if legacy duplicate names exist
        context["categories"] = Category.objects.all().order_by("name", "id")

        # Add staff notification count and notifications to the context
        context['count1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).count()
        context['notification1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).order_by('-created_at')

        return context


# # used to add a new supplier
# class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     model = Supplier
#     form_class = SupplierForm
#     success_url = '/transactions/suppliers'
#     success_message = "Supplier has been created successfully"
#     template_name = "suppliers/edit_supplier.html"
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'New Supplier'
#         context["savebtn"] = 'Add Supplier'
#         return context

    # used to update a supplier's info
class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'

        # Add staff notification data to the context
        context['count1'] = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).count()
        context['notification1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).order_by('-created_at')

        return context

def supplier_detail_json(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    # Build the data for JSON response
    data = {
        'name': supplier.name,
        'contact_person': supplier.contact_person,
        'phone': supplier.phone,
        'email': supplier.email,
        'gstin': supplier.gstin,
        'address': supplier.address,
        'city': supplier.city,
        'state': supplier.state,
        'post_code': supplier.post_code,
        'status': supplier.status,
    }

    return JsonResponse(data)


#
# class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
#     model = Supplier
#     form_class = SupplierForm
#     success_url = '/transactions/suppliers'
#     success_message = "Supplier details has been updated successfully"
#     template_name = "suppliers/edit_supplier.html"
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edit Supplier'
#         context["savebtn"] = 'Save Changes'
#         context["delbtn"] = 'Delete Supplier'
#         return context


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'

        # Adding staff notifications
        count1 = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).order_by('-created_at')

        context["notification_count"] = count1
        context["notifications"] = notification1

        return context


# used to delete a supplier
# class SupplierDeleteView(LoginRequiredMixin, View):
#     template_name = "suppliers/delete_supplier.html"
#     success_message = "Supplier has been deleted successfully"
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, pk):
#         supplier = get_object_or_404(Supplier, pk=pk)
#         return render(request, self.template_name, {'object': supplier})
#
#     def post(self, request, pk):
#         supplier = get_object_or_404(Supplier, pk=pk)
#         supplier.is_deleted = True
#         supplier.save()
#         messages.success(request, self.success_message)
#         return redirect('suppliers-list')

class SupplierDeleteView(LoginRequiredMixin, View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        # Adding staff notification logic
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')
        return render(request, self.template_name, {
            'object': supplier,
            'count1': count1,
            'notification1': notification1
        })

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.status = False
        supplier.save()
        messages.success(request, self.success_message)
        return redirect('suppliers-list')



# used to view a supplier's profile
# class SupplierView(LoginRequiredMixin, View):
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, name):
#         supplierobj = get_object_or_404(Supplier, name=name)
#         bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
#         page = request.GET.get('page', 1)
#         paginator = Paginator(bill_list, 10)
#         try:
#             bills = paginator.page(page)
#         except PageNotAnInteger:
#             bills = paginator.page(1)
#         except EmptyPage:
#             bills = paginator.page(paginator.num_pages)
#         context = {
#             'supplier': supplierobj,
#             'bills': bills
#         }
#         return render(request, 'suppliers/supplier.html', context)
#
# class SupplierView(LoginRequiredMixin, View):
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, name):
#         supplierobj = get_object_or_404(Supplier, name=name)
#         bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
#
#         # Add notification logic
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
#             '-created_at')
#
#         page = request.GET.get('page', 1)
#         paginator = Paginator(bill_list, 10)
#         try:
#             bills = paginator.page(page)
#         except PageNotAnInteger:
#             bills = paginator.page(1)
#         except EmptyPage:
#             bills = paginator.page(paginator.num_pages)
#
#         context = {
#             'supplier': supplierobj,
#             'bills': bills,
#             'count1': count1,  # Pass count to the context
#             'notification1': notification1,  # Pass notifications to the context
#         }
#         return render(request, 'suppliers/supplier.html', context)

from django.utils.dateparse import parse_date


def _scope_dc_list_queryset_for_associate(request, queryset, *, use_salebill_cust_fk=False):
    """
    Non-superuser associates: only list DCs for consumers (Customer) assigned to them
    (Assoc_Assign). Vendor-only lists are hidden. Superuser and non-associate staff unchanged.
    """
    user = request.user
    if (
        not getattr(user, "is_authenticated", False)
        or not is_associate_staff(user)
        or getattr(user, "is_superuser", False)
    ):
        return queryset
    user_type = request.GET.get("user_type", "All")
    if user_type == "Vendor":
        return queryset.none()
    pks = associate_assigned_customer_pk_list(user)
    if not pks:
        return queryset.none()
    if use_salebill_cust_fk:
        return queryset.filter(Cust_id_id__in=pks)
    return queryset.filter(customer_id__in=pks)


class SupplierView(LoginRequiredMixin, View):
    login_url = '/index/'

    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)

        # Get filter parameters from the request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Apply date filtering if both dates are provided
        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            if start_date and end_date:
                bill_list = bill_list.filter(time__date__range=[start_date, end_date])

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)

        context = {
            'supplier': supplierobj,
            'bills': bills,
            'count1': staff_Notification.objects.filter(staff_id=request.user.id, status=False).count(),
            'notification1': staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at'),
        }
        return render(request, 'suppliers/supplier.html', context)

#
# class AllSaleView(LoginRequiredMixin, View):
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, Cust_id):
#         supplierobj = get_object_or_404(Customer, Cust_id=Cust_id)
#         bill_list = SaleBill.objects.filter(Cust_id=supplierobj)
#
#         # Add notification logic
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
#             '-created_at')
#
#         page = request.GET.get('page', 1)
#         paginator = Paginator(bill_list, 10)
#         try:
#             bills = paginator.page(page)
#         except PageNotAnInteger:
#             bills = paginator.page(1)
#         except EmptyPage:
#             bills = paginator.page(paginator.num_pages)
#
#         context = {
#             'supplier': supplierobj,
#             'bills': bills,
#             'count1': count1,  # Pass count to the context
#             'notification1': notification1,  # Pass notifications to the context
#         }
#         return render(request, 'suppliers/supplier.html', context)

class AllSaleView(LoginRequiredMixin, View):
    login_url = '/index/'

    def get(self, request, typ, obj_id):
        if typ == 'customer':
            associate_assert_customer_pk_allowed(request.user, obj_id)
            supplierobj = get_object_or_404(Customer, Cust_id=obj_id)
            bill_list = SaleBill.objects.filter(Cust_id=supplierobj)
            context_object = {'supplier': supplierobj}
            template_name = 'sales/sale.html'
        elif typ == 'vendor':
            if is_associate_staff(request.user) and not getattr(
                request.user, "is_superuser", False
            ):
                raise PermissionDenied(
                    "Vendor DC lists are not available for your account."
                )
            vendorobj = get_object_or_404(Vendor, pk=obj_id)
            bill_list = SaleBill.objects.filter(Vend_id=vendorobj)
            context_object = {'vendor': vendorobj}
            template_name = 'sales/sale.html'
        else:
            raise Http404("Invalid type")

        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)

        # Update with common context variables only
        context_object.update({
            'bills': bills,
            'count1': count1,
            'notification1': notification1,
        })
        return render(request, template_name, context_object)



class AllFinalSaleView(LoginRequiredMixin, View):
    login_url = '/index/'

    def get(self, request, typ, obj_id):
        if typ == 'customer':
            associate_assert_customer_pk_allowed(request.user, obj_id)
            supplierobj = get_object_or_404(Customer, Cust_id=obj_id)
            bill_list = FinalSale.objects.filter(customer=supplierobj)
            context_object = {'supplier': supplierobj}
            template_name = 'sales/finalsale.html'
        elif typ == 'vendor':
            if is_associate_staff(request.user) and not getattr(
                request.user, "is_superuser", False
            ):
                raise PermissionDenied(
                    "Vendor DC lists are not available for your account."
                )
            vendorobj = get_object_or_404(Vendor, pk=obj_id)
            bill_list = FinalSale.objects.filter(vendor=vendorobj)
            context_object = {'vendor': vendorobj}
            template_name = 'sales/finalsale.html'
        else:
            raise Http404("Invalid type")

        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)

        # Update with common context variables only
        context_object.update({
            'bills': bills,
            'count1': count1,
            'notification1': notification1,
        })
        return render(request, template_name, context_object)


#
# # Create List For Return Bill Details
# class AllReturnSaleView(LoginRequiredMixin, View):
#     login_url = '/index/'
#
#     def get(self, request, typ, obj_id):
#         if typ == 'customer':
#             supplierobj = get_object_or_404(Customer, Cust_id=obj_id)
#             bill_list = ReturnSale.objects.filter(customer=supplierobj)
#             context_object = {'supplier': supplierobj}
#             # template_name = 'return/returnsale.html'
#             template_name = "return/return.html"
#         elif typ == 'vendor':
#             vendorobj = get_object_or_404(Vendor, pk=obj_id)
#             bill_list = ReturnSale.objects.filter(vendor=vendorobj)
#             context_object = {'vendor': vendorobj}
#             template_name = "return/return.html"
#         else:
#             raise Http404("Invalid type")
#
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#         page = request.GET.get('page', 1)
#         paginator = Paginator(bill_list, 10)
#         try:
#             bills = paginator.page(page)
#         except PageNotAnInteger:
#             bills = paginator.page(1)
#         except EmptyPage:
#             bills = paginator.page(paginator.num_pages)
#
#
#         # Update with common context variables only
#         context_object.update({
#             'bills': bills,
#             'count1': count1,
#             'notification1': notification1,
#         })
#         return render(request, template_name, context_object)


# Create List For Return Bill Details
class AllReturnSaleView(LoginRequiredMixin, View):
    login_url = '/index/'

    def get(self, request, typ, obj_id):
        if typ == 'customer':
            associate_assert_customer_pk_allowed(request.user, obj_id)
            supplierobj = get_object_or_404(Customer, Cust_id=obj_id)
            bill_list = ReturnSale.objects.filter(customer=supplierobj)
            context_object = {'supplier': supplierobj}
            template_name = "return/return.html"
        elif typ == 'vendor':
            if is_associate_staff(request.user) and not getattr(
                request.user, "is_superuser", False
            ):
                raise PermissionDenied(
                    "Vendor DC lists are not available for your account."
                )
            vendorobj = get_object_or_404(Vendor, pk=obj_id)
            bill_list = ReturnSale.objects.filter(vendor=vendorobj)
            context_object = {'vendor': vendorobj}
            template_name = "return/return.html"
        else:
            raise Http404("Invalid type")

        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)

        # Add filtered items list to each bill, only where r_quantity > 0
        for bill in bills:
            # Filter related ReturnSaleItem objects by r_quantity > 0
            bill.filtered_items = [
                item for item in bill.return_sale_items.all() if item.r_quantity > 0
            ]

        # Update context
        context_object.update({
            'bills': bills,
            'count1': count1,
            'notification1': notification1,
        })
        return render(request, template_name, context_object)


class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = "vendor/vendor_list.html"
    context_object_name = 'object_list'
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_queryset(self):
        queryset = Vendor.objects.all()
        category = self.request.GET.get('category')
        show_all = self.request.GET.get('show_all')

        # Filter by category if selected
        if category:
            queryset = queryset.filter(category_id=category)

        # Filter by active/inactive status based on toggle switch
        if show_all == '1':
            queryset = queryset.filter(status=True)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories to the context for the dropdown
        context['categories'] = Category.objects.all()

        # Add staff notification count and notifications to the context
        context['count1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).count()
        context['notification1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).order_by('-created_at')

        return context



    # used to update a supplier's info
class VendorCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    success_url = '/transactions/vendor'
    success_message = "Vendor has been created successfully"
    template_name = "vendor/edit_vendor.html"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Vendor'
        context["savebtn"] = 'Add Vendor'

        # Add staff notification data to the context
        context['count1'] = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).count()
        context['notification1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False).order_by('-created_at')

        return context

def vendor_detail_json(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)

    # Build the data for JSON response
    data = {
        'name': vendor.name,
        'contact_person': vendor.contact_person,
        'phone': vendor.phone,
        'email': vendor.email,
        'gstin': vendor.gstin,
        'address': vendor.address,
        'city': vendor.city,
        'state': vendor.state,
        'post_code': vendor.post_code,
        'status': vendor.status,
    }

    return JsonResponse(data)




class VendorUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    success_url = '/transactions/vendor'
    success_message = "Vendor details has been updated successfully"
    template_name = "vendor/edit_vendor.html"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Vendor'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Vendor'

        # Adding staff notifications
        count1 = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).order_by('-created_at')

        context["notification_count"] = count1
        context["notifications"] = notification1

        return context



class VendorDeleteView(LoginRequiredMixin, View):
    template_name = "vendor/delete_vendor.html"
    success_message = "Vendor has been deleted successfully"
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        # Adding staff notification logic
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')
        return render(request, self.template_name, {
            'object': vendor,
            'count1': count1,
            'notification1': notification1
        })

    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        vendor.is_deleted = True
        vendor.status = False
        vendor.save()
        messages.success(request, self.success_message)
        return redirect('vendor-list')


class VendorView(LoginRequiredMixin, View):
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)

        # Add notification logic
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')

        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)

        context = {
            'supplier': supplierobj,
            'bills': bills,
            'count1': count1,  # Pass count to the context
            'notification1': notification1,  # Pass notifications to the context
        }
        return render(request, 'suppliers/supplier.html', context)







# # shows the list of bills of all purchases
# class PurchaseView(ListView):
#     model = PurchaseBill
#     template_name = "purchases/purchases_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']
#     # paginate_by = 10

#
# class PurchaseView(ListView):
#     model = PurchaseBill
#     template_name = "purchases/purchases_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         category_id = self.request.GET.get('category')
#
#         # Filter purchases by category if a category is selected
#         if category_id:
#             queryset = queryset.filter(supplier__category_id=category_id)
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()  # Get all categories
#         selected_category = None
#
#         category_id = self.request.GET.get('category')
#         if category_id:
#             selected_category = Category.objects.filter(id=category_id).first()
#
#         context['selected_category'] = selected_category
#         return context

from django.utils import timezone
from datetime import timedelta

from django.utils.dateparse import parse_date
from datetime import timedelta

#
# class PurchaseView(LoginRequiredMixin, ListView):
#     model = PurchaseBill
#     template_name = "purchases/purchases_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Category filter
#         category_id = self.request.GET.get('category')
#         if category_id:
#             queryset = queryset.filter(supplier__category_id=category_id)
#
#         # Date filter
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         # Date filter logic
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             # Get custom date range from the request
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Ensure start_date and end_date are provided and parsed correctly
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             # If valid start_date and end_date, apply filter
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 # Show all data if dates are not valid
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all categories for category dropdown
#         context['categories'] = Category.objects.all()
#
#         # Handle selected category for filtering
#         selected_category = None
#         category_id = self.request.GET.get('category')
#         if category_id:
#             selected_category = Category.objects.filter(id=category_id).first()
#
#         context['selected_category'] = selected_category
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter heading logic
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             # Custom date range
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Convert strings to datetime objects
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context


class PurchaseView(LoginRequiredMixin, ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']  # Default ordering by 'time'
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get_queryset(self):
        queryset = super().get_queryset()

        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(supplier__category_id=category_id)

        # Date filter
        filter_value = self.request.GET.get('filter', 'All')
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None
        table_name = PurchaseBill._meta.db_table

        def _apply_text_date_between(qs, start_dt, end_dt):
            return qs.extra(
                where=[
                    f"substring(COALESCE({table_name}.time::text, ''), 1, 10) BETWEEN %s AND %s"
                ],
                params=[start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")],
            )

        # Date filter logic
        if filter_value == 'Today':
            start_date = today
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == 'Last7Days':
            start_date = today - timedelta(days=7)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == 'Last30Days':
            start_date = today - timedelta(days=30)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == 'ThisMonth':
            start_date = today.replace(day=1)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == 'Custom':
            # Get custom date range from the request
            start_date_str = self.request.GET.get('start_date')
            end_date_str = self.request.GET.get('end_date')

            # Ensure start_date and end_date are provided and parsed correctly
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            # If valid start_date and end_date, apply filter
            if start_date and end_date:
                queryset = _apply_text_date_between(queryset, start_date, end_date)
            else:
                # Show all data if dates are not valid
                queryset = queryset.none()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all categories for category dropdown
        context['categories'] = Category.objects.all()

        # Handle selected category for filtering
        selected_category = None
        category_id = self.request.GET.get('category')
        if category_id:
            selected_category = Category.objects.filter(id=category_id).first()

        context['selected_category'] = selected_category

        # Pass filter value to the context
        filter_option = self.request.GET.get('filter', 'All')
        context['selected_filter'] = filter_option

        # Notifications
        context['count1'] = staff_Notification.objects.filter(staff_id=self.request.user.id, status=False).count()
        context['notification1'] = staff_Notification.objects.filter(
            staff_id=self.request.user.id, status=False
        ).order_by('-created_at')

        # Date filter heading logic
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None

        if filter_option == "All":
            caption_text = "Display All Days View"
            caption_text1 = "Up To Date"
        elif filter_option == "Today":
            start_date = today
            end_date = today
            caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Today"
        elif filter_option == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 7 Days"
        elif filter_option == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 30 Days"
        elif filter_option == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "This Month"
        elif filter_option == "Custom":
            # Custom date range
            start_date_str = self.request.GET.get('start_date')
            end_date_str = self.request.GET.get('end_date')

            # Convert strings to datetime objects
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            if start_date_str and end_date_str:
                caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            else:
                caption_text = "Display Custom Range View"
            caption_text1 = "Custom Range"
        else:
            caption_text = "The option is not selected, so all records show"
            caption_text1 = ""

        context['caption_text'] = caption_text
        context['caption_text1'] = caption_text1

        # Pass custom date range values to the context
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')

        return context


# View to select the supplier based on category
# class SelectSupplierView(LoginRequiredMixin, View):
#     form_class = SelectSupplierForm
#     template_name = 'purchases/select_supplier.html'
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, *args, **kwargs):  # loads the form page
#         form = self.form_class()
#         categories = Category.objects.all()  # Fetch all categories
#         return render(request, self.template_name, {'form': form, 'categories': categories})
#
#     def post(self, request, *args, **kwargs):  # gets selected supplier and redirects to 'PurchaseCreateView' class
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             supplierid = request.POST.get("supplier")
#             supplier = get_object_or_404(Supplier, id=supplierid)
#             return redirect('new-purchase', supplier.pk)
#         categories = Category.objects.all()  # Reload categories on failed submission
#         return render(request, self.template_name, {'form': form, 'categories': categories})


class SelectSupplierView(LoginRequiredMixin, View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get(self, request, *args, **kwargs):  # loads the form page
        form = self.form_class()
        categories = Category.objects.all()  # Fetch all categories

        # Adding notification logic
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')

        return render(request, self.template_name, {
            'form': form,
            'categories': categories,
            'count1': count1,
            'notification1': notification1
        })

    def post(self, request, *args, **kwargs):  # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)

        categories = Category.objects.all()  # Reload categories on failed submission

        # Adding notification logic
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')

        return render(request, self.template_name, {
            'form': form,
            'categories': categories,
            'count1': count1,
            'notification1': notification1
        })


# # AJAX view to get suppliers based on the selected category
# def get_suppliers(request, category_id):
#     suppliers = Supplier.objects.filter(category=category_id)  # Get suppliers for the selected category
#     suppliers_data = [{'id': supplier.id, 'name': supplier.supplier_name} for supplier in suppliers]
#     return JsonResponse({'suppliers': suppliers_data})
def get_suppliers(request, category_id):
    # Fetch suppliers filtered by the selected category
    suppliers = Supplier.objects.filter(category_id=category_id)
    # Use the correct field name 'name' instead of 'supplier_name'
    suppliers_data = [{'id': supplier.id,
                       # 'name': supplier.name
                       'name': f"{supplier.name}, {supplier.city}"
    } for supplier in suppliers]

    # Return the suppliers in JSON format
    return JsonResponse({'suppliers': suppliers_data})




# # used to generate a bill object and save items
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset(request.GET or None)  # renders an empty formset
#         supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#         }  # sends the supplier and formset as context
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)  # recieves a post method for the formset
#         supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
#         if formset.is_valid():
#             # saves bill
#             billobj = PurchaseBill(
#                 supplier=supplierobj)  # a new object of class 'PurchaseBill' is created with supplier field set to 'supplierobj'
#             billobj.save()  # saves object into the db
#             # create bill details object
#             billdetailsobj = PurchaseBillDetails(billno=billobj)
#             billdetailsobj.save()
#             for form in formset:  # for loop to save each individual form as its own object
#                 # false saves the item and links bill to the item
#                 billitem = form.save(commit=False)
#                 billitem.billno = billobj  # links the bill object to the items
#                 # gets the stock item
#                 stock = get_object_or_404(Stock, name=billitem.stock.name)  # gets the item
#                 # calculates the total price
#                 billitem.totalprice = billitem.perprice * billitem.quantity
#                 # updates quantity in stock db
#                 stock.quantity += billitem.quantity  # updates quantity
#                 # saves bill item and stock
#                 stock.save()
#                 billitem.save()
#             messages.success(request, "Purchased items have been registered successfully")
#             return redirect('purchase-bill', billno=billobj.billno)
#         formset = PurchaseItemFormset(request.GET or None)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj
#         }
#         return render(request, self.template_name, context)

#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset(request.GET or None)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         stocks = Stock.objects.filter(is_deleted=False)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stocks': stocks,
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         formset = PurchaseItemFormset(request.POST)
#
#         if formset.is_valid():
#             billobj = PurchaseBill(supplier=supplierobj)
#             billobj.save()
#
#             billdetailsobj = PurchaseBillDetails(billno=billobj)
#             billdetailsobj.save()
#
#             for form in formset:
#                 billitem = form.save(commit=False)
#                 billitem.billno = billobj
#                 stock = get_object_or_404(Stock, name=billitem.stock.name)
#                 billitem.totalprice = billitem.perprice * billitem.quantity
#                 stock.quantity += billitem.quantity
#                 stock.save()
#                 billitem.save()
#
#             messages.success(request, "Purchased items have been registered successfully")
#             return redirect('purchase-bill', billno=billobj.billno)
#
#         stocks = Stock.objects.filter(is_deleted=False)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stocks': stocks,
#         }
#         return render(request, self.template_name, context)

#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset(request.GET or None)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         stock_list = Stock.objects.filter(is_deleted=False)  # Fetch all available stocks
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': stock_list,  # Pass the stock list to the template
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         if formset.is_valid():
#             billobj = PurchaseBill(supplier=supplierobj)
#             billobj.save()
#             billdetailsobj = PurchaseBillDetails(billno=billobj)
#             billdetailsobj.save()
#             for form in formset:
#                 billitem = form.save(commit=False)
#                 billitem.billno = billobj
#                 stock = get_object_or_404(Stock, name=billitem.stock.name)
#                 billitem.totalprice = billitem.perprice * billitem.quantity
#                 stock.quantity += billitem.quantity
#                 stock.save()
#                 billitem.save()
#             messages.success(request, "Purchased items have been registered successfully")
#             return redirect('purchase-bill', billno=billobj.billno)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False)  # Pass the stock list on error
#         }
#         return render(request, self.template_name, context)


from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
import logging

from django.http import JsonResponse
from product.models import Category, SubCategory


logger = logging.getLogger(__name__)
#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     # # Save PurchaseBillDetails
#                     # billdetailsobj = PurchaseBillDetails(billno=billobj)
#
#                     # Extract GST toggle state
#                     gst_toggle = request.POST.get('gstToggle')  # Adjust the key as per your HTML input name
#
#                     # Initialize GST values
#                     gst_value = 0
#                     gst_amount = 0
#
#                     if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
#                         gst_value = request.POST.get('gst_value')  # Adjust the key as per your HTML input name
#                         gst_amount = request.POST.get('gst_amount')  # Adjust the key as per your HTML input name
#
#                     # Save PurchaseBillDetails
#                     billdetailsobj = PurchaseBillDetails(
#                         billno=billobj,
#                         gst_value=gst_value,
#                         gst_amount=gst_amount,
#                         final_amount=request.POST.get('final_amount'),  # Adjust the key as per your HTML input name
#                     )
#                     billdetailsobj.save()
#                     logger.info("PurchaseBillDetails saved successfully")
#
#                     # Save each PurchaseItem and update Stock
#                     for form in formset:
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Get the associated stock
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#
#                         billitem.purchase = billitem.purchase
#                         # Calculate the total price for the item
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#
#                         # Update stock quantity
#                         stock.quantity += billitem.quantity
#                         stock.save()
#                         logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                         # Save the PurchaseItem
#                         billitem.save()
#                         logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#
#                     # If everything goes well
#                     # messages.success(request, "Purchased items have been registered successfully")
#                     # return HttpResponseRedirect('/transactions/purchases/')  # Use HttpResponseRedirect for redirection
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('purchase-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#             # 'product_list': Product.objects.filter(status=1),
#         }
#         return render(request, self.template_name, context)

# class PurchaseCreateView(LoginRequiredMixin, View):
#     template_name = 'purchases/new_purchase.html'
#     login_url = '/index/'  # URL to redirect to if the user is not logged in
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     # Extract GST toggle state
#                     gst_toggle = request.POST.get('gstToggle')
#
#                     # Initialize GST values
#                     gst_value = 0
#                     gst_amount = 0
#                     eway_no = 0
#                     veh_no = 0
#                     hand_by = 0
#                     destination = 0
#                     po_no = 0
#                     po_date = 0
#                     round_off = request.POST.get('round_off')
#                     final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#                     eway_no = request.POST.get('eway_no')
#                     bill_date = request.POST.get('bill_date')
#                     veh_no = request.POST.get('veh_no')
#                     hand_by = request.POST.get('handby')
#                     destination = request.POST.get('destination')
#                     po_no = request.POST.get('po_no')
#                     po_date = request.POST.get('po_date')
#
#                     if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
#                         gst_value = request.POST.get('gst_value')
#                         gst_amount = request.POST.get('gst_amount')
#
#                         # round_off = request.POST.get('round_off')
#                         #
#                         # # Clean the final amount (remove ₹ symbol)
#                         # final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#
#                     # Save PurchaseBillDetails
#                     billdetailsobj = PurchaseBillDetails(
#                         billno=billobj,
#                         gst_value=gst_value,
#                         gst_amount=gst_amount,
#                         round_off = round_off,
#                         eway = eway_no,
#                         cgst = bill_date,
#                         veh = veh_no,
#                         igst = hand_by,
#                         destination = destination,
#                         po = po_no,
#                         tcs = po_date,
#                         # final_amount=request.POST.get('final_amount'),
#                         final_amount=final_amount,
#                         total_amount=request.POST.get('total_amount'),
#                     )
#                     billdetailsobj.save()
#                     logger.info("PurchaseBillDetails saved successfully")
#
#                     # Save each PurchaseItem and update Stock
#                     # for form in formset:
#                     for index, form in enumerate(formset):
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Get the associated stock
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#
#                         # Get the `short_name` from the form and look up the Unit instance
#                         short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
#                         unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
#                         billitem.purchase = unit_instance
#
#                         # Calculate the total price for the item
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#
#                         # Update stock quantity
#                         stock.quantity += billitem.quantity
#                         stock.save()
#                         logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                         # Save the PurchaseItem
#                         billitem.save()
#                         logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#
#                         # Save PurchaseSerial entries
#                         serial_numbers = request.POST.getlist(f'serial_numbers_{index}[]')
#                         for serial_number in serial_numbers:
#                             purchase_serial = PurchaseSerial(
#                                 billno=billobj,
#                                 stock=stock,
#                                 purchase=unit_instance,
#                                 serialNo=serial_number,
#                                 item=billitem  # Link to the saved PurchaseItem
#                             )
#                             purchase_serial.save()
#                             logger.info(
#                                 f"PurchaseSerial saved successfully for stock id {stock.id} with serial number {serial_number}")
#
#                     # If everything goes well
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('purchase-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)



class PurchaseCreateView(LoginRequiredMixin, View):
    template_name = 'purchases/new_purchase.html'
    login_url = '/index/'  # URL to redirect to if the user is not logged in

    def get(self, request, pk):
        # Fetch unread notifications count and the latest unread notifications
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        formset = PurchaseItemFormset()
        supplierobj = get_object_or_404(Supplier, pk=pk)
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
            'count1': count1,  # Add the unread notification count
            'notification1': notification1,  # Add the unread notifications
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)
        supplierobj = get_object_or_404(Supplier, pk=pk)
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        logger.info(f"PurchaseCreateView POST received. Formset valid: {formset.is_valid()}")
        if not formset.is_valid():
            logger.warning(f"Formset validation failed. Errors: {formset.errors}")
            logger.warning(f"Non-form errors: {formset.non_form_errors()}")

        if formset.is_valid():
            try:
                with transaction.atomic():
                    # Save PurchaseBill
                    billobj = PurchaseBill(supplier=supplierobj)
                    billobj.save()
                    logger.info("PurchaseBill saved successfully")

                    # Extract GST toggle state
                    gst_toggle = request.POST.get('gstToggle')

                    # Initialize GST values
                    gst_value = 0
                    gst_amount = 0
                    eway_no = 0
                    veh_no = 0
                    hand_by = 0
                    destination = 0
                    po_no = 0
                    po_date = 0
                    round_off = request.POST.get('round_off')
                    delivery_charges = request.POST.get('delivery_charges')
                    final_amount_raw = request.POST.get('final_amount', '0')
                    final_amount = final_amount_raw.replace('₹', '').strip() if final_amount_raw else '0'
                    eway_no = request.POST.get('eway_no')
                    bill_date = request.POST.get('bill_date')
                    veh_no = request.POST.get('veh_no')
                    hand_by = request.POST.get('handby')
                    destination = request.POST.get('destination')
                    po_no = request.POST.get('po_no')
                    po_date = request.POST.get('po_date')

                    if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
                        gst_value = request.POST.get('gst_value')
                        gst_amount = request.POST.get('gst_amount')

                    # Save PurchaseBillDetails
                    billdetailsobj = PurchaseBillDetails(
                        billno=billobj,
                        gst_value=gst_value,
                        gst_amount=gst_amount,
                        round_off=round_off,
                        delivery_charges=delivery_charges,
                        eway=eway_no,
                        cgst=po_date,
                        veh=veh_no,
                        igst=hand_by,
                        destination=destination,
                        po=po_no,
                        tcs=bill_date,
                        # final_amount=request.POST.get('final_amount'),
                        final_amount=final_amount,
                        total_amount=request.POST.get('total_amount'),
                    )
                    billdetailsobj.save()
                    logger.info("PurchaseBillDetails saved successfully")

                    # Save each PurchaseItem and update Stock
                    items_saved = 0
                    for index, form in enumerate(formset):
                      if form.is_valid() and form.cleaned_data:
                        # Skip empty forms
                        if not form.cleaned_data.get('stock'):
                            logger.info(f"Skipping empty form at index {index}")
                            continue
                            
                        billitem = form.save(commit=False)
                        billitem.billno = billobj

                        # Get the associated stock
                        stock = get_object_or_404(Stock, pk=billitem.stock.id)

                        # Get the `short_name` from the form and look up the Unit instance

                        # short_name = request.POST.get('purchase_id')
                        # unit_instance = get_object_or_404(Unit, id=short_name)
                        # billitem.purchase = unit_instance

                        unit_instance = form.cleaned_data.get('purchase')
                        if not unit_instance:
                            raise ValueError("Purchase unit is required for item {}".format(index))

                        billitem.purchase = unit_instance

                        # Calculate the total price for the item
                        billitem.totalprice = billitem.perprice * billitem.quantity

                        # Update stock quantity
                        stock.quantity += billitem.quantity
                        stock.save()
                        logger.info(f"Stock updated successfully for stock id {stock.id}")

                        # Save the PurchaseItem
                        billitem.save()
                        logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")

                        # Save PurchaseSerial entries
                        serial_numbers = request.POST.getlist(f'serial_numbers_{index}[]')
                        for serial_number in serial_numbers:
                            purchase_serial = PurchaseSerial(
                                billno=billobj,
                                stock=stock,
                                purchase=unit_instance,
                                serialNo=serial_number,
                                item=billitem  # Link to the saved PurchaseItem
                            )
                            purchase_serial.save()
                            logger.info(
                                f"PurchaseSerial saved successfully for stock id {stock.id} with serial number {serial_number}")
                        items_saved += 1
                    
                    if items_saved == 0:
                        raise ValueError("No items were saved. Please add at least one item to the purchase.")
                    
                    logger.info(f"Successfully saved {items_saved} purchase items")

                    # If everything goes well
                    messages.success(request, "Purchased items have been registered successfully")
                    logger.info(f"Redirecting to purchase-bill with billno: {billobj.billno}")
                    return redirect('purchase-bill', billno=billobj.billno)

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"An error occurred in PurchaseCreateView: {str(e)}")
                logger.error(f"Traceback: {error_trace}")
                messages.error(request, f"An error occurred: {str(e)}. Please check the server logs for details.")
        else:
            logger.warning(f"Formset is not valid: {formset.errors}")
            error_msg = "There were errors in the form. Please correct them."
            if formset.errors:
                error_msg += f" Errors: {formset.errors}"
            messages.error(request, error_msg)

        # If form is not valid or any other error occurs
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
            'count1': count1,  # Add the unread notification count again
            'notification1': notification1,  # Add the unread notifications again
        }
        return render(request, self.template_name, context)

#
# # views.py
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from pyzbar.pyzbar import decode
# from PIL import Image
# import pytesseract
# from pdf2image import convert_from_bytes
#
# @csrf_exempt
# def extract_serials(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     if file.name.lower().endswith('.pdf'):
#         pages = convert_from_bytes(file.read())
#         for page in pages:
#             img = page.convert('RGB')
#             serials += extract_from_image(img)
#     else:
#         image = Image.open(file).convert('RGB')
#         serials += extract_from_image(image)
#
#     return JsonResponse({'serials': list(set(serials))[:100]})
#
# def extract_from_image(pil_img):
#     barcodes = decode(pil_img)
#     serials = [barcode.data.decode('utf-8') for barcode in barcodes]
#
#     text = pytesseract.image_to_string(pil_img)
#     lines = text.splitlines()
#     for line in lines:
#         clean = line.strip()
#         if clean and clean not in serials:
#             serials.append(clean)
#
#     return serials


# views.py
import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO

# @csrf_exempt
# def extract_serials(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     if file.name.lower().endswith('.pdf'):
#         pages = convert_from_bytes(file.read(), dpi=300)
#         for page in pages:
#             serials += extract_from_image(page)
#     else:
#         image = Image.open(file).convert('RGB')
#         serials += extract_from_image(image)
#
#     # Deduplicate and return up to 100 serials
#     return JsonResponse({'serials': list(set(serials))[:100]})
#
# def extract_from_image(pil_img):
#     serials = []
#
#     # Convert PIL image to OpenCV
#     open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
#
#     # Convert to grayscale
#     gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
#
#     # Increase contrast
#     gray = cv2.equalizeHist(gray)
#
#     # Resize for better detection
#     scale_percent = 150  # Increase size by 150%
#     width = int(gray.shape[1] * scale_percent / 100)
#     height = int(gray.shape[0] * scale_percent / 100)
#     dim = (width, height)
#     gray = cv2.resize(gray, dim, interpolation=cv2.INTER_LINEAR)
#
#     # Decode barcodes
#     barcodes = decode(gray, symbols=[ZBarSymbol.CODE128, ZBarSymbol.EAN13, ZBarSymbol.QRCODE])
#     for barcode in barcodes:
#         data = barcode.data.decode('utf-8')
#         if data not in serials:
#             serials.append(data)
#
#     # OCR fallback for text-based serials
#     ocr_text = pytesseract.image_to_string(pil_img)
#     for line in ocr_text.splitlines():
#         clean = line.strip()
#         if clean and clean not in serials:
#             serials.append(clean)
#
#     return serials


#
# # views.py
# import cv2
# import numpy as np
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from PIL import Image
# from pdf2image import convert_from_bytes
# from pyzbar.pyzbar import decode, ZBarSymbol
# from io import BytesIO
#
# @csrf_exempt
# def extract_barcode_data(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     try:
#         if file.name.lower().endswith('.pdf'):
#             # Convert PDF to images
#             pages = convert_from_bytes(file.read(), dpi=300)
#             for page in pages:
#                 serials += extract_from_image(page)
#         else:
#             image = Image.open(file).convert('RGB')
#             serials += extract_from_image(image)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'serials': list(set(serials))[:100]})
#
# def extract_from_image(pil_img):
#     serials = []
#
#     # Convert PIL image to OpenCV format
#     image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.equalizeHist(gray)
#
#     # Optional: Resize image to improve detection
#     scale_percent = 150
#     width = int(gray.shape[1] * scale_percent / 100)
#     height = int(gray.shape[0] * scale_percent / 100)
#     gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LINEAR)
#
#     # Decode barcodes from image
#     barcodes = decode(gray, symbols=[ZBarSymbol.CODE128, ZBarSymbol.QRCODE, ZBarSymbol.EAN13, ZBarSymbol.EAN8])
#     for barcode in barcodes:
#         data = barcode.data.decode('utf-8')
#         if data not in serials:
#             serials.append(data)
#
#     return serials

#
# views.py
import base64
import numpy as np
import cv2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyzbar import pyzbar
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
#
# @csrf_exempt
# def extract_barcodes(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     if file.name.lower().endswith('.pdf'):
#         pages = convert_from_bytes(file.read())
#         for page in pages:
#             img = page.convert('RGB')
#             serials += extract_barcodes_from_image(img)
#     else:
#         image_data = file.read()
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
#         nparr = np.frombuffer(image_data, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         serials += extract_barcodes_from_cv2_image(img)
#
#     return JsonResponse({'serials': list(set(serials))[:100]})

import base64
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from pdf2image import convert_from_bytes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyzbar import pyzbar
from pdf2image import convert_from_bytes
import numpy as np
import cv2

# @csrf_exempt
# def extract_barcodes(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         serials = []
#
#         file_ext = file.name.lower().split('.')[-1]
#         file_data = file.read()
#
#         def process_image_data(image_data):
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             # ✅ Use your print-enabled function
#             return extract_barcodes_from_cv2_image(img)
#
#         try:
#             if file_ext in ['jpg', 'jpeg', 'png']:
#                 serials = process_image_data(file_data)
#
#             elif file_ext == 'pdf':
#                 images = convert_from_bytes(file_data)
#                 for image in images:
#                     open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#                     # ✅ Use your print-enabled function
#                     serials.extend(extract_barcodes_from_cv2_image(open_cv_image))
#
#             return JsonResponse({'serials': serials})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)

#-----------------------------------------FInal below _________________________
# Used for Poppler
# @csrf_exempt
# def extract_barcodes(request):
#     if request.method == 'POST' and request.FILES.getlist('files'):
#         serials = []
#         for file in request.FILES.getlist('files'):
#             try:
#                 file_ext = file.name.lower().split('.')[-1]
#                 file_data = file.read()
#
#                 def process_image_data(image_data):
#                     nparr = np.frombuffer(image_data, np.uint8)
#                     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                     return extract_barcodes_from_cv2_image(img)
#
#                 if file_ext in ['jpg', 'jpeg', 'png']:
#                     serials.extend(process_image_data(file_data))
#
#                 elif file_ext == 'pdf':
#                     images = convert_from_bytes(file_data)
#                     for image in images:
#                         open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#                         serials.extend(extract_barcodes_from_cv2_image(open_cv_image))
#
#             except Exception as e:
#                 continue  # Skip problematic files
#             serials = list(OrderedDict.fromkeys(serials))
#         return JsonResponse({'serials': serials})
#         # return JsonResponse({'serials': list(set(serials))})
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#
#
#
# def extract_barcodes_from_image(pil_img):
#     img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
#     return extract_barcodes_from_cv2_image(img_cv)
#
# def extract_barcodes_from_cv2_image(img_cv):
#     serials = []
#     barcodes = pyzbar.decode(img_cv)
#     print("Found barcodes:", len(barcodes))  # ✅ This will print even if 0
#     if barcodes:
#         for barcode in barcodes:
#             barcode_data = barcode.data.decode('utf-8')
#             print("Detected barcode:", barcode_data)  # ✅ Will now show
#             serials.append(barcode_data)
#     return serials

# @csrf_exempt
# def extract_serial_text(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     if file.name.lower().endswith('.pdf'):
#         pages = convert_from_bytes(file.read())
#         for page in pages:
#             img = page.convert('RGB')
#             serials += extract_text_from_image(img)
#     else:
#         image = Image.open(file).convert('RGB')
#         serials += extract_text_from_image(image)
#
#     return JsonResponse({'serials': list(set(serials))[:100]})
# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#     for file in request.FILES.getlist('files'):
#         try:
#             if file.name.lower().endswith('.pdf'):
#                 pages = convert_from_bytes(file.read())
#                 for page in pages:
#                     img = page.convert('RGB')
#                     serials += extract_text_from_image(img)
#             else:
#                 from PIL import Image
#                 image = Image.open(file).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             continue
#
#      # return JsonResponse({'serials': list(set(serials))[:100]})
#         serials = list(OrderedDict.fromkeys(serials))[:100]
#     return JsonResponse({'serials': serials})
#
# def extract_text_from_image(pil_img):
#     serials = []
#     text = pytesseract.image_to_string(pil_img)
#     lines = text.splitlines()
#     for line in lines:
#         clean = line.strip()
#         if clean and clean not in serials:
#             serials.append(clean)
#     return serials

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageFilter, ImageOps
from pdf2image import convert_from_bytes
from collections import OrderedDict
import pytesseract
import re
#
# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#     for file in request.FILES.getlist('files'):
#         try:
#             if file.name.lower().endswith('.pdf'):
#                 pages = convert_from_bytes(file.read())
#                 for page in pages:
#                     img = page.convert('RGB')
#                     serials += extract_text_from_image(img)
#             else:
#                 image = Image.open(file).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             print("Error:", str(e))  # better than silent fail
#             continue
#
#     # Deduplicate while preserving order
#     serials = list(OrderedDict.fromkeys(serials))[:100]
#     return JsonResponse({'serials': serials})
#
# def extract_text_from_image(pil_img):
#     serials = []
#
#     # === Image Preprocessing ===
#     gray = pil_img.convert('L')  # Convert to grayscale
#     enhanced = ImageOps.autocontrast(gray)  # Improve contrast
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpen image
#     # You can also try binary thresholding here if needed
#
#     # === OCR ===
#     text = pytesseract.image_to_string(sharpened)
#
#     # === Extract serials using regex ===
#     pattern = re.compile(r'WS\d{14}')  # Match strings like WS03259045765532
#     matches = pattern.findall(text)
#
#     return matches
# ____________________________________end ______________________________________________________

# used PyMuPDF
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
import numpy as np
import cv2
from pyzbar import pyzbar
import fitz  # PyMuPDF
from PIL import Image
import io

# @csrf_exempt
# def extract_barcodes(request):
#     if request.method == 'POST' and request.FILES.getlist('files'):
#         serials = []
#
#         for file in request.FILES.getlist('files'):
#             try:
#                 file_ext = file.name.lower().split('.')[-1]
#                 file_data = file.read()
#
#                 def process_image_data(image_data):
#                     nparr = np.frombuffer(image_data, np.uint8)
#                     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#                     return extract_barcodes_from_cv2_image(img)
#
#                 if file_ext in ['jpg', 'jpeg', 'png']:
#                     serials.extend(process_image_data(file_data))
#
#                 elif file_ext == 'pdf':
#                     images = convert_pdf_to_images(file_data)
#                     for image in images:
#                         img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#                         serials.extend(extract_barcodes_from_cv2_image(img_cv))
#
#             except Exception as e:
#                 print("Error processing file:", e)
#                 continue  # Skip problematic files
#
#         serials = list(OrderedDict.fromkeys(serials))
#         return JsonResponse({'serials': serials})
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#
#
# def convert_pdf_to_images(pdf_bytes):
#     doc = fitz.Document(stream=pdf_bytes, filetype="pdf")
#     images = []
#     for page in doc:
#         pix = page.get_pixmap(dpi=300)
#         img = Image.open(io.BytesIO(pix.tobytes("png")))
#         images.append(img)
#     return images
#
#
# def extract_barcodes_from_image(pil_img):
#     img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
#     return extract_barcodes_from_cv2_image(img_cv)
#
#
# def extract_barcodes_from_cv2_image(img_cv):
#     serials = []
#     barcodes = pyzbar.decode(img_cv)
#     print("Found barcodes:", len(barcodes))
#     for barcode in barcodes:
#         barcode_data = barcode.data.decode('utf-8')
#         print("Detected barcode:", barcode_data)
#         serials.append(barcode_data)
#     return serials
# #
# #
# # @csrf_exempt
# # def extract_serial_text(request):
# #     if not request.FILES.getlist('files'):
# #         return JsonResponse({'error': 'No file uploaded'}, status=400)
# #
# #     serials = []
# #
# #     for file in request.FILES.getlist('files'):
# #         try:
# #             if file.name.lower().endswith('.pdf'):
# #                 pages = convert_pdf_to_images(file.read())
# #                 for page in pages:
# #                     serials += extract_text_from_image(page)
# #             else:
# #                 image = Image.open(file).convert('RGB')
# #                 serials += extract_text_from_image(image)
# #         except Exception as e:
# #             print("Error:", str(e))
# #             continue
# #
# #     # Deduplicate while preserving order, limit to 100
# #     serials = list(OrderedDict.fromkeys(serials))[:100]
# #
# #     return JsonResponse({'serials': serials})
# #
# #
# # def extract_text_from_image(pil_img):
# #     # === Image Preprocessing ===
# #     gray = pil_img.convert('L')  # Grayscale
# #     enhanced = ImageOps.autocontrast(gray)  # Better contrast
# #     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpened image
# #
# #     # === OCR with config ===
# #     custom_config = r'--oem 3 --psm 6'
# #     text = pytesseract.image_to_string(sharpened, config=custom_config)
# #
# #     # === Extract serials using strict regex ===
# #     pattern = re.compile(r'\bWS\d{14}\b')  # Match: WS + 14 digits
# #     matches = pattern.findall(text)
# #
# #     return matches
# #
# #
# # def convert_pdf_to_images(pdf_bytes):
# #     doc = fitz.open(stream=pdf_bytes, filetype="pdf")
# #     images = []
# #     for page in doc:
# #         pix = page.get_pixmap(dpi=300)
# #         img = Image.open(io.BytesIO(pix.tobytes("png")))
# #         images.append(img)
# #     return images
#
# # from django.views.decorators.csrf import csrf_exempt
# # from django.http import JsonResponse
# # from PIL import Image
# # import re
# # import fitz  # PyMuPDF
# # import io
# # from collections import OrderedDict
# #
# # @csrf_exempt
# # def extract_serial_text(request):
# #     if not request.FILES.getlist('files'):
# #         return JsonResponse({'error': 'No file uploaded'}, status=400)
# #
# #     serials = []
# #
# #     for file in request.FILES.getlist('files'):
# #         try:
# #             if file.name.lower().endswith('.pdf'):
# #                 pdf_bytes = file.read()
# #                 serials += extract_serial_numbers_from_pdf(pdf_bytes)
# #             else:
# #                 image = Image.open(file).convert('RGB')
# #                 serials += extract_text_from_image(image)
# #         except Exception as e:
# #             print("Error:", str(e))
# #             continue
# #
# #     # Deduplicate while preserving order, limit to 100
# #     serials = list(OrderedDict.fromkeys(serials))[:100]
# #
# #     return JsonResponse({'serials': serials})
# #
# #
# # def extract_serial_numbers_from_pdf(pdf_bytes):
# #     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
# #     serial_numbers = []
# #
# #     for page in pdf_document:
# #         text = page.get_text()
# #         matches = re.findall(r'\b[A-Z0-9]{6,}\b', text)  # Adjust regex if needed
# #         serial_numbers.extend(matches)
# #
# #     return serial_numbers
# #
# #
# # def extract_text_from_image(pil_img):
# #     from PIL import ImageOps, ImageFilter
# #     import pytesseract
# #
# #     gray = pil_img.convert('L')  # Grayscale
# #     enhanced = ImageOps.autocontrast(gray)  # Better contrast
# #     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpen image
# #
# #     custom_config = r'--oem 3 --psm 6'
# #     text = pytesseract.image_to_string(sharpened, config=custom_config)
# #
# #     pattern = re.compile(r'\bWS\d{14}\b')  # Match: WS + 14 digits
# #     matches = pattern.findall(text)
# #
# #     return matches
#
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from PIL import Image, ImageOps, ImageFilter
# import pytesseract
# import re
# import fitz  # PyMuPDF
# import io
# from collections import OrderedDict
#
# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     for file in request.FILES.getlist('files'):
#         try:
#             if file.name.lower().endswith('.pdf'):
#                 pdf_bytes = file.read()
#                 serials += extract_serial_numbers_from_pdf(pdf_bytes)
#             else:
#                 image = Image.open(file).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             print("Error:", str(e))
#             continue
#
#     # Deduplicate while preserving order, limit to 100
#     serials = list(OrderedDict.fromkeys(serials))[:100]
#
#     return JsonResponse({'serials': serials})
#
#
# def extract_serial_numbers_from_pdf(pdf_bytes):
#     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
#     serial_numbers = []
#
#     for page in pdf_document:
#         text = page.get_text()
#
#         # Apply line splitting and filtering
#         lines = [line.strip() for line in text.splitlines() if line.strip()]
#
#         # Apply regex on each line
#         for line in lines:
#             matches = re.findall(r'\b[A-Z0-9]{6,}\b', line)  # Adjust this regex as needed
#             serial_numbers.extend(matches)
#
#     return serial_numbers
#
#
# def extract_text_from_image(pil_img):
#     # === Image Preprocessing ===
#     gray = pil_img.convert('L')  # Grayscale
#     enhanced = ImageOps.autocontrast(gray)  # Better contrast
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpened image
#
#     # === OCR with config ===
#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)
#
#     # === Extract serials using strict regex ===
#     pattern = re.compile(r'\bWS\d{14}\b')  # Match: WS + 14 digits
#     matches = pattern.findall(text)
#
#     return matches

# used PyMuPDF
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
import numpy as np
import cv2
from pyzbar import pyzbar
import fitz  # PyMuPDF
from PIL import Image
import io

@csrf_exempt
def extract_barcodes(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        serials = []

        for file in request.FILES.getlist('files'):
            try:
                file_ext = file.name.lower().split('.')[-1]
                file_data = file.read()

                def process_image_data(image_data):
                    nparr = np.frombuffer(image_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    return extract_barcodes_from_cv2_image(img)

                if file_ext in ['jpg', 'jpeg', 'png']:
                    serials.extend(process_image_data(file_data))

                elif file_ext == 'pdf':
                    images = convert_pdf_to_images(file_data)
                    for image in images:
                        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        serials.extend(extract_barcodes_from_cv2_image(img_cv))

            except Exception as e:
                print("Error processing file:", e)
                continue  # Skip problematic files

        serials = list(OrderedDict.fromkeys(serials))
        return JsonResponse({'serials': serials})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def convert_pdf_to_images(pdf_bytes):
    doc = fitz.Document(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images


def extract_barcodes_from_image(pil_img):
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return extract_barcodes_from_cv2_image(img_cv)


def extract_barcodes_from_cv2_image(img_cv):
    serials = []
    barcodes = pyzbar.decode(img_cv)
    print("Found barcodes:", len(barcodes))
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        print("Detected barcode:", barcode_data)
        serials.append(barcode_data)
    return serials


# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)

#     serials = []

#     for file in request.FILES.getlist('files'):
#         try:
#             if file.name.lower().endswith('.pdf'):
#                 pages = convert_pdf_to_images(file.read())
#                 for page in pages:
#                     serials += extract_text_from_image(page)
#             else:
#                 image = Image.open(file).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             print("Error:", str(e))
#             continue

#     # Deduplicate while preserving order, limit to 100
#     serials = list(OrderedDict.fromkeys(serials))[:100]

#     return JsonResponse({'serials': serials})


# def extract_text_from_image(pil_img):
#     # === Image Preprocessing ===
#     gray = pil_img.convert('L')  # Grayscale
#     enhanced = ImageOps.autocontrast(gray)  # Better contrast
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpened image

#     # === OCR with config ===
#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)

#     # === Extract serials using strict regex ===
#     pattern = re.compile(r'\bWS\d{14}\b')  # Match: WS + 14 digits
#     matches = pattern.findall(text)

#     return matches


# def convert_pdf_to_images(pdf_bytes):
#     doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#     images = []
#     for page in doc:
#         pix = page.get_pixmap(dpi=300)
#         img = Image.open(io.BytesIO(pix.tobytes("png")))
#         images.append(img)
#     return images


# from PIL import ImageOps, ImageFilter
# import pytesseract
# import re
# from collections import OrderedDict
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import fitz  # pymupdf
# import io

# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)

#     serials = []

#     for file in request.FILES.getlist('files'):
#         try:
#             file_data = file.read()
#             if file.name.lower().endswith('.pdf'):
#                 # 🔧 Reduce DPI & limit pages
#                 pages = convert_pdf_to_images(file_data, dpi=150, max_pages=3)
#                 for page in pages:
#                     serials += extract_text_from_image(page)
#             else:
#                 image = Image.open(io.BytesIO(file_data)).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             import traceback
#             print("Error:", str(e))
#             print(traceback.format_exc())
#             continue

#     serials = list(OrderedDict.fromkeys(serials))[:100]
#     return JsonResponse({'serials': serials})

# def convert_pdf_to_images(pdf_bytes, dpi=150, max_pages=3):
#     doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#     images = []
#     for i, page in enumerate(doc):
#         if i >= max_pages:
#             break
#         pix = page.get_pixmap(dpi=dpi)
#         img = Image.open(io.BytesIO(pix.tobytes("png")))
#         images.append(img)
#     return images

# def extract_text_from_image(pil_img):
#     # Preprocessing
#     gray = pil_img.convert('L')
#     enhanced = ImageOps.autocontrast(gray)
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)

#     # OCR
#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)

#     # Extract serials
#     pattern = re.compile(r'\bWS\d{14}\b')  # Adjust pattern as needed
#     matches = pattern.findall(text)
#     return matches

# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from PIL import Image, ImageOps, ImageFilter
# import pytesseract
# import re
# import fitz  # PyMuPDF
# import io
# from collections import OrderedDict

# @csrf_exempt
# def extract_serial_text(request):
#     if not request.FILES.getlist('files'):
#         return JsonResponse({'error': 'No file uploaded'}, status=400)

#     serials = []

#     for file in request.FILES.getlist('files'):
#         try:
#             if file.name.lower().endswith('.pdf'):
#                 pdf_bytes = file.read()
#                 serials += extract_serial_numbers_from_pdf(pdf_bytes)
#             else:
#                 image = Image.open(file).convert('RGB')
#                 serials += extract_text_from_image(image)
#         except Exception as e:
#             print("Error:", str(e))
#             continue

#     # Deduplicate while preserving order, limit to 100
#     serials = list(OrderedDict.fromkeys(serials))[:100]

#     return JsonResponse({'serials': serials})


# def extract_serial_numbers_from_pdf(pdf_bytes):
#     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
#     serial_numbers = []

#     for page in pdf_document:
#         text = page.get_text()

#         # Apply line splitting and filtering
#         lines = [line.strip() for line in text.splitlines() if line.strip()]

#         # Apply regex on each line
#         for line in lines:
#             matches = re.findall(r'\b[A-Z0-9]{6,}\b', line)  # Adjust this regex as needed
#             serial_numbers.extend(matches)

#     return serial_numbers


# def extract_text_from_image(pil_img):
#     # === Image Preprocessing ===
#     gray = pil_img.convert('L')  # Grayscale
#     enhanced = ImageOps.autocontrast(gray)  # Better contrast
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)  # Sharpened image

#     # === OCR with config ===
#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)

#     # === Extract serials using strict regex ===
#     pattern = re.compile(r'\bWS\d{14}\b')  # Match: WS + 14 digits
#     matches = pattern.findall(text)

#     return matches


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import re
import fitz  # PyMuPDF
import io
from collections import OrderedDict


@csrf_exempt
def extract_serial_text(request):
    if not request.FILES.getlist('files'):
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    serials = []

    for file in request.FILES.getlist('files'):
        try:
            if file.name.lower().endswith('.pdf'):
                pdf_bytes = file.read()
                serials += extract_serial_numbers_from_pdf(pdf_bytes)
            else:
                image = Image.open(file).convert('RGB')
                serials += extract_serial_numbers_from_image(image)
        except Exception as e:
            print("Error:", str(e))
            continue

    # Deduplicate while preserving order, limit to 100
    serials = list(OrderedDict.fromkeys(serials))[::]

    return JsonResponse({'serials': serials})


# def extract_serial_numbers_from_pdf(pdf_bytes, chunk_size=10):
#     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
#     matches = []

#     patterns = get_serial_patterns()
#     total_pages = pdf_document.page_count

#     for i in range(0, total_pages, chunk_size):
#         chunk_end = min(i + chunk_size, total_pages)
#         for page_num in range(i, chunk_end):
#             page = pdf_document.load_page(page_num)
#             text = page.get_text()
#             words = [w.strip() for w in text.split() if w.strip()]

#             for word in words:
#                 for pattern, dtype in patterns:
#                     if re.fullmatch(pattern, word):
#                         if dtype == 'numeric' and word.isdigit():
#                             matches.append(word)
#                         elif dtype == 'alphanumeric':
#                             matches.append(word)
#                         break
#     return matches


# def extract_serial_numbers_from_image(pil_img):
#     gray = pil_img.convert('L')
#     enhanced = ImageOps.autocontrast(gray)
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)

#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)
#     words = [w.strip() for w in text.split() if w.strip()]

#     matches = []
#     patterns = get_serial_patterns()

#     for word in words:
#         for pattern, dtype in patterns:
#             if re.fullmatch(pattern, word):
#                 if dtype == 'numeric' and word.isdigit():
#                     matches.append(word)
#                 elif dtype == 'alphanumeric':
#                     matches.append(word)
#                 break
#     return matches

# def extract_serial_numbers_from_pdf(pdf_bytes, chunk_size=10):
#     pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
#     matches = []

#     patterns = get_serial_patterns()
#     total_pages = pdf_document.page_count

#     for i in range(0, total_pages, chunk_size):
#         chunk_end = min(i + chunk_size, total_pages)
#         for page_num in range(i, chunk_end):
#             page = pdf_document.load_page(page_num)

#             # Extract blocks with coordinates: (x0, y0, x1, y1, "text", block_no, block_type)
#             blocks = page.get_text("blocks")

#             # Sort blocks top-down, then left-right
#             blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))  # y, x sorting

#             words = []
#             for block in blocks:
#                 block_text = block[4]
#                 for line in block_text.splitlines():
#                     line_words = [w.replace(" ", "").strip() for w in line.split() if w.strip()]
#                     words.extend(line_words)

#             for word in words:
#                 for pattern, dtype in patterns:
#                     if re.fullmatch(pattern, word):
#                         if dtype == 'numeric' and word.isdigit():
#                             matches.append(word)
#                         elif dtype == 'alphanumeric':
#                             matches.append(word)
#                         break

#     return matches


# def extract_serial_numbers_from_image(pil_img):
#     gray = pil_img.convert('L')
#     enhanced = ImageOps.autocontrast(gray)
#     sharpened = enhanced.filter(ImageFilter.SHARPEN)

#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(sharpened, config=custom_config)

#     words = [w.replace(" ", "").strip().upper() for w in text.split() if w.strip()]
#     corrected_words = [correct_ocr_errors(word) for word in words]

#     matches = []
#     patterns = get_serial_patterns()

#     for word in corrected_words:
#         for pattern, dtype in patterns:
#             if re.fullmatch(pattern, word):
#                 if dtype == 'numeric' and word.isdigit():
#                     matches.append(word)
#                 elif dtype == 'alphanumeric':
#                     matches.append(word)
#                 break
#     return matches


def extract_serial_numbers_from_pdf(pdf_bytes, chunk_size=10):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    matches = []

    patterns = get_serial_patterns()
    total_pages = pdf_document.page_count

    for i in range(0, total_pages, chunk_size):
        chunk_end = min(i + chunk_size, total_pages)
        for page_num in range(i, chunk_end):
            page = pdf_document.load_page(page_num)
            blocks = page.get_text("blocks")

            # Sort by Y (top-down) and X (left-right)
            blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))

            words = []

            print(f"Page {page_num + 1} blocks:")
            for block in blocks:
                print(block[4])

                block_text = block[4]
                for line in block_text.splitlines():
                    # line_words = [w.replace(" ", "").strip() for w in line.split() if w.strip()]
                    line_clean = re.sub(r"[^\w/\\-]", " ", line)  # Replace special chars with space
                    line_words = [w.strip() for w in line_clean.split() if w.strip()]

                    words.extend(line_words)

            for word in words:
                word = word.upper()  # Convert to uppercase for consistent matching
                for pattern, dtype in patterns:
                    if re.fullmatch(pattern, word):
                        if dtype == 'numeric' and word.isdigit():
                            matches.append(word)
                        elif dtype == 'alphanumeric':
                            matches.append(word)
                        break

    return matches


def extract_serial_numbers_from_image(pil_img):
    gray = pil_img.convert('L')
    enhanced = ImageOps.autocontrast(gray)
    sharpened = enhanced.filter(ImageFilter.SHARPEN)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(sharpened, config=custom_config)
    words = [w.replace(" ", "").strip() for w in text.split() if w.strip()]

    matches = []
    patterns = get_serial_patterns()

    for word in words:
        word = word.upper()  # Normalize
        for pattern, dtype in patterns:
            if re.fullmatch(pattern, word):
                if dtype == 'numeric' and word.isdigit():
                    matches.append(word)
                elif dtype == 'alphanumeric':
                    matches.append(word)
                break
    return matches



def get_serial_patterns():
    """
    Returns a list of (regex_pattern, datatype) tuples for serial number formats.
    """
    return [
        (r'WS\d{14}', 'alphanumeric'),
        (r'WSO\d{13}', 'alphanumeric'),
        (r'ICON[A-Z0-9]{10,}', 'alphanumeric'),  # <-- Add this line
        (r'NSM\d{12}', 'alphanumeric'),
        (r'63XXE123J\d{15,}', 'alphanumeric'),
        (r'CGP\d{11,13}', 'alphanumeric'),
        (r'ME\d{10,13}', 'alphanumeric'),
        (r'KSY[A-Z0-9]{8,}', 'alphanumeric'),
        (r'\d{6,}', 'numeric'),
        (r'A\d{7,}', 'alphanumeric'),
        (r'PET/RI/\d{4}', 'alphanumeric'),
        (r'M-\d{2}/\d{4}', 'alphanumeric'),
        (r'JA\d{5,}', 'alphanumeric'),
        (r'CJJMEZS\d+', 'alphanumeric'),
        (r'LBLGE\d+', 'alphanumeric'),
        (r'\d{15,}', 'numeric'),
        (r'U\d+', 'alphanumeric'),
    ]



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PurchaseSerial  # Change this to your actual app name

@csrf_exempt
def check_duplicate_serials(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serials = data.get("serials", [])
            stock_id = data.get('stock_id')
            # print("stock", stock_id)
            duplicates = set(PurchaseSerial.objects.filter(stock_id=stock_id, serialNo__in=serials).values_list("serialNo", flat=True))

            return JsonResponse({'duplicates': list(duplicates)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)


# views.py
import base64
import numpy as np
import cv2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyzbar import pyzbar
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

@csrf_exempt
def extract_serials(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    serials = []

    if file.name.lower().endswith('.pdf'):
        pages = convert_from_bytes(file.read())
        for page in pages:
            img = page.convert('RGB')
            serials += extract_from_image(img)
    else:
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Detect barcodes
        barcodes = pyzbar.decode(img)
        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                if barcode_data not in serials:
                    serials.append(barcode_data)

        # OCR fallback for serial numbers
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        text = pytesseract.image_to_string(pil_img)
        lines = text.splitlines()
        for line in lines:
            clean = line.strip()
            if clean and clean not in serials:
                serials.append(clean)

    return JsonResponse({'serials': list(set(serials))[:100]})

def extract_from_image(pil_img):
    image_data = pil_img.tobytes()
    nparr = np.frombuffer(image_data, np.uint8)
    img = np.array(pil_img)

    serials = []

    # Detect barcodes
    barcodes = pyzbar.decode(img)
    if barcodes:
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            if barcode_data not in serials:
                serials.append(barcode_data)

    # OCR fallback for serial numbers
    text = pytesseract.image_to_string(pil_img)
    lines = text.splitlines()
    for line in lines:
        clean = line.strip()
        if clean and clean not in serials:
            serials.append(clean)

    return serials



# # views.py
# import cv2
# import numpy as np
# import base64
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from PIL import Image
# from pdf2image import convert_from_bytes
# from pyzbar import pyzbar
# from io import BytesIO
#
# @csrf_exempt
# def extract_barcode_data(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#
#     serials = []
#
#     try:
#         if file.name.lower().endswith('.pdf'):
#             # Convert PDF to images
#             pages = convert_from_bytes(file.read(), dpi=300)
#             for page in pages:
#                 serials += extract_from_image(page)
#         else:
#             serials += extract_from_file(file)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'serials': list(set(serials))[:100]})
#
# def extract_from_file(image):
#     serials = []
#     image_data = image.read()
#     image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#     nparr = np.frombuffer(image_data, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#     barcodes = pyzbar.decode(img)
#     if barcodes:
#         for barcode in barcodes:
#             barcode_data = barcode.data.decode('utf-8')
#             if barcode_data not in serials:
#                 serials.append(barcode_data)
#
#     return serials
#
# def extract_from_image(pil_img):
#     buffered = BytesIO()
#     pil_img.save(buffered, format="JPEG")
#     buffered.seek(0)
#     return extract_from_file(buffered)



#
# from django.db import transaction
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# # from .models import PurchaseBill, PurchaseBillDetails, Stock
# import logging
#
# logger = logging.getLogger(__name__)
#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     total_amount = 0  # This will store the total of all items
#                     total_gst_amount = 0
#                     unique_gst_values = set()  # To keep track of unique GST values
#
#                     # Save each PurchaseItem and update Stock
#                     for form in formset:
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Get the associated stock
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#
#                         # Calculate the total price for the item
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#                         total_amount += billitem.totalprice  # Add to total amount
#
#                         # Update stock quantity
#                         stock.quantity += billitem.quantity
#                         stock.save()
#                         logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                         # Save the PurchaseItem
#                         billitem.save()
#                         logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#
#                     # Handle multiple gst_values
#                     gst_values = request.POST.getlist('gst_value')  # Fetch all gst_values
#                     for gst_value_str in gst_values:
#                         # Split by commas and clean up each value
#                         for gst_value in gst_value_str.split(','):
#                             gst_value = gst_value.replace('%', '').strip()  # Remove % and trim whitespace
#                             if gst_value:  # Only process non-empty strings
#                                 try:
#                                     unique_gst_values.add(float(gst_value))  # Add to set to ensure uniqueness
#                                 except ValueError:
#                                     logger.error(f"Invalid gst_value provided: {gst_value}")
#                                     messages.error(request,
#                                                    f"Invalid GST value provided: {gst_value}. Please check your input.")
#
#                     # Calculate total GST amount based on a single unique average GST value
#                     if unique_gst_values:
#                         # Calculate the average GST value
#                         avg_gst_value = sum(unique_gst_values) / len(unique_gst_values)
#                         total_gst_amount = (avg_gst_value / 100) * total_amount
#
#                     # Calculate final amount
#                     final_amount = total_amount + total_gst_amount
#
#                     # Save PurchaseBillDetails with total GST and final_amount
#                     billdetailsobj = PurchaseBillDetails(
#                         billno=billobj,
#                         gst_value=', '.join(map(str, unique_gst_values)),  # Store the unique GST values as string
#                         gst_amount=total_gst_amount,
#                         final_amount=final_amount
#                     )
#                     billdetailsobj.save()
#                     logger.info("PurchaseBillDetails saved successfully with GST")
#
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('purchase-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)

    # def post(self, request, pk):
    #     formset = PurchaseItemFormset(request.POST)
    #     supplierobj = get_object_or_404(Supplier, pk=pk)
    #
    #     if formset.is_valid():
    #         try:
    #             with transaction.atomic():
    #                 # Save PurchaseBill
    #                 billobj = PurchaseBill(supplier=supplierobj)
    #                 billobj.save()
    #                 logger.info("PurchaseBill saved successfully")
    #
    #                 total_amount = 0  # This will store the total of all items
    #                 total_gst_amount = 0
    #                 unique_gst_values = set()  # To keep track of unique GST values
    #
    #                 # Save each PurchaseItem and update Stock
    #                 for form in formset:
    #                     billitem = form.save(commit=False)
    #                     billitem.billno = billobj
    #
    #                     # Get the associated stock
    #                     stock = get_object_or_404(Stock, pk=billitem.stock.id)
    #
    #                     # Calculate the total price for the item
    #                     billitem.totalprice = billitem.perprice * billitem.quantity
    #                     total_amount += billitem.totalprice  # Add to total amount
    #
    #                     # Update stock quantity
    #                     stock.quantity += billitem.quantity
    #                     stock.save()
    #                     logger.info(f"Stock updated successfully for stock id {stock.id}")
    #
    #                     # Save the PurchaseItem
    #                     billitem.save()
    #                     logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
    #
    #                 # Check if the GST toggle is enabled
    #                 gstToggle = request.POST.get('gstToggle') == 'on'  # Check if toggle is enabled
    #
    #                 if gstToggle:
    #                     # Handle multiple gst_values
    #                     gst_values = request.POST.getlist('gst_value')  # Fetch all gst_values
    #                     for gst_value_str in gst_values:
    #                         # Split by commas and clean up each value
    #                         for gst_value in gst_value_str.split(','):
    #                             gst_value = gst_value.replace('%', '').strip()  # Remove % and trim whitespace
    #                             if gst_value:  # Only process non-empty strings
    #                                 try:
    #                                     unique_gst_values.add(float(gst_value))  # Add to set to ensure uniqueness
    #                                 except ValueError:
    #                                     logger.error(f"Invalid gst_value provided: {gst_value}")
    #                                     messages.error(request,
    #                                                    f"Invalid GST value provided: {gst_value}. Please check your input.")
    #
    #                     # Calculate total GST amount based on a single unique average GST value
    #                     if unique_gst_values:
    #                         avg_gst_value = sum(unique_gst_values) / len(unique_gst_values)
    #                         total_gst_amount = (avg_gst_value / 100) * total_amount
    #
    #                     # Save PurchaseBillDetails with total GST and final_amount
    #                     final_amount = total_amount + total_gst_amount
    #                     billdetailsobj = PurchaseBillDetails(
    #                         billno=billobj,
    #                         gst_value=', '.join(map(str, unique_gst_values)),  # Store the unique GST values as string
    #                         gst_amount=total_gst_amount,
    #                         final_amount=final_amount
    #                     )
    #                 else:
    #                     # If GST is not enabled, store default values
    #                     billdetailsobj = PurchaseBillDetails(
    #                         billno=billobj,
    #                         gst_value='0',  # Default GST value
    #                         gst_amount=0,  # Default GST amount
    #                         final_amount=total_amount  # Only total amount without GST
    #                     )
    #
    #                 billdetailsobj.save()
    #                 logger.info("PurchaseBillDetails saved successfully with GST")
    #
    #                 messages.success(request, "Purchased items have been registered successfully")
    #                 return redirect('purchase-bill', billno=billobj.billno)
    #
    #         except Exception as e:
    #             logger.error(f"An error occurred: {str(e)}")
    #             messages.error(request, f"An error occurred: {str(e)}")
    #     else:
    #         logger.warning(f"Formset is not valid: {formset.errors}")
    #         messages.error(request, "There were errors in the form. Please correct them.")
    #
    #     # If form is not valid or any other error occurs
    #     context = {
    #         'formset': formset,
    #         'supplier': supplierobj,
    #         'stock_list': Stock.objects.filter(is_deleted=False),
    #         'categories': Category.objects.all(),
    #     }
    #     return render(request, self.template_name, context)


# def get_stock_quantity(request):
#     stock_id = request.GET.get('stock_id')
#     stock = Stock.objects.get(pk=stock_id)
#     return JsonResponse({'quantity': stock.quantity})

def get_stock_quantity(request):
    stock_id = request.GET.get('stock_id')
    stock = Stock.objects.get(pk=stock_id)
    return JsonResponse({
        'quantity': stock.quantity,
        'stock_alert': stock.stock_alert,
        'gst': stock.gst,
        'purchase': stock.purchase.short_name,
        'purchase_id': stock.purchase.id,
    })


#
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Product, Stock, PurchaseBill, PurchaseBillDetail
# from .forms import PurchaseBillForm, PurchaseBillDetailFormSet
#
# def PurchaseCreateView(request, supplier_id):
#     supplier = get_object_or_404(Supplier, id=supplier_id)
#     product_list = Product.objects.all()
#
#     if request.method == 'POST':
#         formset = PurchaseItemFormset(request.POST)
#         if formset.is_valid():
#             bill = PurchaseBill.objects.create(supplier=supplier)
#             for form in formset:
#                 product = form.cleaned_data.get('product')
#                 quantity = form.cleaned_data.get('quantity')
#                 perprice = form.cleaned_data.get('perprice')
#                 if product and quantity and perprice:
#                     # Create or update Stock
#                     stock, created = Stock.objects.get_or_create(name=product.name)
#                     stock.quantity += quantity
#                     stock.save()
#
#                     # Create PurchaseBillDetail
#                     PurchaseBillDetail.objects.create(
#                         bill=bill,
#                         product=product,
#                         quantity=quantity,
#                         perprice=perprice,
#                         total_price=quantity * perprice
#                     )
#             return redirect('some-view-name')  # Update with the appropriate redirect
#     else:
#         formset = PurchaseDetailsForm(queryset=PurchaseBillDetail.objects.none())
#
#     context = {
#         'supplier': supplier,
#         'formset': formset,
#         'product_list': product_list,
#     }
#     return render(request, 'purchases/new_sale.html', context)
# Set up logger


# logger = logging.getLogger(__name__)
#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
    # def get(self, request, pk):
    #     formset = PurchaseItemFormset()
    #     supplierobj = get_object_or_404(Supplier, pk=pk)
    #     context = {
    #         'formset': formset,
    #         'supplier': supplierobj,
    #         # 'stock_list': Stock.objects.filter(is_deleted=False),
    #         'product_list': Product.objects.filter(status=1),
    #     }
    #     return render(request, self.template_name, context)

#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     # Save PurchaseBillDetails
#                     purchase_details_form = PurchaseDetailsForm(request.POST)
#                     if purchase_details_form.is_valid():
#                         billdetailsobj = purchase_details_form.save(commit=False)
#                         billdetailsobj.billno = billobj
#                         billdetailsobj.save()
#                         logger.info("PurchaseBillDetails saved successfully")
#                     else:
#                         logger.warning(f"PurchaseDetailsForm is not valid: {purchase_details_form.errors}")
#                         raise ValueError("Purchase details form is not valid")
#
#                     # Save each PurchaseItem and update Stock
#                     for form in formset:
#                         if form.is_valid():
#                             billitem = form.save(commit=False)
#                             billitem.billno = billobj
#
#                             # Get or create stock
#                             stock, created = Stock.objects.get_or_create(id=billitem.stock.id, defaults={'name': billitem.stock.name})
#
#                             if created:
#                                 logger.info(f"New stock created: {stock.name}")
#                             else:
#                                 logger.info(f"Stock found: {stock.name}")
#
#                             # Calculate the total price for the item
#                             billitem.totalprice = billitem.perprice * billitem.quantity
#
#                             # Update stock quantity
#                             stock.quantity += billitem.quantity
#                             stock.save()
#                             logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                             # Save the PurchaseItem
#                             billitem.save()
#                             logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#                         else:
#                             logger.warning(f"PurchaseItemForm is not valid: {form.errors}")
#
#                     # If everything goes well
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('purchase-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#         }
#         return render(request, self.template_name, context)
#
# def get_stock_quantity(request):
#     product_id = request.GET.get('product_id')
#     stock = Stock.objects.filter(id=product_id).first()
#     quantity = stock.quantity if stock else 0
#     return JsonResponse({'quantity': quantity})


# from .forms import PurchaseItemFormset
# from .models import Supplier, PurchaseBill, PurchaseBillDetails, PurchaseItem, Stock
#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         stock_list = Stock.objects.filter(is_deleted=False)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': stock_list,
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#
#                     billdetailsobj = PurchaseBillDetails(billno=billobj)
#                     billdetailsobj.save()
#
#                     for form in formset:
#                         if form.cleaned_data:  # Ensure form is not empty
#                             billitem = form.save(commit=False)
#                             billitem.billno = billobj
#
#                             stock = get_object_or_404(Stock, pk=billitem.stock.id)
#                             billitem.totalprice = billitem.perprice * billitem.quantity
#
#                             stock.quantity -= billitem.quantity
#                             stock.save()
#
#                             billitem.save()
#
#                     return redirect('purchase-bill-list')
#
#             except Exception as e:
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             print("Formset is not valid")
#             print(formset.errors)  # Print formset errors to identify what’s wrong
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#         }
#         return render(request, self.template_name, context)

#
# from django.forms import formset_factory
# from django.shortcuts import get_object_or_404, render, redirect
# from django.views import View
# from django.db import transaction
# from django.contrib import messages
#
# from .models import Supplier, PurchaseBill, PurchaseBillDetails, PurchaseItem, Stock
# from .forms import PurchaseItemForm, PurchaseItemFormset
#
# class PurchaseCreateView(View):
#     template_name = 'purchases/new_sale.html'
#
#     def get(self, request, pk):
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         stock_list = Stock.objects.filter(is_deleted=False)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': stock_list,
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#
#                     # Save PurchaseBillDetails
#                     billdetailsobj = PurchaseBillDetails(billno=billobj)
#                     billdetailsobj.save()
#
#                     for form in formset:
#                         # Skip empty forms
#                         if not form.cleaned_data.get('stock') or not form.cleaned_data.get('quantity') or not form.cleaned_data.get('perprice'):
#                             continue
#
#                         # Save PurchaseItem and update Stock
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Update stock quantity
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#                         stock.quantity -= billitem.quantity
#                         stock.save()
#
#                         # Save PurchaseItem
#                         billitem.save()
#
#                     messages.success(request, "Purchase items saved successfully.")
#                     return redirect('purchase-bill-list')
#
#             except Exception as e:
#                 messages.error(request, f"An error occurred: {str(e)}")
#
#         else:
#             # If the formset is not valid
#             messages.error(request, "Please fill out all required fields correctly.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#         }
#         return render(request, self.template_name, context)



#
# # used to delete a bill object
# class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
#     model = PurchaseBill
#     template_name = "purchases/delete_purchase.html"
#     success_url = '/transactions/purchases'
#     def delete(self, *args, **kwargs):
#         self.object = self.get_object()
#         items = PurchaseItem.objects.filter(billno=self.object.billno)
#         for item in items:
#             stock = get_object_or_404(Stock, name=item.stock.name)
#             if stock.is_deleted == False:
#                 stock.quantity -= item.quantity
#                 stock.save()
#         messages.success(self.request, "Purchase bill has been deleted successfully")
#         return super(PurchaseDeleteView, self).delete(*args, **kwargs)



# class PurchaseDeleteView(LoginRequiredMixin, View):
#     template_name = "purchases/delete_purchase.html"
#     login_url = '/index/'
#
#     def get(self, request, *args, **kwargs):
#         # Render the confirmation page before deletion
#         purchase_bill = get_object_or_404(PurchaseBill, pk=kwargs['pk'])
#         return render(request, self.template_name, {'purchase_bill': purchase_bill})
#
#     def post(self, request, *args, **kwargs):
#         # Get the purchase bill object
#         purchase_bill = get_object_or_404(PurchaseBill, pk=kwargs['pk'])
#
#         # Get the related purchase items
#         purchase_items = PurchaseItem.objects.filter(billno=purchase_bill.billno)
#
#         # Update stock quantities before deleting the purchase bill
#         for item in purchase_items:
#             stock = Stock.objects.filter(id=item.stock.id, is_deleted=False).first()
#             if stock:
#                 stock.quantity -= item.quantity
#                 stock.save()
#
#         # Delete related purchase items
#         purchase_items.delete()
#
#         # Delete the purchase bill itself
#         purchase_bill.delete()
#
#         # Add a success message
#         messages.success(request, "Purchase bill has been deleted successfully")
#
#         # Redirect to the purchase list page
#         return redirect('/transactions/purchases')


class PurchaseDeleteView(LoginRequiredMixin, View):
    template_name = "purchases/delete_purchase.html"
    login_url = '/index/'

    def get(self, request, *args, **kwargs):
        # Calculate unread notifications count and retrieve notifications
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

        # Render the confirmation page before deletion
        purchase_bill = get_object_or_404(PurchaseBill, pk=kwargs['pk'])
        return render(request, self.template_name, {
            'purchase_bill': purchase_bill,
            'count1': count1,
            'notification1': notification1
        })

    def post(self, request, *args, **kwargs):
        # Get the purchase bill object
        purchase_bill = get_object_or_404(PurchaseBill, pk=kwargs['pk'])

        # Get the related purchase items
        purchase_items = PurchaseItem.objects.filter(billno=purchase_bill.billno)

        # Update stock quantities before deleting the purchase bill
        for item in purchase_items:
            stock = Stock.objects.filter(id=item.stock.id, is_deleted=False).first()
            if stock:
                stock.quantity -= item.quantity
                stock.save()

        # Delete related purchase items
        purchase_items.delete()

        # Delete the purchase bill itself
        purchase_bill.delete()

        # Add a success message
        messages.success(request, "Purchase bill has been deleted successfully")

        # Redirect to the purchase list page
        return redirect('/transactions/purchases')


def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})
#
# def get_stocks(request):
#     subcategory_id = request.GET.get('subcategory_id')
#     stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name')
#     return JsonResponse({'stocks': list(stocks)})

def get_stocks_purchase(request):
    subcategory_id = request.GET.get('subcategory_id')
    # Filter stocks by subcategory and ensure stock quantity is more than 0
    stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name')
    return JsonResponse({'stocks': list(stocks)})



def get_stocks(request):
    subcategory_id = request.GET.get('subcategory_id')
    # Filter stocks by subcategory and ensure stock quantity is more than 0
    stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False, quantity__gt=0).values('id', 'name', 'gst')
    return JsonResponse({'stocks': list(stocks)})


# # View to select the supplier based on category
# class SelectCustomerView(View):
#     form_class = SelectSaleForm
#     template_name = 'sales/select_customer.html'
#
#     def get(self, request, *args, **kwargs):  # loads the form page
#         form = self.form_class()
#         customers = Customer.objects.values('Cust_type').distinct()  # Fetch only Cust_type as a list
#         return render(request, self.template_name, {'form': form, 'customers': customers})
#
#     def post(self, request, *args, **kwargs):  # gets selected supplier and redirects to 'PurchaseCreateView' class
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             customerid = request.POST.get("customer")
#             customer = get_object_or_404(Customer, id=customerid)
#             return redirect('new-purchase', customer.pk)
#         customers = Customer.objects.values('Cust_type').distinct()  # Fetch only Cust_type as a list
#         return render(request, self.template_name, {'form': form, 'customers': customers})
#
# # # AJAX view to get suppliers based on the selected category
# # def get_suppliers(request, category_id):
# #     suppliers = Supplier.objects.filter(category=category_id)  # Get suppliers for the selected category
# #     suppliers_data = [{'id': supplier.id, 'name': supplier.supplier_name} for supplier in suppliers]
# #     return JsonResponse({'suppliers': suppliers_data})
# def get_customer(request, Cust_id):
#     # Fetch suppliers filtered by the selected category
#     suppliers = Customer.objects.filter(Cust_id=Cust_id)
#     # Use the correct field name 'name' instead of 'supplier_name'
#     suppliers_data = [{'id': supplier.Cust_id, 'name': supplier.Comp_name} for supplier in suppliers]
#
#     # Return the suppliers in JSON format
#     return JsonResponse({'suppliers': suppliers_data})


# class SelectCustomerView(View):
#     form_class = SelectSaleForm
#     template_name = 'sales/select_customer.html'
#
#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         customers = Customer.objects.values('Cust_type').distinct()  # Fetch distinct Cust_type values
#         return render(request, self.template_name, {'form': form, 'customers': customers})
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             customerid = request.POST.get("supplier")
#             customer = get_object_or_404(Customer, Cust_id=customerid)
#             print(customer)
#             return redirect('new-sale', customer.pk)
#
#         customers = Customer.objects.values('Cust_type').distinct()
#         return render(request, self.template_name, {'form': form, 'customers': customers})
#
# def get_customer(request, cust_type):
#     suppliers = Customer.objects.filter(Cust_type=cust_type)
#     suppliers_data = [{'id': supplier.Cust_id, 'name': supplier.Comp_name} for supplier in suppliers]
#     return JsonResponse({'suppliers': suppliers_data})



from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

# class SelectCustomerView(LoginRequiredMixin, View):
#     form_class = SelectSaleForm
#     template_name = 'sales/select_customer.html'
#     login_url = '/index/'
#
#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         customers = Customer.objects.values('Cust_type').distinct()  # Fetch distinct Cust_type values
#         return render(request, self.template_name, {'form': form, 'customers': customers})
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         selected_supplier = request.POST.get("selected_supplier")
#         dc_type = request.POST.get("dc_type")
#         if selected_supplier:
#             customer = get_object_or_404(Customer, Cust_id=selected_supplier)
#             if dc_type == "individual":
#               return redirect('new-sale', customer.pk)
#             if dc_type == "selected" and selected_supplier:
#               return redirect('custome-sale', customer.pk)
#         customers = Customer.objects.values('Cust_type').distinct()
#         return render(request, self.template_name, {'form': form, 'customers': customers})


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Customer, Vendor
from .forms import SelectSaleForm

class SelectCustomerView(LoginRequiredMixin, View):
    form_class = SelectSaleForm
    template_name = 'sales/select_customer.html'
    login_url = '/index/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        # Get distinct customer categories from the Customer table
        customer_categories = list(Customer.objects.values('Cust_type').distinct())
        # Get distinct vendor categories (assumes Vendor.category exists)
        vendor_categories = list(Vendor.objects.values('category__id', 'category__name').distinct())
        context = {
            'form': form,
            'customer_categories': customer_categories,
            'vendor_categories': vendor_categories,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        selected_supplier = request.POST.get("selected_supplier")
        dc_type = request.POST.get("dc_type")
        entity_type = request.POST.get("selected_entity")  # 'customer' or 'vendor'
        if selected_supplier:
            if entity_type == 'customer':
                customer = get_object_or_404(Customer, Cust_id=selected_supplier)
                if dc_type == "individual":
                    return redirect('new-sale', customer.pk)
                elif dc_type == "selected":
                    return redirect('custome-sale', customer.pk)
            elif entity_type == 'vendor':
                customer = get_object_or_404(Vendor, id=selected_supplier)
                if dc_type == "individual":
                    # Change URL name as appropriate
                    return redirect('new-sale', customer.pk)
                elif dc_type == "selected":
                    return redirect('custome-sale', customer.pk)
        # If something is missing, re-render the form with categories for context.
        customer_categories = list(Customer.objects.values('Cust_type').distinct())
        vendor_categories = list(Vendor.objects.values('category__id', 'category__name').distinct())
        context = {
            'form': form,
            'customer_categories': customer_categories,
            'vendor_categories': vendor_categories,
        }
        return render(request, self.template_name, context)


from django.http import JsonResponse
from .models import Vendor

def get_vendors(request, category_id):
    # Filter vendors by the category id. Adjust the filter if needed.
    vendors = Vendor.objects.filter(category__id=category_id, status=True)
    vendor_list = [{'id': vendor.id,
                    'name':f"{vendor.name}, {vendor.city}"
    } for vendor in vendors]

    return JsonResponse({'suppliers': vendor_list})



class SelectCustomerView_bill(LoginRequiredMixin, View):
    form_class = SelectSaleForm
    template_name = 'sales/select_customer_bill.html'
    login_url = '/index/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        customers = Customer.objects.values('Cust_type').distinct()  # Fetch distinct Cust_type values
        return render(request, self.template_name, {'form': form, 'customers': customers})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        selected_supplier = request.POST.get("selected_supplier")
        if selected_supplier:
            customer = get_object_or_404(Customer, Cust_id=selected_supplier)
            return redirect('new-sale_bill', customer.pk)

        customers = Customer.objects.values('Cust_type').distinct()
        return render(request, self.template_name, {'form': form, 'customers': customers})

#
# def get_customer(request, cust_type):
#     suppliers = Customer.objects.filter(Cust_type=cust_type)
#     suppliers_data = [{'id': supplier.Cust_id, 'name': supplier.Comp_name} for supplier in suppliers]
#     return JsonResponse({'suppliers': suppliers_data})

# def get_customer(request, cust_type):
#     suppliers = Customer.objects.filter(Cust_type=cust_type)
#     suppliers_data = [{
#         'id': supplier.Cust_id,
#         'name': f"{supplier.Comp_name}, {supplier.City}"
#     } for supplier in suppliers]
#     return JsonResponse({'suppliers': suppliers_data})


def get_customer(request, cust_type):
    # suppliers = Customer.objects.filter(Cust_type=cust_type)
    suppliers = Customer.objects.filter(Cust_type=cust_type, advance_paid='paid')
    suppliers_data = []

    for supplier in suppliers:
        comp_name = supplier.Comp_name or ''
        city = supplier.City or ''
        consumer = supplier.Consumer or ''
        last_four = consumer[-4:] if len(consumer) >= 4 else consumer
        full_name = f"{comp_name},  {city} -  (Mseb - {last_four})"
        suppliers_data.append({'id': supplier.Cust_id, 'name': full_name})

    return JsonResponse({'suppliers': suppliers_data})



#
# # shows the list of bills of all sales
# class SaleView(ListView):
#     model = SaleBill
#     template_name = "sales/sales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']
#     paginate_by = 10
#


# class SaleView(ListView):
#     model = SaleBill
#     template_name = "sales/sales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Category filter
#         category_id = self.request.GET.get('category')
#         if category_id:
#             queryset = queryset.filter(supplier__category_id=category_id)
#
#         # Date filter
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         # Date filter logic
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             # Get custom date range from the request
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Ensure start_date and end_date are provided and parsed correctly
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             # If valid start_date and end_date, apply filter
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 # Show all data if dates are not valid
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all categories for category dropdown
#         context['categories'] = Category.objects.all()
#
#         # Handle selected category for filtering
#         selected_category = None
#         category_id = self.request.GET.get('category')
#         if category_id:
#             selected_category = Category.objects.filter(id=category_id).first()
#
#         context['selected_category'] = selected_category
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter heading logic
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             # Custom date range
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Convert strings to datetime objects
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context


# class SaleView(ListView):
#     model = SaleBill
#     template_name = "sales/sales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Cust_type filter
#         cust_type = self.request.GET.get('cust_type')
#         if cust_type:
#             queryset = queryset.filter(supplier__customer__cust_type=cust_type)
#
#         # Date filter
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         # Date filter logic
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             # Get custom date range from the request
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Ensure start_date and end_date are provided and parsed correctly
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             # If valid start_date and end_date, apply filter
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 # Show all data if dates are not valid
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all Cust_type for cust_type dropdown
#         context['cust_types'] = Customer.objects.values_list('cust_type', flat=True).distinct()
#
#         # Handle selected Cust_type for filtering
#         selected_cust_type = self.request.GET.get('cust_type')
#         context['selected_cust_type'] = selected_cust_type
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter heading logic
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             # Custom date range
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             # Convert strings to datetime objects
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context
#
# class SaleView(LoginRequiredMixin, ListView):
#     model = SaleBill
#     template_name = "sales/sales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#     login_url = '/index/'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Cust_type filter
#         cust_type = self.request.GET.get('cust_type')
#         if cust_type:
#             queryset = queryset.filter(Cust_id__Cust_type=cust_type)
#
#         # Date filter logic (same as before)
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all customer types for cust_type dropdown
#         context['customers'] = Customer.objects.values('Cust_type').distinct()
#
#         # Handle selected cust_type for filtering
#         selected_cust_type = self.request.GET.get('cust_type')
#         context['selected_Cust_type'] = selected_cust_type
#
#
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter caption logic (same as before)
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context
#

# class SaleView(LoginRequiredMixin, ListView):
#     model = SaleBill
#     template_name = "sales/sales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#     login_url = '/index/'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Get user type from the GET parameters (default to Consumer)
#         user_type = self.request.GET.get("user_type", "Consumer")
#
#         if user_type == "Consumer":
#             cust_type = self.request.GET.get("cust_type")
#             if cust_type:
#                 queryset = queryset.filter(Cust_id__Cust_type=cust_type)
#         elif user_type == "Vendor":
#             vendor_category = self.request.GET.get("vendor_category")
#             if vendor_category:
#                 # Adjust filtering based on your vendor relationship;
#                 # here we assume SaleBill has a vendor field with a category relation.
#                 queryset = queryset.filter(Vend_id__category_id=vendor_category)
#
#         # Date filter logic
#         filter_value = self.request.GET.get("filter", "All")
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_value == "Today":
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == "Custom":
#             start_date_str = self.request.GET.get("start_date")
#             end_date_str = self.request.GET.get("end_date")
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # For Consumer dropdown
#         context["customers"] = Customer.objects.values("Cust_type").distinct()
#         selected_cust_type = self.request.GET.get("cust_type")
#         context["selected_Cust_type"] = selected_cust_type
#
#         # For Vendor dropdown (assuming Category model is used)
#         context["vendor_categories"] = Category.objects.all()
#         selected_vendor_category = self.request.GET.get("vendor_category")
#         context["selected_vendor_category"] = selected_vendor_category
#
#         # User type (default to Consumer)
#         selected_user_type = self.request.GET.get("user_type", "Consumer")
#         context["selected_user_type"] = selected_user_type
#
#         # Pass date filter value to the context
#         filter_option = self.request.GET.get("filter", "All")
#         context["selected_filter"] = filter_option
#
#         # Date filter caption logic
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             start_date_str = self.request.GET.get("start_date")
#             end_date_str = self.request.GET.get("end_date")
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date and end_date:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context["caption_text"] = caption_text
#         context["caption_text1"] = caption_text1
#
#         # Pass custom date range values to the context
#         context["start_date"] = self.request.GET.get("start_date", "")
#         context["end_date"] = self.request.GET.get("end_date", "")
#
#         return context

class SaleView(LoginRequiredMixin, ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']  # Default ordering by 'time'
    login_url = '/index/'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get user type (default to All)
        user_type = self.request.GET.get("user_type", "All")

        if user_type == "Consumer":
            # Only show consumer records.
            # Apply consumer category filter if provided and not "All"
            cust_type = self.request.GET.get("cust_type", "All")
            if cust_type != "All" and cust_type:
                queryset = queryset.filter(Cust_id__Cust_type=cust_type)
            else:
                # Assuming consumer records are identified by having a non-null Cust_id.
                queryset = queryset.filter(Cust_id__isnull=False)
        elif user_type == "Vendor":
            # Only show vendor records.
            # Apply vendor category filter if provided and not "All"
            vendor_category = self.request.GET.get("vendor_category", "All")
            if vendor_category != "All" and vendor_category:
                # queryset = queryset.filter(vendor__category_id=vendor_category)
                queryset = queryset.filter(Vend_id__category_id=vendor_category)
            else:
                # Assuming vendor records are identified by having a non-null vendor field.
                queryset = queryset.filter(Vend_id__isnull=False)
        elif user_type == "All":
            # No filtering based on user type; show all records.
            pass

        # Date filter logic
        filter_value = self.request.GET.get("filter", "All")
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None
        table_name = SaleBill._meta.db_table

        def _apply_text_date_between(qs, start_dt, end_dt):
            return qs.extra(
                where=[
                    f"substring(COALESCE({table_name}.time::text, ''), 1, 10) BETWEEN %s AND %s"
                ],
                params=[start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")],
            )

        if filter_value == "Today":
            start_date = today
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None
            if start_date and end_date:
                queryset = _apply_text_date_between(queryset, start_date, end_date)
            else:
                queryset = queryset.none()

        queryset = _scope_dc_list_queryset_for_associate(
            self.request, queryset, use_salebill_cust_fk=True
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For Consumer category dropdown
        context["customers"] = Customer.objects.values("Cust_type").distinct()
        selected_cust_type = self.request.GET.get("cust_type", "All")
        context["selected_Cust_type"] = selected_cust_type

        # For Vendor category dropdown (using Category model)
        context["vendor_categories"] = Category.objects.all()
        selected_vendor_category = self.request.GET.get("vendor_category", "All")
        context["selected_vendor_category"] = selected_vendor_category

        # User type (default to All)
        selected_user_type = self.request.GET.get("user_type", "All")
        context["selected_user_type"] = selected_user_type

        # Date filter value
        filter_option = self.request.GET.get("filter", "All")
        context["selected_filter"] = filter_option

        # Date filter caption logic
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None

        if filter_option == "All":
            caption_text = "Display All Days View"
            caption_text1 = "Up To Date"
        elif filter_option == "Today":
            start_date = today
            end_date = today
            caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Today"
        elif filter_option == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 7 Days"
        elif filter_option == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 30 Days"
        elif filter_option == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "This Month"
        elif filter_option == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")
            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None
            if start_date and end_date:
                caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            else:
                caption_text = "Display Custom Range View"
            caption_text1 = "Custom Range"
        else:
            caption_text = "The option is not selected, so all records show"
            caption_text1 = ""

        context["caption_text"] = caption_text
        context["caption_text1"] = caption_text1

        # Pass custom date range values to the context
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")

        return context



# class FinalSaleView(LoginRequiredMixin, ListView):
#     model = FinalSale
#     template_name = "sales/finalsales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#     login_url = '/index/'
#
#     def get_queryset(self):
#         # queryset = super().get_queryset()
#         queryset = super().get_queryset().prefetch_related('final_sale_items',
#                                                            'sale_bills')  # Prefetch related SaleBill
#
#         # Start with the base queryset, filtered for is_deleted=False
#         # queryset = super().get_queryset().filter(is_deleted=False).prefetch_related(
#         #     'final_sale_items', 'sale_bills'
#         # )
#
#         # Cust_type filter
#         cust_type = self.request.GET.get('cust_type')
#         if cust_type:
#             queryset = queryset.filter(customer__Cust_type=cust_type)
#
#         # Date filter logic (same as before)
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all customer types for cust_type dropdown
#         context['customers'] = Customer.objects.values('Cust_type').distinct()
#
#         # Handle selected cust_type for filtering
#         selected_cust_type = self.request.GET.get('cust_type')
#         context['selected_Cust_type'] = selected_cust_type
#
#
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter caption logic (same as before)
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context


class FinalSaleView(LoginRequiredMixin, ListView):
    model = FinalSale
    template_name = "sales/finalsales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']  # Default ordering by 'time'
    login_url = '/index/'

    def get_queryset(self):
        # queryset = super().get_queryset()
        queryset = super().get_queryset().prefetch_related('final_sale_items',
                                                           'sale_bills')  # Prefetch related SaleBill

        # Get user type (default to All)
        user_type = self.request.GET.get("user_type", "All")

        if user_type == "Consumer":
            # Only show consumer records.
            # Apply consumer category filter if provided and not "All"
            cust_type = self.request.GET.get("cust_type", "All")
            if cust_type != "All" and cust_type:
                queryset = queryset.filter(customer__Cust_type=cust_type)
            else:
                # Assuming consumer records are identified by having a non-null Cust_id.
                queryset = queryset.filter(customer__isnull=False)
        elif user_type == "Vendor":
            # Only show vendor records.
            # Apply vendor category filter if provided and not "All"
            vendor_category = self.request.GET.get("vendor_category", "All")
            if vendor_category != "All" and vendor_category:
                # queryset = queryset.filter(vendor__category_id=vendor_category)
                queryset = queryset.filter(vendor__category_id=vendor_category)
            else:
                # Assuming vendor records are identified by having a non-null vendor field.
                queryset = queryset.filter(vendor__isnull=False)
        elif user_type == "All":
            # No filtering based on user type; show all records.
            pass

        # Date filter logic
        filter_value = self.request.GET.get("filter", "All")
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None
        table_name = FinalSale._meta.db_table

        def _apply_text_date_between(qs, start_dt, end_dt):
            # DB-safe for both timestamp and legacy text columns:
            # compare YYYY-MM-DD prefix from time::text.
            return qs.extra(
                where=[
                    f"substring(COALESCE({table_name}.time::text, ''), 1, 10) BETWEEN %s AND %s"
                ],
                params=[start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")],
            )

        if filter_value == "Today":
            start_date = today
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")

            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            if start_date and end_date:
                queryset = _apply_text_date_between(queryset, start_date, end_date)
            else:
                queryset = queryset.none()

        queryset = _scope_dc_list_queryset_for_associate(self.request, queryset)
        # Scalar subquery avoids PostgreSQL GROUP BY errors when the queryset uses .extra()
        # (date filter) alongside a join + Count on return_sales.
        _active_returns_subq = (
            ReturnSale.objects.filter(
                final_bill_id=OuterRef("billno"),
                is_deleted=False,
            )
            .order_by()
            .values("final_bill_id")
            .annotate(_n=Count("pk"))
            .values("_n")[:1]
        )
        queryset = queryset.annotate(
            active_return_count=Coalesce(
                Subquery(_active_returns_subq, output_field=IntegerField()),
                Value(0),
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For Consumer category dropdown
        context["customers"] = Customer.objects.values("Cust_type").distinct()
        selected_cust_type = self.request.GET.get("cust_type", "All")
        context["selected_Cust_type"] = selected_cust_type

        # For Vendor category dropdown (using Category model)
        context["vendor_categories"] = Category.objects.all()
        selected_vendor_category = self.request.GET.get("vendor_category", "All")
        context["selected_vendor_category"] = selected_vendor_category

        # User type (default to All)
        selected_user_type = self.request.GET.get("user_type", "All")
        context["selected_user_type"] = selected_user_type

        # Date filter value
        filter_option = self.request.GET.get("filter", "All")
        context["selected_filter"] = filter_option

        # Date filter caption logic
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None

        if filter_option == "All":
            caption_text = "Display All Days View"
            caption_text1 = "Up To Date"
        elif filter_option == "Today":
            start_date = today
            end_date = today
            caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Today"
        elif filter_option == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 7 Days"
        elif filter_option == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 30 Days"
        elif filter_option == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "This Month"
        elif filter_option == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")

            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            if start_date and end_date:
                caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            else:
                caption_text = "Display Custom Range View"
            caption_text1 = "Custom Range"
        else:
            caption_text = "The option is not selected, so all records show"
            caption_text1 = ""

        context["caption_text"] = caption_text
        context["caption_text1"] = caption_text1

        # Pass custom date range values to the context
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")

        return context


#
# # used to generate a bill object and save items
# class SaleCreateView(View):
#     template_name = 'sales/new_sale.html'
#
#     def get(self, request, pk):
#         formset = SaleItemFormset()
#         supplierobj = get_object_or_404(Customer, Cust_id=pk)
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         form = SaleForm(request.POST)
#         formset = SaleItemFormset(request.POST)  # recieves a post method for the formset
#         supplierobj = get_object_or_404(Customer, Cust_id=pk)
#
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = SaleBill(Cust_id=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     # Extract GST toggle state
#                     gst_toggle = request.POST.get('gstToggle')
#
#                     # Initialize GST values
#                     gst_value = 0
#                     gst_amount = 0
#                     eway_no = 0
#                     veh_no = 0
#                     hand_by = 0
#                     destination = 0
#                     po_no = 0
#                     po_date = 0
#                     round_off = request.POST.get('round_off')
#                     final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#                     eway_no = request.POST.get('eway_no')
#                     bill_date = request.POST.get('bill_date')
#                     veh_no = request.POST.get('veh_no')
#                     hand_by = request.POST.get('handby')
#                     destination = request.POST.get('destination')
#                     po_no = request.POST.get('po_no')
#                     po_date = request.POST.get('po_date')
#                     sale_bill = SaleBill.objects.create(bill_no=formset.cleaned_data['sales_billno'])
#
#                     if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
#                         gst_value = request.POST.get('gst_value')
#                         gst_amount = request.POST.get('gst_amount')
#
#                         # round_off = request.POST.get('round_off')
#                         #
#                         # # Clean the final amount (remove ₹ symbol)
#                         # final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#
#                     # Save PurchaseBillDetails
#                     billdetailsobj = SaleBillDetails(
#                         billno=billobj,
#                         gst_value=gst_value,
#                         gst_amount=gst_amount,
#                         round_off=round_off,
#                         eway=eway_no,
#                         cgst=bill_date,
#                         veh=veh_no,
#                         igst=hand_by,
#                         destination=destination,
#                         po=po_no,
#                         tcs=po_date,
#                         # final_amount=request.POST.get('final_amount'),
#                         final_amount=final_amount,
#                         total_amount=request.POST.get('total_amount'),
#                     )
#                     billdetailsobj.save()
#                     logger.info("PurchaseBillDetails saved successfully")
#
#                     # Save each PurchaseItem and update Stock
#                     # for form in formset:
#                     for index, form in enumerate(formset):
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Get the associated stock
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#
#                         # Get the `short_name` from the form and look up the Unit instance
#                         short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
#                         unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
#                         billitem.sale = unit_instance
#
#                         # Calculate the total price for the item
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#
#                         # Update stock quantity
#                         stock.quantity -= billitem.quantity
#                         stock.save()
#                         logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                         # Save the PurchaseItem
#                         billitem.save()
#                         logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#
#                         # # Handle selected serial numbers for the SaleBill
#                         # selected_serial_numbers = request.POST.getlist('serialNo')
#                         # print(selected_serial_numbers)
#                         # if selected_serial_numbers:
#                         #     PurchaseSerial.objects.filter(id__in=selected_serial_numbers).update(sales_billNo=billobj)
#
#                         # Get and save selected serial numbers
#                         serial_numbers = request.POST.get('serials-' + str(stock.id))
#                         if serial_numbers:
#                             serial_list = serial_numbers.split(',')
#                             PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
#                                 sales_billno=sale_bill)
#
#                     # If everything goes well
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('sale-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)

from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Assume these are your defined models and forms
# from .models import SaleBill, SaleBillDetails, Stock, Unit, Customer
# from .forms import SaleForm, SaleItemFormset


# -------------------------------------------------------------------------------------------
# class SaleCreateView(LoginRequiredMixin, View):
#     template_name = 'sales/new_sale.html'
#     login_url = '/index/'
#
#     def get(self, request, pk):
#         formset = SaleItemFormset()  # Initialize an empty formset
#         # supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
#         supplierobj = Customer.objects.filter(Cust_id=pk).first()
#         vendor_obj = Vendor.objects.filter(pk=pk).first()
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'vendor': vendor_obj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = SaleItemFormset(request.POST)  # Receive POST data for the formset
#         # supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
#         # Determine if the pk belongs to a Customer or Vendor
#         supplierobj = Customer.objects.filter(Cust_id=pk).first()
#         vendor_obj = Vendor.objects.filter(pk=pk).first()
#
#         if not supplierobj and not vendor_obj:
#             messages.error(request, "No matching Customer or Vendor was found.")
#             return redirect('select_customer')
#
#         if formset.is_valid():  # Check if the formset is valid
#             try:
#                 with transaction.atomic():  # Use transaction to ensure atomicity
#                     # Save the SaleBill object
#                     # billobj = SaleBill(Cust_id=supplierobj)
#                     # billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
#                     if supplierobj:
#                         billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
#                     else:
#                         # sale_bill = SaleBill(
#                         #     customer=vendor_obj)  # or sale_bill.vendor = vendor_obj if you have separate fields
#                         billobj = SaleBill(Vend_id=vendor_obj, time=timezone.now())
#
#                     billobj.save()
#                     logger.info("SaleBill saved successfully")
#
#                     # Extract additional data from the POST request
#                     # gst_toggle = request.POST.get('gstToggle')
#                     # round_off = request.POST.get('round_off')
#                     # final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#
#                     # Save SaleBillDetails
#                     billdetailsobj = SaleBillDetails(
#                         billno=billobj,
#                         # gst_value=request.POST.get('gst_value') if gst_toggle == 'on' else 0,
#                         # gst_amount=request.POST.get('gst_amount') if gst_toggle == 'on' else 0,
#                         # round_off=round_off,
#                         eway=request.POST.get('eway_no'),
#                         cgst=request.POST.get('bill_date'),
#                         veh=request.POST.get('veh_no'),
#                         sgst=request.POST.get('arrange'),
#                         igst=request.POST.get('handby'),
#                         destination=request.POST.get('destination'),
#                         po=request.POST.get('po_no'),
#                         tcs=request.POST.get('po_date'),
#                         # final_amount=final_amount,
#                         # total_amount=request.POST.get('total_amount'),
#                     )
#                     billdetailsobj.save()
#                     logger.info("SaleBillDetails saved successfully")
#
#                     # Process each form in the formset
#                     for form in formset:
#                         if form.is_valid():  # Check if each individual form is valid
#                             billitem = form.save(commit=False)  # Do not commit yet
#                             billitem.billno = billobj  # Associate the SaleBill with the item
#
#                             # Get the associated stock
#                             stock = get_object_or_404(Stock, pk=billitem.stock.id)
#                             # billitem.totalprice = billitem.perprice * billitem.quantity  # Calculate total price
#
#                             # Get the `short_name` from the form and look up the Unit instance
#                             # short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
#                             # unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
#                             # billitem.sale = unit_instance
#                             billitem.sale = stock.sales  # Assuming `Stock` has a ForeignKey to `Unit`
#
#                             # Update stock quantity and save
#                             stock.quantity -= billitem.quantity
#                             stock.save()
#                             logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                             # Save the SaleItem
#                             billitem.save()
#                             logger.info(f"SaleItem saved successfully for stock id {stock.id}")
#
                            # # Handle selected serial numbers for the SaleBill
                            # serial_numbers = request.POST.get(f'serials-{stock.id}')
                            # if serial_numbers:
                            #     serial_list = serial_numbers.split(',')
                            #     PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
                            #         sales_billno=billobj
                            #     )
#
#                     # If everything goes well, log and redirect
#                     messages.success(request, "Sales items have been registered successfully")
#                     # logger.info(f"Redirecting to sale-bill with billno: {billobj.billno}")
#                     print(f"Redirecting to sale-bill with billno: {billobj.billno}")
#                     return redirect('sale-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)

class SaleCreateView(LoginRequiredMixin, View):
    template_name = 'sales/new_sale.html'
    login_url = '/index/'

    def get(self, request, pk):
        formset = SaleItemFormset()  # Initialize an empty formset
        supplierobj = Customer.objects.filter(Cust_id=pk).first()
        vendor_obj = Vendor.objects.filter(pk=pk).first()
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'vendor': vendor_obj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = SaleItemFormset(request.POST)
        supplierobj = Customer.objects.filter(Cust_id=pk).first()
        vendor_obj = Vendor.objects.filter(pk=pk).first()

        if not supplierobj and not vendor_obj:
            messages.error(request, "No matching Customer or Vendor was found.")
            return redirect('select_customer')

        if formset.is_valid():
            try:
                with transaction.atomic():
                    if supplierobj:
                        billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
                    else:
                        billobj = SaleBill(Vend_id=vendor_obj, time=timezone.now())
                    billobj.save()

                    # Save SaleBillDetails
                    billdetailsobj = SaleBillDetails(
                        billno=billobj,
                        eway=request.POST.get('eway_no'),
                        cgst=request.POST.get('bill_date'),
                        veh=request.POST.get('veh_no'),
                        sgst=request.POST.get('arrange'),
                        igst=request.POST.get('handby'),
                        destination=request.POST.get('destination'),
                        po=request.POST.get('po_no'),
                        tcs=request.POST.get('po_date'),
                    )
                    billdetailsobj.save()

                    # Process each form in the formset
                    for form in formset:
                        if form.is_valid():
                            billitem = form.save(commit=False)
                            billitem.billno = billobj
                            stock = get_object_or_404(Stock, pk=billitem.stock.id)
                            billitem.sale = stock.sales

                            # Update stock quantity and save
                            stock.quantity -= billitem.quantity
                            stock.save()
                            billitem.save()

                            # Handle scanned barcodes for the SaleBill
                            barcodes = request.POST.get(f'barcodes-{stock.id}')

                            # Handle selected serial numbers for the SaleBill
                            serial_numbers = request.POST.get(f'serials-{stock.id}')
                            if serial_numbers:
                                 serial_list = serial_numbers.split(',')
                                 PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
                                        sales_billno=billobj
                                 )
                            else:
                                if barcodes:
                                    barcode_list = barcodes.split(',')
                                    for barcode in barcode_list:
                                        if barcode.strip():  # Ensure barcode is not empty
                                            # Update or create PurchaseSerial record
                                            PurchaseSerial.objects.filter(serialNo=barcode.strip()).update(
                                                sales_billno=billobj,
                                                stock=stock
                                            )

                    messages.success(request, "Sales items have been registered successfully")
                    return redirect('sale-bill', billno=billobj.billno)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "There were errors in the form. Please correct them.")

        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
        }
        return render(request, self.template_name, context)
    # def post(self, request, pk):
    #     formset = SaleItemFormset(request.POST)
    #     supplierobj = Customer.objects.filter(Cust_id=pk).first()
    #     vendor_obj = Vendor.objects.filter(pk=pk).first()
    #
    #     if not supplierobj and not vendor_obj:
    #         messages.error(request, "No matching Customer or Vendor was found.")
    #         return redirect('select_customer')
    #
    #     if formset.is_valid():
    #         try:
    #             with transaction.atomic():
    #                 if supplierobj:
    #                     billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
    #                 else:
    #                     billobj = SaleBill(Vend_id=vendor_obj, time=timezone.now())
    #                 billobj.save()
    #
    #                 # Save SaleBillDetails
    #                 billdetailsobj = SaleBillDetails(
    #                     billno=billobj,
    #                     eway=request.POST.get('eway_no'),
    #                     cgst=request.POST.get('bill_date'),
    #                     veh=request.POST.get('veh_no'),
    #                     sgst=request.POST.get('arrange'),
    #                     igst=request.POST.get('handby'),
    #                     destination=request.POST.get('destination'),
    #                     po=request.POST.get('po_no'),
    #                     tcs=request.POST.get('po_date'),
    #                 )
    #                 billdetailsobj.save()
    #
    #                 # Process each form in the formset
    #                 for form in formset:
    #                     if form.is_valid():
    #                         billitem = form.save(commit=False)
    #                         billitem.billno = billobj
    #                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
    #                         billitem.sale = stock.sales
    #
    #                         # Update stock quantity and save
    #                         stock.quantity -= billitem.quantity
    #                         stock.save()
    #                         billitem.save()
    #
    #                         # Handle both scanned barcodes and selected serial numbers
    #                         barcodes = request.POST.get(f'barcodes-{stock.id}')
    #                         serial_numbers = request.POST.get(f'serials-{stock.id}')
    #
    #                         # Combine both sources of serial numbers
    #                         all_serials = []
    #                         if barcodes:
    #                             all_serials.extend(
    #                                 barcode.strip() for barcode in barcodes.split(',') if barcode.strip())
    #                         if serial_numbers:
    #                             all_serials.extend(
    #                                 serial.strip() for serial in serial_numbers.split(',') if serial.strip())
    #
    #                         # Remove duplicates
    #                         all_serials = list(set(all_serials))
    #
    #                         # Update all serial numbers
    #                         if all_serials:
    #                             PurchaseSerial.objects.filter(
    #                                 serialNo__in=all_serials,
    #                                 stock=stock,
    #                                 sales_billno__isnull=True  # Ensure they're not already sold
    #                             ).update(sales_billno=billobj)

    #                 messages.success(request, "Sales items have been registered successfully")
    #                 return redirect('sale-bill', billno=billobj.billno)
    #
    #         except Exception as e:
    #             messages.error(request, f"An error occurred: {str(e)}")
    #     else:
    #         messages.error(request, "There were errors in the form. Please correct them.")
    #
    #     context = {
    #         'formset': formset,
    #         'supplier': supplierobj,
    #         'stock_list': Stock.objects.filter(is_deleted=False),
    #         'categories': Category.objects.all(),
    #     }
    #     return render(request, self.template_name, context)
# ---------------------------------------------------------------------------------------------------

def search_barcode(request):
    if request.method == 'GET' and 'barcode' in request.GET:
        barcode = request.GET.get('barcode')

        # Search for serial numbers matching the barcode
        serial_numbers = PurchaseSerial.objects.filter(
            serialNo=barcode,
            sales_billno__isnull=True  # Only include serials not already sold
        ).select_related('stock', 'billno').values(
            'serialNo',
            'stock_id',
            stock_name=F('stock__name'),
            bill_no=F('billno__billno'),
            bill_date=F('billno__time')
        )

        return JsonResponse({
            'serial_numbers': list(serial_numbers)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

# def check_barcode(request):
#     if request.method == 'GET' and 'barcode' in request.GET:
#         barcode = request.GET['barcode']
#         try:
#             # Check if barcode exists in transactions_purchaseserial table
#             purchase_serial = PurchaseSerial.objects.filter(serialNo=barcode).first()
#             if purchase_serial:
#                 stock = purchase_serial.stock
#                 return JsonResponse({
#                     'exists': True,
#                     'stock_id': stock.id,
#                     'stock_name': stock.name,
#                     'stock_quantity': float(stock.quantity),
#                     'purchase': stock.purchase.name if stock.purchase else '',
#                     'purchase_id': stock.purchase.id if stock.purchase else None,
#                     'stock_alert': stock.stock_alert
#                 })
#             return JsonResponse({'exists': False})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Invalid request'}, status=400)


# def check_barcode(request):
#     if request.method == 'GET' and 'barcode' in request.GET:
#         barcode = request.GET['barcode']
#         try:
#             # Check if barcode exists in transactions_purchaseserial table
#             purchase_serial = PurchaseSerial.objects.filter(serialNo=barcode).first()
#             if purchase_serial:
#                 stock = purchase_serial.stock
#                 return JsonResponse({
#                     'exists': True,
#                     'stock_id': stock.id,
#                     'stock_name': stock.name,
#                     'stock_quantity': float(stock.quantity),  # Get quantity from inventory_stock
#                     'purchase': stock.purchase.short_name if stock.purchase else '',
#                     'purchase_id': stock.purchase.id if stock.purchase else None,
#                     'stock_alert': stock.stock_alert,
#                     'serial_id': purchase_serial.id  # Include the serial ID
#                 })
#             return JsonResponse({'exists': False})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Invalid request'}, status=400)

def check_barcode(request):
    if request.method == 'GET' and 'barcode' in request.GET:
        barcode = request.GET['barcode']
        try:
            # Check if barcode exists in transactions_purchaseserial table
            purchase_serial = PurchaseSerial.objects.filter(serialNo=barcode).first()
            if purchase_serial:
                # Check if this serial number is already assigned to a sales bill
                if purchase_serial.sales_billno:
                    return JsonResponse({
                        'exists': True,
                        'already_sold': True,
                        'bill_no': purchase_serial.sales_billno.billno if purchase_serial.sales_billno else ''
                    })

                stock = purchase_serial.stock
                return JsonResponse({
                    'exists': True,
                    'already_sold': False,
                    'stock_id': stock.id,
                    'stock_name': stock.name,
                    'stock_quantity': float(stock.quantity),
                    'purchase': stock.purchase.short_name if stock.purchase else '',
                    'purchase_id': stock.purchase.id if stock.purchase else None,
                    'stock_alert': stock.stock_alert,
                    'serial_id': purchase_serial.id
                })
            return JsonResponse({'exists': False})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from .models import SaleBillDetails, Stock
from inventory.models import FavoriteList
from .forms import SaleForm, SaleItemFormset


class customeView(LoginRequiredMixin, View):
    template_name = 'sales/custome_sale.html'
    login_url = '/index/'

    def get(self, request, pk):
        form = SaleForm()
        formset = SaleItemFormset()
        # supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
        # Check for both Customer and Vendor using filter().first()
        supplierobj = Customer.objects.filter(Cust_id=pk).first()
        vendor_obj = Vendor.objects.filter(pk=pk).first()
        stocks = Stock.objects.for_forms_dropdown()  # PG-safe vs legacy bit boolean columns
        favorite_lists = FavoriteList.objects.all()  # Get all favorite lists
        favorite_list = FavoriteList.objects.all().order_by(Lower('name'))

        context = {
            'form': form,
            'formset': formset,
            'stocks': stocks,
            'favorite_lists': favorite_lists,  # Send favorite lists to the template
            'favorite_list': favorite_list,  # Send favorite lists to the template
            'supplier': supplierobj,
            'vendor': vendor_obj,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = SaleItemFormset(request.POST)  # Receive POST data for the formset
        # supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
        # Determine if the pk belongs to a Customer or Vendor
        supplierobj = Customer.objects.filter(Cust_id=pk).first()
        vendor_obj = Vendor.objects.filter(pk=pk).first()

        if formset.is_valid():  # Check if the formset is valid
            try:
                with transaction.atomic():  # Use transaction to ensure atomicity
                    # Save the SaleBill object
                    # billobj = SaleBill(Cust_id=supplierobj)
                    # billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
                    if supplierobj:
                        billobj = SaleBill(Cust_id=supplierobj, time=timezone.now())
                    else:
                        billobj = SaleBill(Vend_id=vendor_obj, time=timezone.now())

                    billobj.save()
                    logger.info("SaleBill saved successfully")

                    # Extract additional data from the POST request
                    # gst_toggle = request.POST.get('gstToggle')
                    # round_off = request.POST.get('round_off')
                    # final_amount = request.POST.get('final_amount').replace('₹', '').strip()

                    # Save SaleBillDetails
                    billdetailsobj = SaleBillDetails(
                        billno=billobj,
                        # gst_value=request.POST.get('gst_value') if gst_toggle == 'on' else 0,
                        # gst_amount=request.POST.get('gst_amount') if gst_toggle == 'on' else 0,
                        # round_off=round_off,
                        eway=request.POST.get('eway_no'),
                        cgst=request.POST.get('bill_date'),
                        veh=request.POST.get('veh_no'),
                        sgst=request.POST.get('arrange'),
                        igst=request.POST.get('handby'),
                        destination=request.POST.get('destination'),
                        po=request.POST.get('po_no'),
                        tcs=request.POST.get('po_date'),
                        # final_amount=final_amount,
                        # total_amount=request.POST.get('total_amount'),
                    )
                    billdetailsobj.save()
                    logger.info("SaleBillDetails saved successfully")

                    # Process each form in the formset
                    for form in formset:
                        if form.is_valid():  # Check if each individual form is valid
                            billitem = form.save(commit=False)  # Do not commit yet
                            billitem.billno = billobj  # Associate the SaleBill with the item

                            # Get the associated stock
                            stock = get_object_or_404(Stock, pk=billitem.stock.id)
                            # billitem.totalprice = billitem.perprice * billitem.quantity  # Calculate total price

                            # # Get the `short_name` from the form and look up the Unit instance
                            # short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
                            # unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
                            # billitem.sale = unit_instance

                            # Fetch the correct unit from the stock model instead of request.POST
                            billitem.sale = stock.sales  # Assuming `Stock` has a ForeignKey to `Unit`

                            # Update stock quantity and save
                            stock.quantity -= billitem.quantity
                            stock.save()
                            logger.info(f"Stock updated successfully for stock id {stock.id}")

                            # Save the SaleItem
                            billitem.save()
                            logger.info(f"SaleItem saved successfully for stock id {stock.id}")

                            # Handle selected serial numbers for the SaleBill
                            serial_numbers = request.POST.get(f'serials-{stock.id}')
                            if serial_numbers:
                                serial_list = serial_numbers.split(',')
                                PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
                                    sales_billno=billobj
                                )

                    # If everything goes well, log and redirect
                    messages.success(request, "Purchased items have been registered successfully")
                    # logger.info(f"Redirecting to sale-bill with billno: {billobj.billno}")
                    print(f"Redirecting to sale-bill with billno: {billobj.billno}")
                    return redirect('sale-bill', billno=billobj.billno)

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            logger.warning(f"Formset is not valid: {formset.errors}")
            messages.error(request, "There were errors in the form. Please correct them.")

        # If form is not valid or any other error occurs
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.for_forms_dropdown(),
            'categories': Category.objects.all(),
        }
        return render(request, self.template_name, context)


def verify_barcode(request):
    serial_no = request.GET.get('serial_no')
    serial = PurchaseSerial.objects.filter(serialNo=serial_no, sales_billno__isnull=True).select_related('stock').first()
    if serial:
        return JsonResponse({
            'exists': True,
            'stock_id': serial.stock.id,
            'stock_name': serial.stock.name,
        })
    return JsonResponse({'exists': False})



#
# def get_favoritelist_stocks(request):
#     # Get the selected favorite list id from AJAX request
#     favoritelist_id = request.GET.get('favoritelist_id')
#     if favoritelist_id:
#         # Retrieve stocks related to the selected favoritelist
#         favoritelist_stocks = FavoriteList.objects.filter(id=favoritelist_id)
#         stocks = favoritelist_stocks.stocks.all()
#
#         # Prepare data to send back in JSON format
#         data = {
#             'stocks': [
#                 {
#                     'id': stock.id,
#                     'name': stock.name,
#                     'quantity': stock.quantity,
#                     # 'price': stock.price,
#                     # 'purchase': stock.purchase,
#                     'purchase': stock.purchase_id,
#                     'stock_alert': stock.stock_alert,
#                     # 'gst': stock.gst,
#                 }
#                 for stock in stocks
#             ]
#         }
#         return JsonResponse(data)
#     return JsonResponse({'stocks': []})

# from django.http import JsonResponse

#
# @login_required(login_url='user-login')
# def get_favoritelist_stocks(request):
#     favoritelist_id = request.GET.get('favoritelist_id')
#
#     if favoritelist_id:
#         try:
#             # Retrieve the favoritelist object
#             favoritelist = FavoriteList.objects.get(id=favoritelist_id)
#
#             # Access related Stock objects through the 'stocks' Many-to-Many field
#             stocks = favoritelist.stocks.all()
#
#             # Prepare data for JSON response
#             data = {
#                 'stocks': [
#                     {
#                         'id': stock.id,
#                         'name': stock.name,
#                         'quantity': stock.quantity,
#                         # 'price': stock.purchase.price if stock.purchase else None,
#                         # # Example: modify according to your need
#                         # 'purchase': stock.purchase.unit_name if stock.purchase else None,
#                         # # Example: modify according to your Unit model
#                         'purchase': stock.purchase.short_name if stock.purchase else None,
#                         # Example: ensure it aligns with your database
#                         'stock_alert': stock.stock_alert,
#                         'gst': stock.gst,
#                         'purchase_id': stock.purchase.id,
#                     }
#                     for stock in stocks
#                 ]
#             }
#             return JsonResponse(data)
#             # return JsonResponse({
#             #     'quantity': stocks.quantity,
#             #     'stock_alert': stocks.stock_alert,
#             #     'gst': stocks.gst,
#             #     'purchase': stocks.purchase.short_name,
#             #     'purchase_id': stocks.purchase.id,
#             # })
#             #
#
#         except FavoriteList.DoesNotExist:
#             return JsonResponse({'error': 'FavoriteList not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     # If no favoritelist_id is provided
#     return JsonResponse({'stocks': []})


@login_required(login_url='user-login')
def get_favoritelist_stocks(request):
    favoritelist_id = request.GET.get('favoritelist_id')

    if favoritelist_id:
        try:
            favoritelist = FavoriteList.objects.get(id=favoritelist_id)

            # Fetch related stock items with through model quantity
            favoritelist_stocks = FavoriteListStock.objects.filter(favorite_list=favoritelist)

            data = {
                'stocks': [
                    {
                        'id': fls.stock.id,
                        'name': fls.stock.name,
                        'quantity': fls.stock.quantity,
                        'favorite_quantity': fls.quantity,  # 🔹 Add the quantity from FavoriteListStock
                        'purchase': fls.stock.purchase.short_name if fls.stock.purchase else None,
                        'purchase_id': fls.stock.purchase.id if fls.stock.purchase else None,
                        'stock_alert': fls.stock.stock_alert,
                        'gst': fls.stock.gst,
                    }
                    for fls in favoritelist_stocks
                ]
            }
            return JsonResponse(data)

        except FavoriteList.DoesNotExist:
            return JsonResponse({'error': 'FavoriteList not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'stocks': []})



# def edit_sale_bill(request, sale_bill_id):
#     sale_bill = get_object_or_404(SaleBill, id=sale_bill_id)
#     SaleItemFormSet = SaleItemFormset_factory(SaleItem, fields=('stock', 'quantity'), extra=0, can_delete=True)
#
#     if request.method == 'POST':
#         formset = SaleItemFormSet(request.POST, queryset=sale_bill.items.all())
#         if formset.is_valid():
#             formset.save()
#             # Update or perform other operations as necessary
#             return redirect('sales-list')
#     else:
#         formset = SaleItemFormSet(queryset=sale_bill.items.all())
#
#     context = {
#         'sale_bill': sale_bill,
#         'formset': formset,
#         'categories': Category.objects.all()  # For category dropdown
#     }
#     return render(request, 'edit_sale_bill.html', context)



class SaleCreateView_bill(LoginRequiredMixin, View):
    template_name = 'sales/new_sale_bill.html'
    login_url = '/index/'

    def get(self, request, pk):
        formset = SaleItemFormset_bill()  # Initialize an empty formset
        supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = SaleItemFormset_bill(request.POST)  # Receive POST data for the formset
        supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object

        if formset.is_valid():  # Check if the formset is valid
            try:
                with transaction.atomic():  # Use transaction to ensure atomicity
                    # Save the SaleBill object
                    billobj = SaleBill(Cust_id=supplierobj)
                    billobj.save()
                    logger.info("SaleBill saved successfully")

                    # Extract additional data from the POST request
                    gst_toggle = request.POST.get('gstToggle')
                    round_off = request.POST.get('round_off')
                    final_amount = request.POST.get('final_amount').replace('₹', '').strip()

                    # Save SaleBillDetails
                    billdetailsobj = SaleBillDetails(
                        billno=billobj,
                        gst_value=request.POST.get('gst_value') if gst_toggle == 'on' else 0,
                        gst_amount=request.POST.get('gst_amount') if gst_toggle == 'on' else 0,
                        round_off=round_off,
                        eway=request.POST.get('eway_no'),
                        cgst=request.POST.get('bill_date'),
                        veh=request.POST.get('veh_no'),
                        igst=request.POST.get('handby'),
                        destination=request.POST.get('destination'),
                        po=request.POST.get('po_no'),
                        tcs=request.POST.get('po_date'),
                        final_amount=final_amount,
                        total_amount=request.POST.get('total_amount'),
                    )
                    billdetailsobj.save()
                    logger.info("SaleBillDetails saved successfully")

                    # Process each form in the formset
                    for form in formset:
                        if form.is_valid():  # Check if each individual form is valid
                            billitem = form.save(commit=False)  # Do not commit yet
                            billitem.billno = billobj  # Associate the SaleBill with the item

                            # Get the associated stock
                            stock = get_object_or_404(Stock, pk=billitem.stock.id)
                            billitem.totalprice = billitem.perprice * billitem.quantity  # Calculate total price

                            # Update stock quantity and save
                            stock.quantity -= billitem.quantity
                            stock.save()
                            logger.info(f"Stock updated successfully for stock id {stock.id}")

                            # Save the SaleItem
                            billitem.save()
                            logger.info(f"SaleItem saved successfully for stock id {stock.id}")

                            # Handle selected serial numbers for the SaleBill
                            serial_numbers = request.POST.get(f'serials-{stock.id}')
                            if serial_numbers:
                                serial_list = serial_numbers.split(',')
                                PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
                                    sales_billno=billobj
                                )

                    # If everything goes well, log and redirect
                    messages.success(request, "Purchased items have been registered successfully")
                    # logger.info(f"Redirecting to sale-bill with billno: {billobj.billno}")
                    print(f"Redirecting to sale-bill with billno: {billobj.billno}")
                    return redirect('sale-bill_bill', billno=billobj.billno)



            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            logger.warning(f"Formset is not valid: {formset.errors}")
            messages.error(request, "There were errors in the form. Please correct them.")

        # If form is not valid or any other error occurs
        context = {
            'formset': formset,
            'supplier': supplierobj,
            'stock_list': Stock.objects.filter(is_deleted=False),
            'categories': Category.objects.all(),
        }
        return render(request, self.template_name, context)






#
# from django.views import View
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.db import transaction
# import logging
#
# # Initialize logger
# logger = logging.getLogger(__name__)
#
# # Assume these are your defined models and forms
# # from .models import SaleBill, SaleBillDetails, Stock, Unit, Customer
# # from .forms import SaleForm, SaleItemFormset
#
# class SaleCreateView(View):
#     template_name = 'sales/new_sale.html'
#
#     def get(self, request, pk):
#         formset = SaleItemFormset()  # Initialize an empty formset
#         supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)
#
#     def post(self, request, pk):
#         formset = SaleItemFormset(request.POST)  # Receive POST data for the formset
#         supplierobj = get_object_or_404(Customer, Cust_id=pk)  # Get the supplier object
#
#         if formset.is_valid():  # Check if the formset is valid
#             try:
#                 with transaction.atomic():  # Use transaction to ensure atomicity
#                     # Save the SaleBill object
#                     billobj = SaleBill(Cust_id=supplierobj)
#                     billobj.save()
#                     logger.info("SaleBill saved successfully")
#
#                     # Extract additional data from the POST request
#                     gst_toggle = request.POST.get('gstToggle')
#                     round_off = request.POST.get('round_off')
#                     final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#
#                     # Save SaleBillDetails
#                     billdetailsobj = SaleBillDetails(
#                         billno=billobj,
#                         gst_value=request.POST.get('gst_value') if gst_toggle == 'on' else 0,
#                         gst_amount=request.POST.get('gst_amount') if gst_toggle == 'on' else 0,
#                         round_off=round_off,
#                         eway=request.POST.get('eway_no'),
#                         cgst=request.POST.get('bill_date'),
#                         veh=request.POST.get('veh_no'),
#                         igst=request.POST.get('handby'),
#                         destination=request.POST.get('destination'),
#                         po=request.POST.get('po_no'),
#                         tcs=request.POST.get('po_date'),
#                         final_amount=final_amount,
#                         total_amount=request.POST.get('total_amount'),
#                     )
#                     billdetailsobj.save()
#                     logger.info("SaleBillDetails saved successfully")
#
#                     # Process each form in the formset
#                     for form in formset:
#                         if form.is_valid():  # Check if each individual form is valid
#                             billitem = form.save(commit=False)  # Do not commit yet
#                             billitem.billno = billobj  # Associate the SaleBill with the item
#
#                             # Get the associated stock
#                             stock = get_object_or_404(Stock, pk=billitem.stock.id)
#                             billitem.totalprice = billitem.perprice * billitem.quantity  # Calculate total price
#
#                             # Update stock quantity and save
#                             stock.quantity -= billitem.quantity
#                             stock.save()
#                             logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                             # Save the SaleItem
#                             billitem.save()
#                             logger.info(f"SaleItem saved successfully for stock id {stock.id}")
#
#                             # Handle selected serial numbers for the SaleBill
#                             serial_numbers = request.POST.get(f'serials-{stock.id}')
#                             if serial_numbers:
#                                 serial_list = serial_numbers.split(',')
#                                 PurchaseSerial.objects.filter(serialNo__in=serial_list, stock=stock).update(
#                                     sales_billno=billobj
#                                 )
#
#                     # If everything goes well
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('sale-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#         }
#         return render(request, self.template_name, context)




# def get_serial_numbers(request):
#         stock_id = request.GET.get('stock_id')
#         serial_numbers = PurchaseSerial.objects.filter(stock_id=stock_id).values('serialNo')
#         return JsonResponse({'serial_numbers': list(serial_numbers)})

# def get_serial_numbers(request):
#     stock_id = request.GET.get('stock_id')
#     serial_numbers = PurchaseSerial.objects.filter(stock_id=stock_id, sales_billno=None).values('id', 'serialNo')
#     return JsonResponse({'serial_numbers': list(serial_numbers)})



def get_purchase_serial_numbers(request):
    billno = request.GET.get('billno')
    stock_id = request.GET.get('stock_id')


    # Sanitize and extract the numeric part of the billno
    if billno and billno.startswith("Bill no: "):
        billno = billno.replace("Bill no: ", "")

    print(billno)
    print(stock_id)
    # Filter the PurchaseSerial records accordingly. Adjust the query as needed.
    serials = PurchaseSerial.objects.filter(billno=billno, stock_id=stock_id)
    serial_list = [s.serialNo for s in serials]
    return JsonResponse({'serialNumbers': serial_list})

#
# def get_serial_numbers(request):
#     stock_id = request.GET.get('stock_id')
#     serial_numbers = PurchaseSerial.objects.filter(stock_id=stock_id, sales_billno=None)
#     serials = [{'serialNo': s.serialNo} for s in serial_numbers]
#     return JsonResponse({'serial_numbers': serials})


import json
from django.views.decorators.csrf import csrf_exempt

#
# # @csrf_exempt  # Alternatively, ensure you pass the CSRF token from your AJAX request
# def update_purchase_serial_numbers(request):
#     if request.method == 'POST':
#         billno = request.POST.get('billno')
#         stock_id = request.POST.get('stock_id')
#         # purchase = request.POST.get('purchase_id')
#         serial_numbers = json.loads(request.POST.get('serial_numbers', '[]'))
#
#         print(billno)
#         print(stock_id)
#         print(serial_numbers)
#         # print(purchase)
#
#         # Sanitize and extract the numeric part of the billno
#         if billno and billno.startswith("Bill no: "):
#             billno = billno.replace("Bill no: ", "")
#
#         # Retrieve related PurchaseBill and Stock objects (adjust queries as needed)
#         bill = get_object_or_404(PurchaseBill, billno=billno)
#         stock = get_object_or_404(Stock, id=stock_id)
#         purchase_item = get_object_or_404(PurchaseItem, billno=bill, stock=stock)
#         print(purchase_item)
#         PurchaseSerial.objects.filter(item=purchase_item).delete()
#         # Here you might want to update existing PurchaseSerial records or create new ones.
#         # For simplicity, let’s remove old records and create new ones.
#         # PurchaseSerial.objects.filter(billno=bill, stock_id=stock).delete()
#         for serial in serial_numbers:
#             PurchaseSerial.objects.create(
#                 billno=bill,
#                 stock=stock,
#                 serialNo=serial.strip(),
#                 purchase=stock.purchase,
#                 item_id=purchase_item.id,
#                 # Set other required fields as needed.
#             )
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'error': 'Invalid request method'}, status=400)



def update_purchase_serial_numbers(request):
    if request.method == 'POST':
        billno = request.POST.get('billno')
        stock_id = request.POST.get('stock_id')
        serial_numbers = json.loads(request.POST.get('serial_numbers', '[]'))

        print(billno)
        print(stock_id)
        print(serial_numbers)

        # Remove the "Bill no: " prefix if present
        if billno and billno.startswith("Bill no: "):
            billno = billno.replace("Bill no: ", "")

        # Retrieve related objects.
        bill = get_object_or_404(PurchaseBill, billno=billno)
        stock = get_object_or_404(Stock, id=stock_id)

        try:
            purchase_item = PurchaseItem.objects.get(billno=bill, stock=stock)
        except PurchaseItem.DoesNotExist:
            # Option A: Create a new PurchaseItem if one doesn't exist.
            purchase_item = PurchaseItem.objects.create(
                billno=bill,
                stock=stock,
                # Set other required fields here.
            )
            # Option B: Or you could return an error message instead.
            # return JsonResponse({'error': 'No purchase item exists for this bill and stock.'}, status=404)
        print(purchase_item)

        # Delete any existing PurchaseSerial records for this purchase item.
        PurchaseSerial.objects.filter(item=purchase_item).delete()

        # Create new PurchaseSerial entries.
        for serial in serial_numbers:
            PurchaseSerial.objects.create(
                billno=bill,
                stock=stock,
                serialNo=serial.strip(),
                purchase=stock.purchase,
                item=purchase_item,  # Pass the instance directly.
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_serial_numbers(request):
    stock_id = request.GET.get('stock_id')
    serial_numbers = (
        PurchaseSerial.objects
        .filter(
            stock_id=stock_id,
            sales_billno__isnull=True,
            final_salebill__isnull=True
        )
        .select_related('billno')
        .order_by('billno__billno', 'serialNo')
    )

    serials = []
    grouped = {}

    for s in serial_numbers:
        bill_no = str(s.billno.billno) if s.billno_id else "N/A"
        serial_value = (s.serialNo or "").strip()
        if not serial_value:
            continue
        serials.append({
            'serialNo': serial_value,
            'billno': bill_no
        })
        grouped.setdefault(bill_no, []).append(serial_value)

    grouped_by_bill = [
        {
            'billno': bill_no,
            'serial_numbers': values,
            'serial_count': len(values)
        }
        for bill_no, values in grouped.items()
    ]

    return JsonResponse({
        'serial_numbers': serials,
        'grouped_by_bill': grouped_by_bill
    })


# def get_serial_numbers(request):
#     stock_id = request.GET.get('stock_id')
#     sales_billno = request.GET.get(
#         'sales_billno')  # You might want to pass the sales_billno here to track selected serials
#     serial_numbers = PurchaseSerial.objects.filter(stock_id=stock_id, sales_billno=None)
#
#     # Get already selected serial numbers for the current sales bill
#     selected_serials = PurchaseSerial.objects.filter(sales_billno=sales_billno).values_list('serialNo', flat=True)
#
#     serials = [
#         {'serialNo': s.serialNo, 'is_selected': s.serialNo in selected_serials}
#         for s in serial_numbers
#     ]
#
#     return JsonResponse({'serial_numbers': serials})




def update_sales_billno(request):
        if request.method == 'POST':
            selected_serial_numbers = request.POST.getlist('selectedSerialNumbers')
            sales_billno = request.POST.get('sales_billno')

            # Update purchaseserial entries
            PurchaseSerial.objects.filter(serialNo__in=selected_serial_numbers).update(sales_billno=sales_billno)

            return JsonResponse({'success': True})


#
# def submit_purchase_form(request):
#     if request.method == 'POST':
#         form_data = request.POST
#         selected_serial_numbers = json.loads(form_data.get('selected_serial_numbers', '[]'))
#         sales_bill_no = form_data.get('sales_bill_no')  # Adjust based on your form field name
#
#         # Update sales bill no in the database for selected serial numbers
#         PurchaseSerial.objects.filter(serialNo__in=selected_serial_numbers).update(sales_billno=sales_bill_no)
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False}, status=400)


    # def post(self, request, pk):
    #     formset = PurchaseItemFormset(request.POST)
    #     supplierobj = get_object_or_404(Supplier, pk=pk)
    #
    #     if formset.is_valid():
    #         try:
    #             with transaction.atomic():
    #                 # Save PurchaseBill
    #                 billobj = PurchaseBill(supplier=supplierobj)
    #                 billobj.save()
    #                 logger.info("PurchaseBill saved successfully")
    #
    #                 # Extract GST toggle state
    #                 gst_toggle = request.POST.get('gstToggle')
    #
    #                 # Initialize GST values
    #                 gst_value = 0
    #                 gst_amount = 0
    #                 eway_no = 0
    #                 veh_no = 0
    #                 hand_by = 0
    #                 destination = 0
    #                 po_no = 0
    #                 po_date = 0
    #                 round_off = request.POST.get('round_off')
    #                 final_amount = request.POST.get('final_amount').replace('₹', '').strip()
    #                 eway_no = request.POST.get('eway_no')
    #                 bill_date = request.POST.get('bill_date')
    #                 veh_no = request.POST.get('veh_no')
    #                 hand_by = request.POST.get('handby')
    #                 destination = request.POST.get('destination')
    #                 po_no = request.POST.get('po_no')
    #                 po_date = request.POST.get('po_date')
    #
    #                 if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
    #                     gst_value = request.POST.get('gst_value')
    #                     gst_amount = request.POST.get('gst_amount')
    #
    #                     # round_off = request.POST.get('round_off')
    #                     #
    #                     # # Clean the final amount (remove ₹ symbol)
    #                     # final_amount = request.POST.get('final_amount').replace('₹', '').strip()
    #
    #                 # Save PurchaseBillDetails
    #                 billdetailsobj = PurchaseBillDetails(
    #                     billno=billobj,
    #                     gst_value=gst_value,
    #                     gst_amount=gst_amount,
    #                     round_off = round_off,
    #                     eway = eway_no,
    #                     cgst = bill_date,
    #                     veh = veh_no,
    #                     igst = hand_by,
    #                     destination = destination,
    #                     po = po_no,
    #                     tcs = po_date,
    #                     # final_amount=request.POST.get('final_amount'),
    #                     final_amount=final_amount,
    #                     total_amount=request.POST.get('total_amount'),
    #                 )
    #                 billdetailsobj.save()
    #                 logger.info("PurchaseBillDetails saved successfully")
    #
    #                 # Save each PurchaseItem and update Stock
    #                 # for form in formset:
    #                 for index, form in enumerate(formset):
    #                     billitem = form.save(commit=False)
    #                     billitem.billno = billobj
    #
    #                     # Get the associated stock
    #                     stock = get_object_or_404(Stock, pk=billitem.stock.id)
    #
    #                     # Get the `short_name` from the form and look up the Unit instance
    #                     short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
    #                     unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
    #                     billitem.purchase = unit_instance
    #
    #                     # Calculate the total price for the item
    #                     billitem.totalprice = billitem.perprice * billitem.quantity
    #
    #                     # Update stock quantity
    #                     stock.quantity += billitem.quantity
    #                     stock.save()
    #                     logger.info(f"Stock updated successfully for stock id {stock.id}")
    #
    #                     # Save the PurchaseItem
    #                     billitem.save()
    #                     logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
    #
    #                     # Save PurchaseSerial entries
    #                     serial_numbers = request.POST.getlist(f'serial_numbers_{index}[]')
    #                     for serial_number in serial_numbers:
    #                         purchase_serial = PurchaseSerial(
    #                             billno=billobj,
    #                             stock=stock,
    #                             purchase=unit_instance,
    #                             serialNo=serial_number,
    #                             item=billitem  # Link to the saved PurchaseItem
    #                         )
    #                         purchase_serial.save()
    #                         logger.info(
    #                             f"PurchaseSerial saved successfully for stock id {stock.id} with serial number {serial_number}")
    #
    #                 # If everything goes well
    #                 messages.success(request, "Purchased items have been registered successfully")
    #                 return redirect('purchase-bill', billno=billobj.billno)
    #
    #         except Exception as e:
    #             logger.error(f"An error occurred: {str(e)}")
    #             messages.error(request, f"An error occurred: {str(e)}")
    #     else:
    #         logger.warning(f"Formset is not valid: {formset.errors}")
    #         messages.error(request, "There were errors in the form. Please correct them.")
    #
    #     # If form is not valid or any other error occurs
    #     context = {
    #         'formset': formset,
    #         'supplier': supplierobj,
    #         'stock_list': Stock.objects.filter(is_deleted=False),
    #         'categories': Category.objects.all(),
    #     }
    #     return render(request, self.template_name, context)



# used to generate a bill object and save items
class SaleCreateView1(LoginRequiredMixin, View):
    template_name = 'sales/new_sale1.html'
    login_url = '/index/'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)  # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form': form,
            'formset': formset,
            'stocks': stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)  # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            # saves bill
            billobj = form.save(commit=False)
            billobj.save()
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:  # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj  # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form': form,
            'formset': formset,
        }
        return render(request, self.template_name, context)

#
# # used to delete a bill object
# class SaleDeleteView(SuccessMessageMixin, DeleteView):
#     model = SaleBill
#     template_name = "sales/delete_sale.html"
#     success_url = '/transactions/sales'
#
#     def delete(self, *args, **kwargs):
#         self.object = self.get_object()
#         items = SaleItem.objects.filter(billno=self.object.billno)
#         for item in items:
#             stock = get_object_or_404(Stock, name=item.stock.name)
#             if stock.is_deleted == False:
#                 stock.quantity += item.quantity
#                 stock.save()
#         messages.success(self.request, "Sale bill has been deleted successfully")
#         return super(SaleDeleteView, self).delete(*args, **kwargs)
#
#
# class SaleDeleteView(View):
#     template_name = "sales/delete_sale.html"
#
#     def get(self, request, *args, **kwargs):
#         # Display the confirmation page
#         sale_bill = get_object_or_404(SaleBill, pk=kwargs['pk'])
#         return render(request, self.template_name, {'sale_bill': sale_bill})
#
#     def post(self, request, *args, **kwargs):
#         # Perform the deletion and stock update
#         sale_bill = get_object_or_404(SaleBill, pk=kwargs['pk'])
#         sale_items = SaleItem.objects.filter(billno=sale_bill.billno)
#
#         # Restore stock quantities
#         for item in sale_items:
#             stock = Stock.objects.filter(id=item.stock.id, is_deleted=False).first()
#             if stock:
#                 stock.quantity += item.quantity
#                 stock.save()
#
#         # Delete sale items and sale bill
#         sale_items.delete()
#         sale_bill.delete()
#
#         # Add a success message
#         messages.success(request, "Sale bill has been deleted successfully")
#
#         # Redirect after deletion
#         return redirect('/transactions/sales')


class SaleDeleteView(LoginRequiredMixin, View):
    template_name = "sales/delete_sale.html"
    login_url = '/index/'

    @staticmethod
    def _party_display_name(party_obj):
        if not party_obj:
            return ""
        for attr in ("name", "Comp_name", "Consumer", "company_name", "full_name"):
            value = getattr(party_obj, attr, None)
            if value:
                return str(value)
        first_name = (getattr(party_obj, "first_name", "") or "").strip()
        last_name = (getattr(party_obj, "last_name", "") or "").strip()
        full_name = f"{first_name} {last_name}".strip()
        if full_name:
            return full_name
        return str(party_obj)

    def _linked_final_sale_refs_for_sale_bill(self, sale_bill):
        linked_final_bills = []
        if sale_bill.final_salebill_id:
            linked_final_bills.append(sale_bill.final_salebill)

        serial_linked_bills = (
            PurchaseSerial.objects.filter(sales_billno=sale_bill, final_salebill__isnull=False)
            .select_related("final_salebill__customer", "final_salebill__vendor")
            .values_list("final_salebill_id", flat=True)
            .distinct()
        )
        if serial_linked_bills:
            linked_final_bills.extend(
                FinalSale.objects.filter(billno__in=serial_linked_bills)
                .select_related("customer", "vendor")
                .order_by("billno")
            )

        final_bill_refs = []
        seen_final_billnos = set()
        for final_bill in linked_final_bills:
            if not final_bill or final_bill.billno in seen_final_billnos:
                continue
            seen_final_billnos.add(final_bill.billno)
            party = final_bill.customer or final_bill.vendor
            party_name = self._party_display_name(party)
            final_bill_refs.append(
                f"{final_bill.billno} ({party_name})" if party_name else f"{final_bill.billno}"
            )
        return final_bill_refs

    def get(self, request, *args, **kwargs):
        # Display the confirmation page
        sale_bill = get_object_or_404(SaleBill, pk=kwargs['pk'])
        final_bill_refs = self._linked_final_sale_refs_for_sale_bill(sale_bill)
        if final_bill_refs:
            error_message = "\n".join(
                [
                    f"Cannot delete Sale Bill {sale_bill.billno}.",
                    "This bill is already used in Final Sale Bill:",
                    f"Final Sale Bills: {', '.join(final_bill_refs)}",
                ]
            )
            messages.error(request, error_message)
            return redirect('/transactions/sales')
        return render(request, self.template_name, {'sale_bill': sale_bill})

    def post(self, request, *args, **kwargs):
        # Perform the deletion and stock update
        sale_bill = get_object_or_404(SaleBill, pk=kwargs['pk'])

        final_bill_refs = self._linked_final_sale_refs_for_sale_bill(sale_bill)

        if final_bill_refs:
            error_message = "\n".join(
                [
                    f"Cannot delete Sale Bill {sale_bill.billno}.",
                    "This bill is already used in Final Sale Bill:",
                    f"Final Sale Bills: {', '.join(final_bill_refs)}",
                ]
            )
            messages.error(request, error_message)
            return render(
                request,
                self.template_name,
                {
                    "sale_bill": sale_bill,
                    "delete_error_message": error_message,
                },
            )

        sale_items = SaleItem.objects.filter(billno=sale_bill.billno)

        # Restore stock quantities
        for item in sale_items:
            stock = Stock.objects.filter(id=item.stock.id, is_deleted=False).first()
            if stock:
                stock.quantity += item.quantity
                stock.save()

            # Set related PurchaseSerial.sales_billno to Null (instead of deleting PurchaseSerial records)
            purchase_serials = PurchaseSerial.objects.filter(stock=stock, sales_billno=sale_bill)
            for ps in purchase_serials:
                ps.sales_billno = None  # Set to Null
                ps.save()

        # Delete sale items and sale bill
        sale_items.delete()
        # sale_bill.delete()
        sale_bill.is_deleted = True
        sale_bill.save()

        # Add a success message
        messages.success(request, "Sale bill has been deleted successfully")

        # Redirect after deletion
        return redirect('/transactions/sales')



# used to display the purchase bill object
class PurchaseBillView(LoginRequiredMixin, View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            # 'items': PurchaseItem.objects.filter(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno).prefetch_related('purchaseserial_set'),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)

            billdetailsobj.eway = request.POST.get("eway")
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.cgst = request.POST.get("handby")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            # billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("bill_date")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
        }
        return render(request, self.template_name, context)



def _sale_bill_for_display(billno):
    """
    Return one SaleBill for this bill number. If the DB has duplicate rows with the
    same billno (e.g. sequence/PK drift), prefer the most recently created/updated row.
    """
    return (
        SaleBill.objects.filter(billno=billno)
        .order_by("-time", "-update_time", "-billno")
        .first()
    )


class SaleBillView(LoginRequiredMixin, View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        bill = _sale_bill_for_display(billno)
        if bill is None:
            messages.error(request, "Sale bill not found.")
            return redirect('some-other-view-name')  # Redirect to a fallback view

        items = SaleItem.objects.filter(billno=bill)

        # For each item, retrieve the related serial numbers from PurchaseSerial
        for item in items:
            item.serials = PurchaseSerial.objects.filter(
                stock=item.stock, sales_billno=bill, return_bill=None
            )

        billdetails = (
            SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
        )
        if billdetails is None:
            messages.error(request, "Sale bill details not found.")
            return redirect('some-other-view-name')

        context = {
            "bill": bill,
            "items": items,
            "billdetails": billdetails,
            "bill_base": self.bill_base,
        }
        return render(request, self.template_name, context)

#
# # used to display the sale bill object
# class SaleBillView(View):
#     model = SaleBill
#     template_name = "bill/sale_bill.html"
#     bill_base = "bill/bill_base.html"
#
#     def get(self, request, billno):
#         context = {
#             'bill': SaleBill.objects.get(billno=billno),
#             'items': SaleItem.objects.filter(billno=billno),
#             'billdetails': SaleBillDetails.objects.get(billno=billno),
#             'bill_base': self.bill_base,
#         }
#         return render(request, self.template_name, context)

    def post(self, request, billno):
        bill = _sale_bill_for_display(billno)
        if bill is None:
            messages.error(request, "Sale bill not found.")
            return redirect("some-other-view-name")

        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = (
                SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
            )
            if billdetailsobj:
                billdetailsobj.eway = request.POST.get("eway")
                billdetailsobj.veh = request.POST.get("veh")
                billdetailsobj.destination = request.POST.get("destination")
                billdetailsobj.po = request.POST.get("po")
                billdetailsobj.cgst = request.POST.get("cgst")
                billdetailsobj.sgst = request.POST.get("sgst")
                billdetailsobj.igst = request.POST.get("igst")
                billdetailsobj.cess = request.POST.get("cess")
                billdetailsobj.tcs = request.POST.get("tcs")
                billdetailsobj.total = request.POST.get("total")

                billdetailsobj.save()
                messages.success(
                    request, "Bill details have been modified successfully"
                )

        billdetails = (
            SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
        )
        context = {
            "bill": bill,
            "items": SaleItem.objects.filter(billno=bill),
            "billdetails": billdetails,
            "bill_base": self.bill_base,
        }
        return render(request, self.template_name, context)

    # class SaleBillView(View):
    #     model = SaleBill
    #     template_name = "bill/sale_bill.html"
    #     bill_base = "bill/bill_base.html"
    #
    #     def get(self, request, billno):
    #         items = SaleItem.objects.filter(billno=billno)
    #
    #         # For each item, retrieve the related serial numbers from PurchaseSerial
    #         for item in items:
    #             item.serials = PurchaseSerial.objects.filter(stock=item.stock, sales_billno=billno)
    #
    #         try:
    #             context = {
    #                 'bill': SaleBill.objects.get(billno=billno),
    #                 'items': items,
    #                 'billdetails': SaleBillDetails.objects.get(billno=billno),
    #                 'bill_base': self.bill_base,
    #                 # 'item.serials': item.serials,
    #             }
    #             return render(request, self.template_name, context)
    #         except SaleBill.DoesNotExist:
    #             messages.error(request, "Sale bill not found.")
    #             return redirect('some-other-view-name')  # Redirect to a fallback view
    #
    #     #
    #     # # used to display the sale bill object
    #     # class SaleBillView(View):
    #     #     model = SaleBill
    #     #     template_name = "bill/sale_bill.html"
    #     #     bill_base = "bill/bill_base.html"
    #     #
    #     #     def get(self, request, billno):
    #     #         context = {
    #     #             'bill': SaleBill.objects.get(billno=billno),
    #     #             'items': SaleItem.objects.filter(billno=billno),
    #     #             'billdetails': SaleBillDetails.objects.get(billno=billno),
    #     #             'bill_base': self.bill_base,
    #     #         }
    #     #         return render(request, self.template_name, context)
    #
    #     def post(self, request, billno):
    #         form = SaleDetailsForm(request.POST)
    #         if form.is_valid():
    #             billdetailsobj = SaleBillDetails.objects.get(billno=billno)
    #
    #             billdetailsobj.eway = request.POST.get("eway")
    #             billdetailsobj.veh = request.POST.get("veh")
    #             billdetailsobj.destination = request.POST.get("destination")
    #             billdetailsobj.po = request.POST.get("po")
    #             billdetailsobj.cgst = request.POST.get("cgst")
    #             billdetailsobj.sgst = request.POST.get("sgst")
    #             billdetailsobj.igst = request.POST.get("igst")
    #             billdetailsobj.cess = request.POST.get("cess")
    #             billdetailsobj.tcs = request.POST.get("tcs")
    #             billdetailsobj.total = request.POST.get("total")
    #
    #             billdetailsobj.save()
    #             messages.success(request, "Bill details have been modified successfully")
    #         context = {
    #             'bill': SaleBill.objects.get(billno=billno),
    #             'items': SaleItem.objects.filter(billno=billno),
    #             'billdetails': SaleBillDetails.objects.get(billno=billno),
    #             'bill_base': self.bill_base,
    #         }
    #         return render(request, self.template_name, context)


class SaleBillView_bill(LoginRequiredMixin, View):
        model = SaleBill
        template_name = "bill/sale_bill_bill.html"
        bill_base = "bill/bill_base.html"
        login_url = '/index/'

        def get(self, request, billno):
            bill = _sale_bill_for_display(billno)
            if bill is None:
                messages.error(request, "Sale bill not found.")
                return redirect("some-other-view-name")

            items = SaleItem.objects.filter(billno=bill)

            for item in items:
                item.serials = PurchaseSerial.objects.filter(
                    stock=item.stock, sales_billno=bill
                )

            billdetails = (
                SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
            )
            if billdetails is None:
                messages.error(request, "Sale bill details not found.")
                return redirect("some-other-view-name")

            context = {
                "bill": bill,
                "items": items,
                "billdetails": billdetails,
                "bill_base": self.bill_base,
            }
            return render(request, self.template_name, context)

        #
        # # used to display the sale bill object
        # class SaleBillView(View):
        #     model = SaleBill
        #     template_name = "bill/sale_bill.html"
        #     bill_base = "bill/bill_base.html"
        #
        #     def get(self, request, billno):
        #         context = {
        #             'bill': SaleBill.objects.get(billno=billno),
        #             'items': SaleItem.objects.filter(billno=billno),
        #             'billdetails': SaleBillDetails.objects.get(billno=billno),
        #             'bill_base': self.bill_base,
        #         }
        #         return render(request, self.template_name, context)

        def post(self, request, billno):
            bill = _sale_bill_for_display(billno)
            if bill is None:
                messages.error(request, "Sale bill not found.")
                return redirect("some-other-view-name")

            form = SaleDetailsForm(request.POST)
            if form.is_valid():
                billdetailsobj = (
                    SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
                )
                if billdetailsobj:
                    billdetailsobj.eway = request.POST.get("eway")
                    billdetailsobj.veh = request.POST.get("veh")
                    billdetailsobj.destination = request.POST.get("destination")
                    billdetailsobj.po = request.POST.get("po")
                    billdetailsobj.cgst = request.POST.get("cgst")
                    billdetailsobj.sgst = request.POST.get("sgst")
                    billdetailsobj.igst = request.POST.get("igst")
                    billdetailsobj.cess = request.POST.get("cess")
                    billdetailsobj.tcs = request.POST.get("tcs")
                    billdetailsobj.total = request.POST.get("total")

                    billdetailsobj.save()
                    messages.success(
                        request, "Bill details have been modified successfully"
                    )

            billdetails = (
                SaleBillDetails.objects.filter(billno=bill).order_by("-id").first()
            )
            context = {
                "bill": bill,
                "items": SaleItem.objects.filter(billno=bill),
                "billdetails": billdetails,
                "bill_base": self.bill_base,
            }
            return render(request, self.template_name, context)


from django.shortcuts import render, get_object_or_404
from .models import SaleBill, SaleItem, SaleBillDetails

#
# def edit_sale_view(request, pk):
#     # Fetch the SaleBill instance
#     sale_bill = get_object_or_404(SaleBill, pk=pk)
#
#     # Fetch related SaleBillDetails and SaleItems
#     sale_details = SaleBillDetails.objects.filter(billno=sale_bill)
#     sale_items = SaleItem.objects.filter(billno=sale_bill)
#
#     context = {
#         'sale_bill': sale_bill,
#         'sale_details': sale_details,
#         'sale_items': sale_items,
#     }
#
#     if request.method == "POST":
#         # Handle form submission to update records
#         # Update SaleBill, SaleBillDetails, and SaleItems
#         sale_bill.name = request.POST.get("name")
#         sale_bill.phone = request.POST.get("phone")
#         sale_bill.address = request.POST.get("address")
#         sale_bill.email = request.POST.get("email")
#         sale_bill.gstin = request.POST.get("gstin")
#         sale_bill.save()
#
#         # Update related SaleItems
#         for item in sale_items:
#             item.quantity = request.POST.get(f'quantity_{item.pk}')
#             item.totalprice = request.POST.get(f'totalprice_{item.pk}')
#             item.save()
#
#         # Redirect to a success page or refresh the current page
#         return redirect('sales-list')  # Replace with your sales list URL name
#
#     return render(request, 'sales/edit_sale.html', context)


# def edit_sale_view(request, pk):
#     # Fetch the SaleBill based on the primary key
#     sale_bill = get_object_or_404(SaleBill, pk=pk)
#
#     # Fetch related SaleItems
#     sale_items = SaleItem.objects.filter(billno=sale_bill)
#
#     # Fetch SaleBillDetails
#     try:
#         sale_bill_details = SaleBillDetails.objects.get(billno=sale_bill)
#     except SaleBillDetails.DoesNotExist:
#         sale_bill_details = None
#
#     # Fetch categories, subcategories, and stocks
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.all()
#
#     context = {
#         'sale_bill': sale_bill,
#         'sale_items': sale_items,
#         'sale_bill_details': sale_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#     }
#     return render(request, 'sales/edit_sale.html', context)
#


# def get_serial_numbers_edit(request):
#     stock_id = request.GET.get('stock_id')
#     sales_billno = request.GET.get('sales_billno')
#     if not stock_id:
#         return JsonResponse({'serial_numbers': []})
#
#     # Fetch serial numbers from PurchaseSerial table
#     serials = PurchaseSerial.objects.filter(stock_id=stock_id).values('serialNo', 'sales_billno')
#
#     # Build response with 'checked' status based on whether sales_billno is not None
#     serial_numbers = [
#         {'serialNo': serial['serialNo'], 'checked': serial['sales_billno'] is not None}
#          for serial in serials
#     ]
#     return JsonResponse({'serial_numbers': serial_numbers})



# def get_serial_numbers_edit(request):
#     stock_id = request.GET.get('stock_id')
#     sales_billno = request.GET.get('sales_billno')  # Current bill number
#     print(sales_billno)
#
#     if sales_billno and sales_billno.startswith("Bill no: "):
#         sales_billno = sales_billno.replace("Bill no: ", "")
#
#     try:
#         sales_billno = int(sales_billno)  # Convert to integer
#     except (ValueError, TypeError):
#         return JsonResponse({"error": "Invalid sales bill number"}, status=400)
#
#     if not stock_id or not sales_billno:
#         return JsonResponse({'serial_numbers': []})
#
#     # Fetch serial numbers for the current stock and current sales bill number
#     serials = PurchaseSerial.objects.filter(stock_id=stock_id)
#     # Fetch serial numbers based on stock_id and sales_billno
#     serials = PurchaseSerial.objects.filter(stock_id=stock_id)
#
#     # Include 'checked' status only for the current bill number
#     serial_numbers = [
#         {
#             'serialNo': serial['sales_billno'],
#             'checked': serial['sales_billno'] == sales_billno  # Check if the sales_billno matches the current bill
#         }
#         for serial in serials.values('serialNo', 'sales_billno')
#     ]
#
#     return JsonResponse({'serial_numbers': serial_numbers})


from django.db import models  # Ensure Q is imported correctly

@login_required(login_url='user-login')
def get_serial_numbers_edit(request):
    stock_id = request.GET.get('stock_id')  # Get the stock ID
    sales_billno = request.GET.get('sales_billno')  # Current bill number

    # Debugging log to print the sales bill number
    # print(f"Sales Bill Number: {sales_billno}")


    # Sanitize and extract the numeric part of the sales_billno
    if sales_billno and sales_billno.startswith("Bill no: "):
        sales_billno = sales_billno.replace("Bill no: ", "")

    try:
        sales_billno = int(sales_billno)  # Ensure it's an integer
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid sales bill number"}, status=400)

    # Return empty result if stock_id is missing
    if not stock_id:
        return JsonResponse({'serial_numbers': []})

    # Fetch records matching the sales_billno or where sales_billno is NULL
    serials = PurchaseSerial.objects.filter(
        stock_id=stock_id
    ).filter(
        models.Q(sales_billno=sales_billno) | models.Q(sales_billno__isnull=True)
    )

    # Construct response with the required fields
    serial_numbers = [
        {
            'serialNo': serial['serialNo'],  # Ensure 'serialNo' field is used
            'checked': serial['sales_billno'] == sales_billno,  # Check if the sales_billno matches the current bill
            'billno': serial['billno__billno'],
        }
        for serial in serials.values('serialNo', 'sales_billno', 'billno__billno')  # Fetch necessary fields
    ]

    grouped = {}
    for row in serial_numbers:
        bill_no = str(row.get('billno') or 'N/A')
        grouped.setdefault(bill_no, 0)
        grouped[bill_no] += 1

    grouped_by_bill = [
        {'billno': bill_no, 'serial_count': count}
        for bill_no, count in grouped.items()
    ]

    return JsonResponse({'serial_numbers': serial_numbers, 'grouped_by_bill': grouped_by_bill})


@login_required(login_url='user-login')
def final_get_serial_numbers_edit(request):
    stock_id = request.GET.get('stock_id')  # Get the stock ID
    sales_billno = request.GET.get('sales_billno')  # Current bill number

    # Debugging log to print the sales bill number
    # print(f"Sales Bill Number: {sales_billno}")

    # Sanitize and extract the numeric part of the sales_billno
    if sales_billno and sales_billno.startswith("Final Bill No: "):
        sales_billno = sales_billno.replace("Final Bill No: ", "")

    try:
        sales_billno = int(sales_billno)  # Ensure it's an integer
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid sales bill number"}, status=400)

    # Return empty result if stock_id is missing
    if not stock_id:
        return JsonResponse({'serial_numbers': []})

    # Fetch records matching the sales_billno or where sales_billno is NULL
    serials = PurchaseSerial.objects.filter(stock_id=stock_id).filter(models.Q(final_salebill=sales_billno))

    # Construct response with the required fields
    serial_numbers = [
        {
            'serialNo': serial['serialNo'],  # Ensure 'serialNo' field is used
            'checked': serial['final_salebill'] == sales_billno  # Check if the sales_billno matches the current bill
        }
        for serial in serials.values('serialNo', 'final_salebill')  # Fetch necessary fields
    ]

    return JsonResponse({'serial_numbers': serial_numbers})




# @login_required(login_url='user-login')
# def return_get_serial_numbers_edit(request):
#     stock_id = request.GET.get('stock_id')  # Get the stock ID
#     sales_billno = request.GET.get('sales_billno')  # Current bill number
#
#     # Debugging log to print the sales bill number
#     # print(f"Sales Bill Number: {sales_billno}")
#
#     # Sanitize and extract the numeric part of the sales_billno
#     if sales_billno and sales_billno.startswith("Final Bill No: "):
#         sales_billno = sales_billno.replace("Final Bill No: ", "")
#
#     try:
#         sales_billno = int(sales_billno)  # Ensure it's an integer
#     except (ValueError, TypeError):
#         return JsonResponse({"error": "Invalid sales bill number"}, status=400)
#
#     # Return empty result if stock_id is missing
#     if not stock_id:
#         return JsonResponse({'serial_numbers': []})
#
#     # Fetch records matching the sales_billno or where sales_billno is NULL
#     # serials = PurchaseSerial.objects.filter(stock_id=stock_id).filter(models.Q(final_salebill=sales_billno))
#
#     serials = PurchaseSerial.objects.filter(stock_id=stock_id, return_bill__isnull=False).filter(models.Q(final_salebill=sales_billno))
#
#     # Construct response with the required fields
#     serial_numbers = [
#         {
#             'serialNo': serial['serialNo'],  # Ensure 'serialNo' field is used
#             'checked': serial['final_salebill'] == sales_billno  # Check if the sales_billno matches the current bill
#         }
#         for serial in serials.values('serialNo', 'final_salebill')  # Fetch necessary fields
#     ]
#
#     return JsonResponse({'serial_numbers': serial_numbers})

#
# @login_required(login_url='user-login')
# def return_get_serial_numbers_edit(request):
#     stock_id = request.GET.get('stock_id')
#     sales_billno = request.GET.get('sales_billno')
#
#     if not stock_id or not sales_billno:
#         return JsonResponse({'serial_numbers': []})
#
#     # Clean the sales_billno if it has prefix
#     if sales_billno.startswith("Final Bill No: "):
#         sales_billno = sales_billno.replace("Final Bill No: ", "")
#
#     try:
#         sales_billno = int(sales_billno)
#     except (ValueError, TypeError):
#         return JsonResponse({"error": "Invalid sales bill number"}, status=400)
#
#     # Get current return bill number from request if available
#     current_return_billno = request.GET.get('return_billno', None)
#
#     # Get serials already assigned to THIS return bill (should be checked)
#     assigned_serials = PurchaseSerial.objects.filter(
#         stock_id=stock_id,
#         final_salebill=sales_billno
#     ).exclude(return_bill__isnull=True)
#
#     if current_return_billno:
#         assigned_serials = assigned_serials.filter(return_bill__billno=current_return_billno)
#
#     assigned_serials = assigned_serials.values_list('serialNo', flat=True)
#
#     # Get all serials from the original sale (final bill) that could be returned
#     # These are serials from the same final bill but not in any return bill
#     available_serials = PurchaseSerial.objects.filter(
#         stock_id=stock_id,
#         final_salebill=sales_billno,
#         return_bill__isnull=True
#     ).values_list('serialNo', flat=True)
#
#     # Combine results - assigned serials come first
#     serial_numbers = []
#
#     # Add assigned serials (checked)
#     for serial in assigned_serials:
#         serial_numbers.append({
#             'serialNo': serial,
#             'checked': True,
#             'type': 'assigned'
#         })
#
#     # Add available serials (unchecked)
#     for serial in available_serials:
#         serial_numbers.append({
#             'serialNo': serial,
#             'checked': False,
#             'type': 'available'
#         })


@login_required(login_url='user-login')
def return_get_serial_numbers_edit(request):
    stock_id = request.GET.get('stock_id')
    sales_billno = request.GET.get('sales_billno')
    return_billno = request.GET.get('return_billno')

    if not stock_id or not sales_billno:
        return JsonResponse({'serial_numbers': []})

    # Clean the sales_billno if it has prefix
    if sales_billno.startswith("Final Bill No: "):
        sales_billno = sales_billno.replace("Final Bill No: ", "")

    try:
        sales_billno = int(sales_billno)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid sales bill number"}, status=400)

    # Get serials assigned to THIS return bill (should be checked)
    assigned_query = PurchaseSerial.objects.filter(
        stock_id=stock_id,
        final_salebill=sales_billno
    )

    if return_billno:
        assigned_query = assigned_query.filter(return_bill__billno=return_billno)
    else:
        assigned_query = assigned_query.exclude(return_bill__isnull=True)

    assigned_serials = assigned_query.values_list('serialNo', flat=True)

    # Get available serials (from original sale, not in any return bill)
    available_serials = PurchaseSerial.objects.filter(
        stock_id=stock_id,
        final_salebill=sales_billno,
        return_bill__isnull=True
    ).values_list('serialNo', flat=True)

    # Combine results
    serial_numbers = []

    # Add assigned serials (checked)
    for serial in assigned_serials:
        serial_numbers.append({
            'serialNo': serial,
            'checked': True,
            'type': 'assigned'
        })

    # Add available serials (unchecked)
    for serial in available_serials:
        serial_numbers.append({
            'serialNo': serial,
            'checked': False,
            'type': 'available'
        })

    return JsonResponse({'serial_numbers': serial_numbers})


#     return JsonResponse({'serial_numbers': serial_numbers})

#
# @login_required(login_url='user-login')
# def return_get_serial_numbers_edit(request):
#     stock_id = request.GET.get('stock_id')
#     sales_billno = request.GET.get('sales_billno')
#     return_billno = request.GET.get('return_billno')
#
#     if not stock_id or not sales_billno:
#         return JsonResponse({'serial_numbers': []})
#
#     # Clean the sales_billno if it has prefix
#     if sales_billno.startswith("Final Bill No: "):
#         sales_billno = sales_billno.replace("Final Bill No: ", "")
#
#     try:
#         sales_billno = int(sales_billno)
#     except (ValueError, TypeError):
#         return JsonResponse({"error": "Invalid sales bill number"}, status=400)
#
#     # Get serials assigned to THIS return bill (should be checked)
#     assigned_query = PurchaseSerial.objects.filter(
#         stock_id=stock_id,
#         final_salebill=sales_billno
#     )
#
#     if return_billno:
#         assigned_query = assigned_query.filter(return_bill__billno=return_billno)
#     else:
#         assigned_query = assigned_query.exclude(return_bill__isnull=True)
#
#     assigned_serials = assigned_query.values_list('serialNo', flat=True)
#
#     # Get available serials (from original sale, not in any return bill)
#     available_serials = PurchaseSerial.objects.filter(
#         stock_id=stock_id,
#         final_salebill=sales_billno,
#         return_bill__isnull=True
#     ).values_list('serialNo', flat=True)
#
#     # Combine results
#     serial_numbers = []
#
#     # Add assigned serials (checked)
#     for serial in assigned_serials:
#         serial_numbers.append({
#             'serialNo': serial,
#             'checked': True,
#             'type': 'assigned'
#         })
#
#     # Add available serials (unchecked)
#     for serial in available_serials:
#         serial_numbers.append({
#             'serialNo': serial,
#             'checked': False,
#             'type': 'available'
#         })
#
#     return JsonResponse({'serial_numbers': serial_numbers})

from django.views.decorators.http import require_POST
import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

@require_POST
@login_required(login_url='user-login')
def update_selected_serials(request):
    data = json.loads(request.body)

    selected_serial_ids = data.get("selected_serial_ids", [])  # Expecting a list of IDs
    return_billno = data.get("return_billno")

    if not (selected_serial_ids and return_billno):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        return_bill = ReturnSale.objects.get(billno=return_billno)
    except ReturnSale.DoesNotExist:
        return JsonResponse({"error": "Return bill not found"}, status=404)

    # ✅ Update only the selected serials, and only if return_bill_id is currently NULL
    updated_count = PurchaseSerial.objects.filter(
        id__in=selected_serial_ids,
        return_bill__isnull=True
    ).update(return_bill=return_bill)

    return JsonResponse({
        "message": "Selected serials updated successfully",
        "updated_count": updated_count
    })


#
# from django.http import JsonResponse
#
#
# def get_serial_numbers(request):
#     stock_id = request.GET.get('stock_id')
#     if not stock_id:
#         return JsonResponse({'serial_numbers': []})
#
#     # Fetch serial numbers from PurchaseSerial table
#     serials = PurchaseSerial.objects.filter(stock_id=stock_id).values('serialNo', 'sales_billno')
#
#     # Build response with 'checked' status and disabled status based on 'sales_billno'
#     serial_numbers = [
#         {
#             'serialNo': serial['serialNo'],
#             'checked': serial['sales_billno'] is not None,
#             'disabled': serial['sales_billno'] is not None  # Mark as disabled if sales_billno is set
#         }
#         for serial in serials
#     ]
#     return JsonResponse({'serial_numbers': serial_numbers})


@login_required(login_url='user-login')
def update_sales_billno_edit(request):
    if request.method == 'POST':
        checked_serial_numbers = json.loads(request.POST.get('checkedSerialNumbers', '[]'))
        unchecked_serial_numbers = json.loads(request.POST.get('uncheckedSerialNumbers', '[]'))
        sales_billno = request.POST.get('sales_billno')

        # Update checked serial numbers with the sales bill number
        if checked_serial_numbers:
            PurchaseSerial.objects.filter(serialNo__in=checked_serial_numbers).update(sales_billno=sales_billno)

        # Update unchecked serial numbers to have serialNo set to None
        if unchecked_serial_numbers:
            PurchaseSerial.objects.filter(serialNo__in=unchecked_serial_numbers).update(sales_billno=None)

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required(login_url='user-login')
def edit_sale_view(request, pk):
    sale_bill = get_object_or_404(SaleBill, pk=pk)
    sale_items = SaleItem.objects.filter(billno=sale_bill)

    # For each item, retrieve the related serial numbers from PurchaseSerial
    for item in sale_items:
        item.serials = PurchaseSerial.objects.filter(stock=item.stock, sales_billno=pk)

    try:
        sale_bill_details = SaleBillDetails.objects.get(billno=sale_bill)
    except SaleBillDetails.DoesNotExist:
        sale_bill_details = None

    existing_stock_ids = sale_items.values_list('stock_id', flat=True)
    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.for_forms_dropdown()

    context = {
        'sale_bill': sale_bill,
        'sale_items': sale_items,
        'sale_bill_details': sale_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
        'existing_stock_ids': list(existing_stock_ids),
    }

    if request.method == "POST":
        # Update SaleBill fields
        sale_bill.name = request.POST.get("name", sale_bill.name)
        sale_bill.phone = request.POST.get("phone", sale_bill.phone)
        sale_bill.address = request.POST.get("address", sale_bill.address)
        sale_bill.email = request.POST.get("email", sale_bill.email)
        sale_bill.gstin = request.POST.get("gstin", sale_bill.gstin)
        sale_bill.update_time = timezone.now()
        sale_bill.save()

        # Update SaleBillDetails fields
        if sale_bill_details:
            sale_bill_details.eway = request.POST.get("eway_no", sale_bill_details.eway)
            sale_bill_details.cgst = request.POST.get("bill_date", sale_bill_details.tcs)
            sale_bill_details.veh = request.POST.get("veh_no", sale_bill_details.veh)
            sale_bill_details.sgst = request.POST.get("arrange", sale_bill_details.sgst)
            sale_bill_details.igst = request.POST.get("handby", sale_bill_details.igst)
            sale_bill_details.destination = request.POST.get("destination", sale_bill_details.destination)
            sale_bill_details.po = request.POST.get("po_no", sale_bill_details.po)
            sale_bill_details.tcs = request.POST.get("po_date", sale_bill_details.cgst)
            sale_bill_details.save()

        # Update SaleItems and Stock
        serials_data = {
            key.split('-')[1]: value.split(',')
            for key, value in request.POST.items() if key.startswith('serials-')
        }


        for stock_id, serial_numbers in serials_data.items():
            PurchaseSerial.objects.filter(stock_id=stock_id, sales_billno=sale_bill.billno).update(sales_billno=None)
            PurchaseSerial.objects.filter(
                stock_id=stock_id,
                serialNo__in=serial_numbers
            ).update(sales_billno=sale_bill.billno)


        for item in sale_items:
            quantity = request.POST.get(f'quantity_{item.pk}')
            if quantity:
                previous_quantity = item.quantity
                item.quantity = Decimal(quantity)

                # Update the sale field to match the stock
                item.sale = item.stock.sales

                item.save()

                stock = item.stock
                stock_quantity = stock.quantity
                quantity_change = item.quantity - previous_quantity
                stock.quantity = stock_quantity - quantity_change
                stock.save()

        # Process new items
        new_stock_ids = request.POST.getlist("stock_ids[]")
        new_quantities = request.POST.getlist("quantities[]")
        for stock_id, quantity in zip(new_stock_ids, new_quantities):
            stock = Stock.objects.get(pk=stock_id)

            SaleItem.objects.create(
                billno=sale_bill,
                stock=stock,
                quantity=Decimal(quantity),
                totalprice=1 * Decimal(quantity),  # Assuming `price` is handled
                sale=stock.sales,
            )
            stock.quantity -= Decimal(quantity)
            stock.save()

        # Handle removed items
        existing_ids = set(item.pk for item in sale_items)
        retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
        removed_ids = existing_ids - retained_ids

        for removed_id in removed_ids:
            item_to_remove = SaleItem.objects.get(pk=removed_id)
            stock = item_to_remove.stock
            quantity_to_remove = item_to_remove.quantity

            PurchaseSerial.objects.filter(
                stock=stock,
                sales_billno=sale_bill.billno
            ).update(sales_billno=None)

            stock.quantity += quantity_to_remove
            stock.save()
            item_to_remove.delete()

        return redirect('sales-list')

    return render(request, 'sales/edit_sale.html', context)


#
# @login_required(login_url='user-login')
# def purchase_edit_view(request, pk):
#     purchase_bill = get_object_or_404(PurchaseBill, pk=pk)
#     purchase_items = PurchaseItem.objects.filter(billno=purchase_bill)
#
#     # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in purchase_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, billno=pk)
#         item_serials = PurchaseSerial.objects.filter(item=item)
#
#     try:
#         purchase_bill_details = PurchaseBillDetails.objects.get(billno=purchase_bill)
#     except PurchaseBillDetails.DoesNotExist:
#         purchase_bill_details = None
#
#     existing_stock_ids = purchase_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     context = {
#         'purchase_bill': purchase_bill,
#         'purchase_items': purchase_items,
#         'purchase_bill_details': purchase_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#         'existing_stock_ids': list(existing_stock_ids),
#     }
#
#     if request.method == "POST":
#         # Update SaleBill fields
#         # purchase_bill.name = request.POST.get("name", purchase_bill.name)
#         # purchase_bill.phone = request.POST.get("phone", purchase_bill.phone)
#         # purchase_bill.address = request.POST.get("address", purchase_bill.address)
#         # purchase_bill.email = request.POST.get("email", purchase_bill.email)
#         # purchase_bill.gstin = request.POST.get("gstin", purchase_bill.gstin)
#         # purchase_bill.update_time = timezone.now()
#         # purchase_bill.save()
#
#         # Update PurchaseBillDetails fields
#         if purchase_bill_details:
#             purchase_bill_details.eway = request.POST.get("eway_no", purchase_bill_details.eway)
#             purchase_bill_details.tcs = request.POST.get("bill_date", purchase_bill_details.tcs)
#             purchase_bill_details.veh = request.POST.get("veh_no", purchase_bill_details.veh)
#             purchase_bill_details.sgst = request.POST.get("arrange", purchase_bill_details.sgst)
#             purchase_bill_details.igst = request.POST.get("handby", purchase_bill_details.igst)
#             purchase_bill_details.destination = request.POST.get("destination", purchase_bill_details.destination)
#             purchase_bill_details.po = request.POST.get("po_no", purchase_bill_details.po)
#             purchase_bill_details.cgst = request.POST.get("po_date", purchase_bill_details.cgst)
#             purchase_bill_details.final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#             purchase_bill_details.gst_value = request.POST.get("gst_values", purchase_bill_details.gst_value)
#             purchase_bill_details.gst_amount = request.POST.get("gst_amount", purchase_bill_details.gst_amount)
#             purchase_bill_details.total_amount = request.POST.get("total_amount", purchase_bill_details.total_amount)
#             purchase_bill_details.round_off = request.POST.get("round_off", purchase_bill_details.round_off)
#             purchase_bill_details.delivery_charges = request.POST.get("delivery_charges", purchase_bill_details.delivery_charges)
#             purchase_bill_details.save()
#
#         # Update PurchaseItems and Stock
#         serials_data = {
#             key.split('-')[1]: value.split(',')
#             for key, value in request.POST.items() if key.startswith('serials-')
#         }
#
#         for stock_id, serial_numbers in serials_data.items():
#             PurchaseSerial.objects.filter(stock_id=stock_id).update(sales_billno=None)
#             PurchaseSerial.objects.filter(
#                 stock_id=stock_id,
#                 serialNo__in=serial_numbers
#             ).update(billno=purchase_bill.billno)
#
#
#         for item in purchase_items:
#             quantity = request.POST.get(f'quantity_{item.pk}')
#             price = request.POST.get(f'perprice_{item.pk}')
#             if quantity and price:
#                 previous_quantity = item.quantity
#                 item.quantity = int(quantity)
#                 item.perprice = float(price)
#                 item.totalprice = item.quantity * item.perprice
#                 item.save()
#
#                 stock = item.stock
#                 stock_quantity = stock.quantity
#                 quantity_change = item.quantity - previous_quantity
#                 stock.quantity = stock_quantity + quantity_change
#                 stock.save()
#
#         # Process new items
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         new_prices = request.POST.getlist("perprices[]")  # Ensure your form provides perprices[] for new items.
#         # for stock_id, quantity in zip(new_stock_ids, new_quantities):
#         for stock_id, quantity, price in zip(new_stock_ids, new_quantities, new_prices):
#             stock = Stock.objects.get(pk=stock_id)
#             price_value = float(price)  # Convert price string to float.
#             PurchaseItem.objects.create(
#                 billno=purchase_bill,
#                 stock=stock,
#                 purchase=stock.purchase,
#                 quantity=int(quantity),
#                 perprice=price_value,
#                 # totalprice = item.quantity * item.perprice
#                 totalprice=price_value * int(quantity),  # Assuming `price` is handled
#                 # sale=stock.sales,
#             )
#
#             stock.quantity += int(quantity)
#             stock.save()
#
#         # Handle removed items
#         existing_ids = set(item.pk for item in purchase_items)
#         retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
#         removed_ids = existing_ids - retained_ids
#
#         for removed_id in removed_ids:
#             item_to_remove = PurchaseItem.objects.get(pk=removed_id)
#             stock = item_to_remove.stock
#             quantity_to_remove = item_to_remove.quantity
#
#             # PurchaseSerial.objects.filter(
#             #     stock=stock,
#             #     # billno=billno,
#             #     billno=purchase_bill.billno,
#             # ).update(billno=None)
#             PurchaseSerial.objects.filter(
#                 stock=stock,
#                 billno=purchase_bill,  # Use the instance, not purchase_bill.billno
#             ).delete()
#
#             stock.quantity -= quantity_to_remove
#             stock.save()
#             item_to_remove.delete()
#
#         return redirect('purchases-list')
#
#     return render(request, 'purchases/purchase_edit.html', context)



# @login_required(login_url='user-login')
# def purchase_edit_view(request, pk):
#     purchase_bill = get_object_or_404(PurchaseBill, pk=pk)
#     purchase_items = PurchaseItem.objects.filter(billno=purchase_bill)
#
#     # Attach existing serial numbers to each purchase item (for template display, if needed)
#     for item in purchase_items:
#         item.serials = PurchaseSerial.objects.filter(item=item)
#
#     try:
#         purchase_bill_details = PurchaseBillDetails.objects.get(billno=purchase_bill)
#     except PurchaseBillDetails.DoesNotExist:
#         purchase_bill_details = None
#
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     context = {
#         'purchase_bill': purchase_bill,
#         'purchase_items': purchase_items,
#         'purchase_bill_details': purchase_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#     }
#
#     if request.method == "POST":
#         # (1) Update PurchaseBillDetails fields
#         if purchase_bill_details:
#             purchase_bill_details.eway = request.POST.get("eway_no", purchase_bill_details.eway)
#             purchase_bill_details.tcs = request.POST.get("bill_date", purchase_bill_details.tcs)
#             purchase_bill_details.veh = request.POST.get("veh_no", purchase_bill_details.veh)
#             purchase_bill_details.sgst = request.POST.get("arrange", purchase_bill_details.sgst)
#             purchase_bill_details.igst = request.POST.get("handby", purchase_bill_details.igst)
#             purchase_bill_details.destination = request.POST.get("destination", purchase_bill_details.destination)
#             purchase_bill_details.po = request.POST.get("po_no", purchase_bill_details.po)
#             purchase_bill_details.cgst = request.POST.get("po_date", purchase_bill_details.cgst)
#             final_amount = request.POST.get('final_amount')
#             if final_amount:
#                 purchase_bill_details.final_amount = final_amount.replace('₹', '').strip()
#             purchase_bill_details.gst_value = request.POST.get("gst_values", purchase_bill_details.gst_value)
#             purchase_bill_details.gst_amount = request.POST.get("gst_amount", purchase_bill_details.gst_amount)
#             purchase_bill_details.total_amount = request.POST.get("total_amount", purchase_bill_details.total_amount)
#             purchase_bill_details.round_off = request.POST.get("round_off", purchase_bill_details.round_off)
#             purchase_bill_details.delivery_charges = request.POST.get("delivery_charges", purchase_bill_details.delivery_charges)
#             purchase_bill_details.save()
#
#         # (2) Build a dictionary of serial numbers from the POST data.
#         # The JS is appending hidden inputs with names like "serials-<stock_id>[]"
#         serials_data = {}
#         for key in request.POST:
#             if key.startswith("serials-"):
#                 # Remove any square brackets (if present) so that "serials-28[]" becomes "28"
#                 cleaned_key = key.split('-')[1].replace('[]', '')
#                 serials_data[cleaned_key] = request.POST.getlist(key)
#
#
#         # (3) Process serial numbers for existing purchase items.
#         for item in purchase_items:
#             stock_id_str = str(item.stock_id)
#             if stock_id_str in serials_data:
#                 submitted_serials = serials_data[stock_id_str]
#                 existing_serial_objs = PurchaseSerial.objects.filter(item=item)
#                 existing_serials = set(existing_serial_objs.values_list('serialNo', flat=True))
#                 # Delete any serials that were removed in the form
#                 for serial_obj in existing_serial_objs:
#                     if serial_obj.serialNo not in submitted_serials:
#                         serial_obj.delete()
#                 # Create new PurchaseSerial records for any serial that is newly submitted
#                 for serial in submitted_serials:
#                     if serial not in existing_serials:
#                         PurchaseSerial.objects.create(
#                             billno=purchase_bill,
#                             stock=item.stock,
#                             serialNo=serial,
#                             purchase=item.stock.purchase,
#                             item=item,
#                         )
#                 # Remove the key so that it isn’t processed again in the new items block.
#                 del serials_data[stock_id_str]
#
#         # (4) Update existing PurchaseItems (quantity, price, and stock adjustment)
#         for item in purchase_items:
#             quantity = request.POST.get(f'quantity_{item.pk}')
#             price = request.POST.get(f'perprice_{item.pk}')
#             if quantity and price:
#                 previous_quantity = item.quantity
#                 new_quantity = int(quantity)
#                 new_price = float(price)
#                 item.quantity = new_quantity
#                 item.perprice = new_price
#                 item.totalprice = new_quantity * new_price
#                 item.save()
#
#                 stock = item.stock
#                 stock.quantity += (new_quantity - previous_quantity)
#                 stock.save()
#
#         # (5) Process new items – these come from the new item inputs.
#         # new_stock_ids = request.POST.getlist("stock_ids[]")
#         # new_quantities = request.POST.getlist("quantities[]")
#         # new_prices = request.POST.getlist("perprices[]")
#         # for stock_id, quantity, price in zip(new_stock_ids, new_quantities, new_prices):
#         #     stock = Stock.objects.get(pk=stock_id)
#         #     new_quantity = int(quantity)
#         #     new_price = float(price)
#         #     new_item = PurchaseItem.objects.create(
#         #         billno=purchase_bill,
#         #         stock=stock,
#         #         purchase=stock.purchase,
#         #         quantity=new_quantity,
#         #         perprice=new_price,
#         #         totalprice=new_quantity * new_price,
#         #     )
#         #     stock.quantity += new_quantity
#         #     stock.save()
#         #
#         #     # Now check if serial numbers were submitted for this new item.
#         #     # Look up using the stock id as a string.
#         #     new_serials = serials_data.get(str(stock_id), [])
#         #     for serial in new_serials:
#         #         PurchaseSerial.objects.create(
#         #             billno=purchase_bill,
#         #             stock=stock,
#         #             serialNo=serial,
#         #             purchase=stock.purchase,
#         #             item=new_item,
#         #         )
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         new_prices = request.POST.getlist("perprices[]")
#         for stock_id, quantity, price in zip(new_stock_ids, new_quantities, new_prices):
#             stock = Stock.objects.get(pk=stock_id)
#             new_quantity = int(quantity)
#             new_price = float(price)
#             new_item = PurchaseItem.objects.create(
#                 billno=purchase_bill,
#                 stock=stock,
#                 purchase=stock.purchase,
#                 quantity=new_quantity,
#                 perprice=new_price,
#                 totalprice=new_quantity * new_price,
#             )
#             stock.quantity += new_quantity
#             stock.save()
#
#             # Look up serial numbers using the stock id as a string.
#             new_serials = serials_data.get(str(stock_id), [])
#             for serial in new_serials:
#                 PurchaseSerial.objects.create(
#                     billno=purchase_bill,
#                     stock=stock,
#                     serialNo=serial,
#                     purchase=stock.purchase,
#                     item=new_item,
#                 )
#             print("Serials Data:", serials_data)
#
#         # (6) Handle removed items.
#         existing_ids = set(item.pk for item in purchase_items)
#         retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
#         removed_ids = existing_ids - retained_ids
#         for removed_id in removed_ids:
#             item_to_remove = PurchaseItem.objects.get(pk=removed_id)
#             stock = item_to_remove.stock
#             quantity_to_remove = item_to_remove.quantity
#             # Remove all PurchaseSerial records associated with this bill and stock.
#             PurchaseSerial.objects.filter(stock=stock, billno=purchase_bill).delete()
#             stock.quantity -= quantity_to_remove
#             stock.save()
#             item_to_remove.delete()
#
#         return redirect('purchases-list')
#
#     return render(request, 'purchases/purchase_edit.html', context)


from django.db.models import Q

@login_required(login_url='user-login')
def purchase_edit_view(request, pk):
    purchase_bill = get_object_or_404(PurchaseBill, pk=pk)
    purchase_items = PurchaseItem.objects.filter(billno=purchase_bill)

    # Attach existing serial numbers to each purchase item (for template display, if needed)
    for item in purchase_items:
        item.serials = PurchaseSerial.objects.filter(item=item)

    try:
        purchase_bill_details = PurchaseBillDetails.objects.get(billno=purchase_bill)
    except PurchaseBillDetails.DoesNotExist:
        purchase_bill_details = None

    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.filter(is_deleted=False)

    context = {
        'purchase_bill': purchase_bill,
        'purchase_items': purchase_items,
        'purchase_bill_details': purchase_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
    }

    if request.method == "POST":
        gst_toggle = request.POST.get('gstToggle')

        # (1) Update PurchaseBillDetails fields
        if purchase_bill_details:
            purchase_bill_details.eway = request.POST.get("eway_no", purchase_bill_details.eway)
            purchase_bill_details.tcs = request.POST.get("bill_date", purchase_bill_details.tcs)
            purchase_bill_details.veh = request.POST.get("veh_no", purchase_bill_details.veh)
            purchase_bill_details.sgst = request.POST.get("arrange", purchase_bill_details.sgst)
            purchase_bill_details.igst = request.POST.get("handby", purchase_bill_details.igst)
            purchase_bill_details.destination = request.POST.get("destination", purchase_bill_details.destination)
            purchase_bill_details.po = request.POST.get("po_no", purchase_bill_details.po)
            purchase_bill_details.cgst = request.POST.get("po_date", purchase_bill_details.cgst)
            final_amount = request.POST.get('final_amount')
            if final_amount:
                purchase_bill_details.final_amount = final_amount.replace('₹', '').strip()
            if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
             purchase_bill_details.gst_value = request.POST.get("gst_values", purchase_bill_details.gst_value)
             purchase_bill_details.gst_amount = request.POST.get("gst_amount", purchase_bill_details.gst_amount)
            else:
                purchase_bill_details.gst_value = 0
                purchase_bill_details.gst_amount = 0
            purchase_bill_details.total_amount = request.POST.get("total_amount", purchase_bill_details.total_amount)
            purchase_bill_details.round_off = request.POST.get("round_off", purchase_bill_details.round_off)
            purchase_bill_details.delivery_charges = request.POST.get("delivery_charges", purchase_bill_details.delivery_charges)
            purchase_bill_details.save()

        # (2) Build a dictionary of serial numbers from the POST data.
        # The JS is appending hidden inputs with names like "serials-<stock_id>[]"
        serials_data = {}
        for key in request.POST:
            if key.startswith("serials-"):
                # Remove any square brackets (if present) so that "serials-28[]" becomes "28"
                cleaned_key = key.split('-')[1].replace('[]', '')
                # Filter out empty strings so only non-empty serial numbers remain.
                serials_data[cleaned_key] = [s.strip() for s in request.POST.getlist(key) if s.strip()]

        # (3) Process serial numbers for existing purchase items.
        for item in purchase_items:
            stock_id_str = str(item.stock_id)
            if stock_id_str in serials_data:
                # Use only non-empty submitted serials.
                submitted_serials = serials_data[stock_id_str]

                # First, remove any existing PurchaseSerial records that have an empty or null serialNo.
                PurchaseSerial.objects.filter(item=item).filter(Q(serialNo='') | Q(serialNo__isnull=True)).delete()

                # Now get the current non-empty serial numbers from the DB.
                existing_serial_objs = PurchaseSerial.objects.filter(item=item)
                existing_serials = set(existing_serial_objs.values_list('serialNo', flat=True))

                # Delete any serials that are no longer in the submitted list.
                for serial_obj in existing_serial_objs:
                    if serial_obj.serialNo not in submitted_serials:
                        serial_obj.delete()

                # Create new PurchaseSerial records for any submitted serial that isn’t already present.
                for serial in submitted_serials:
                    if serial not in existing_serials:
                        PurchaseSerial.objects.create(
                            billno=purchase_bill,
                            stock=item.stock,
                            serialNo=serial,
                            purchase=item.stock.purchase,
                            item=item,
                        )
                # Remove the key so that it isn’t processed in the new items block.
                del serials_data[stock_id_str]

        # (4) Update existing PurchaseItems (quantity, price, and stock adjustment)
        for item in purchase_items:
            quantity = request.POST.get(f'quantity_{item.pk}')
            price = request.POST.get(f'perprice_{item.pk}')
            if quantity and price:
                previous_quantity = item.quantity
                # new_quantity = int(quantity)
                # new_quantity = float(quantity)
                # new_price = float(price)
                new_quantity = Decimal(quantity)
                new_price = Decimal(price)
                item.quantity = new_quantity
                item.perprice = new_price
                item.totalprice = new_quantity * new_price
                item.save()

                stock = item.stock
                stock.quantity += (new_quantity - previous_quantity)
                stock.save()

        # (5) Process new items – these come from the new item inputs.
        new_stock_ids = request.POST.getlist("stock_ids[]")
        new_quantities = request.POST.getlist("quantities[]")
        new_prices = request.POST.getlist("perprices[]")
        for stock_id, quantity, price in zip(new_stock_ids, new_quantities, new_prices):
            stock = Stock.objects.get(pk=stock_id)
            # new_quantity = round(float(quantity))
            # new_price = float(price)
            new_quantity = Decimal(quantity)
            new_price = Decimal(price)
            new_item = PurchaseItem.objects.create(
                billno=purchase_bill,
                stock=stock,
                purchase=stock.purchase,
                quantity=new_quantity,
                perprice=new_price,
                totalprice=new_quantity * new_price,
            )
            stock.quantity += new_quantity
            stock.save()

            # Look up serial numbers for the new item using the stock id as a string.
            new_serials = serials_data.get(str(stock_id), [])
            for serial in new_serials:
                PurchaseSerial.objects.create(
                    billno=purchase_bill,
                    stock=stock,
                    serialNo=serial,
                    purchase=stock.purchase,
                    item=new_item,
                )

        # (6) Handle removed items.
        existing_ids = set(item.pk for item in purchase_items)
        retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
        removed_ids = existing_ids - retained_ids
        for removed_id in removed_ids:
            item_to_remove = PurchaseItem.objects.get(pk=removed_id)
            stock = item_to_remove.stock
            quantity_to_remove = item_to_remove.quantity
            # Remove all PurchaseSerial records associated with this bill and stock.
            PurchaseSerial.objects.filter(stock=stock, billno=purchase_bill).delete()
            stock.quantity -= quantity_to_remove
            stock.save()
            item_to_remove.delete()

        return redirect('purchases-list')

    return render(request, 'purchases/purchase_edit.html', context)



#
# def purchase_edit_sale_view(request, pk):
#     def get(self, request, pk):
#         # Fetch unread notifications count and the latest unread notifications
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         previous_bills = PurchaseBill.objects.filter(supplier=supplierobj).order_by('-billno')
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#             'previous_bills': previous_bills,
#             'count1': count1,  # Add the unread notification count
#             'notification1': notification1,  # Add the unread notifications
#         }
#         return render(request, 'purchases/purchase_edit.html', context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # Save PurchaseBill
#                     billobj = PurchaseBill(supplier=supplierobj)
#                     billobj.save()
#                     logger.info("PurchaseBill saved successfully")
#
#                     # Extract GST toggle state
#                     gst_toggle = request.POST.get('gstToggle')
#
#                     # Initialize GST values
#                     gst_value = 0
#                     gst_amount = 0
#                     eway_no = 0
#                     veh_no = 0
#                     hand_by = 0
#                     destination = 0
#                     po_no = 0
#                     po_date = 0
#                     round_off = request.POST.get('round_off')
#                     delivery_charges = request.POST.get('delivery_charges')
#                     final_amount = request.POST.get('final_amount').replace('₹', '').strip()
#                     eway_no = request.POST.get('eway_no')
#                     bill_date = request.POST.get('bill_date')
#                     veh_no = request.POST.get('veh_no')
#                     hand_by = request.POST.get('handby')
#                     destination = request.POST.get('destination')
#                     po_no = request.POST.get('po_no')
#                     po_date = request.POST.get('po_date')
#
#                     if gst_toggle == 'on':  # or 'true' based on how the toggle is set in your HTML
#                         gst_value = request.POST.get('gst_value')
#                         gst_amount = request.POST.get('gst_amount')
#
#                     # Save PurchaseBillDetails
#                     billdetailsobj = PurchaseBillDetails(
#                         billno=billobj,
#                         gst_value=gst_value,
#                         gst_amount=gst_amount,
#                         round_off=round_off,
#                         delivery_charges=delivery_charges,
#                         eway=eway_no,
#                         cgst=bill_date,
#                         veh=veh_no,
#                         igst=hand_by,
#                         destination=destination,
#                         po=po_no,
#                         tcs=po_date,
#                         final_amount=final_amount,
#                         total_amount=request.POST.get('total_amount'),
#                     )
#                     billdetailsobj.save()
#                     logger.info("PurchaseBillDetails saved successfully")
#
#                     # Save each PurchaseItem and update Stock
#                     for index, form in enumerate(formset):
#                         billitem = form.save(commit=False)
#                         billitem.billno = billobj
#
#                         # Get the associated stock
#                         stock = get_object_or_404(Stock, pk=billitem.stock.id)
#
#                         # Get the `short_name` from the form and look up the Unit instance
#                         short_name = request.POST.get('purchase_id')  # This assumes 'purchase' contains the short_name
#                         unit_instance = get_object_or_404(Unit, id=short_name)  # Query by short_name
#                         billitem.purchase = unit_instance
#
#                         # Calculate the total price for the item
#                         billitem.totalprice = billitem.perprice * billitem.quantity
#
#                         # Update stock quantity
#                         stock.quantity += billitem.quantity
#                         stock.save()
#                         logger.info(f"Stock updated successfully for stock id {stock.id}")
#
#                         # Save the PurchaseItem
#                         billitem.save()
#                         logger.info(f"PurchaseItem saved successfully for stock id {stock.id}")
#
#                         # Save PurchaseSerial entries
#                         serial_numbers = request.POST.getlist(f'serial_numbers_{index}[]')
#                         for serial_number in serial_numbers:
#                             purchase_serial = PurchaseSerial(
#                                 billno=billobj,
#                                 stock=stock,
#                                 purchase=unit_instance,
#                                 serialNo=serial_number,
#                                 item=billitem  # Link to the saved PurchaseItem
#                             )
#                             purchase_serial.save()
#                             logger.info(
#                                 f"PurchaseSerial saved successfully for stock id {stock.id} with serial number {serial_number}")
#
#                     # If everything goes well
#                     messages.success(request, "Purchased items have been registered successfully")
#                     return redirect('purchase-bill', billno=billobj.billno)
#
#             except Exception as e:
#                 logger.error(f"An error occurred: {str(e)}")
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             logger.warning(f"Formset is not valid: {formset.errors}")
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         # If form is not valid or any other error occurs
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#             'count1': count1,  # Add the unread notification count again
#             'notification1': notification1,  # Add the unread notifications again
#         }
#         return render(request, 'purchases/purchase_edit.html', context)
#
#
# def get_previous_bill_details(request):
#     bill_no = request.GET.get('bill_no')
#     bill = get_object_or_404(PurchaseBill, billno=bill_no)
#     items = PurchaseItem.objects.filter(billno=bill)
#     data = {
#         'items': [
#             {
#                 'stock_id': item.stock.id,
#                 'stock_name': item.stock.name,
#                 'stock_quantity': item.stock.quantity,
#                 'stock_alert': item.stock.alert_level,
#                 'purchase': item.purchase.short_name,
#                 'purchase_id': item.purchase.id,
#                 'quantity': item.quantity,
#                 'perprice': item.perprice,
#                 'totalprice': item.totalprice,
#                 'gst': item.stock.gst,
#             }
#             for item in items
#         ]
#     }
#     return JsonResponse(data)

#
# def edit_purchase_bill(request):
#     purchase_bills = PurchaseBill.objects.all()
#     return render(request, 'purchases/purchase_edit.html', {'purchase_bills': purchase_bills})
#
# def get_purchase_bill(request, bill_id):
#     bill = get_object_or_404(PurchaseBill, billno=bill_id)
#     items = PurchaseItem.objects.filter(billno=bill)
#     items_data = [{
#         # 'product_name': item.product_name,
#         'quantity': item.quantity,
#         # 'price': item.price
#     } for item in items]
#     return JsonResponse({'items': items_data})
#
# def update_purchase_bill(request):
#     if request.method == 'POST':
#         bill_id = request.POST.get('purchase_bill')
#         bill = get_object_or_404(PurchaseBill, id=bill_id)
#
#         # Clear old items
#         PurchaseItem.objects.filter(purchase_bill=bill).delete()
#
#         # Add updated items
#         product_names = request.POST.getlist('product_name')
#         quantities = request.POST.getlist('quantity')
#         prices = request.POST.getlist('price')
#
#         for name, qty, price in zip(product_names, quantities, prices):
#             PurchaseItem.objects.create(
#                 purchase_bill=bill,
#                 product_name=name,
#                 quantity=qty,
#                 price=price
#             )
#
#         return JsonResponse({'success': True})
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#
# def get_purchase_bill(request, bill_id):
#     bill = get_object_or_404(PurchaseBill, id=bill_id)
#     items = PurchaseItem.objects.filter(purchase_bill=bill)
#
#     items_data = [{
#         'product_name': item.product_name,
#         'quantity': item.quantity,
#         'price': item.price
#     } for item in items]
#
#     return JsonResponse({'items': items_data})

# class PurchaseEditSaleView(View):
#     def get(self, request, pk):
#         # Fetch unread notifications count and the latest unread notifications
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#         formset = PurchaseItemFormset()
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         previous_bills = PurchaseBill.objects.filter(supplier=supplierobj).order_by('-billno')
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#             'previous_bills': previous_bills,
#             'count1': count1,
#             'notification1': notification1,
#         }
#         return render(request, 'purchases/purchase_edit.html', context)
#
#     def post(self, request, pk):
#         formset = PurchaseItemFormset(request.POST)
#         supplierobj = get_object_or_404(Supplier, pk=pk)
#         count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#         notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#         if formset.is_valid():
#             try:
#                 with transaction.atomic():
#                     # [Keep your existing post logic here]
#                     return redirect('purchase-bill', billno=billobj.billno)
#             except Exception as e:
#                 messages.error(request, f"An error occurred: {str(e)}")
#         else:
#             messages.error(request, "There were errors in the form. Please correct them.")
#
#         context = {
#             'formset': formset,
#             'supplier': supplierobj,
#             'stock_list': Stock.objects.filter(is_deleted=False),
#             'categories': Category.objects.all(),
#             'count1': count1,
#             'notification1': notification1,
#         }
#         return render(request, 'purchases/purchase_edit.html', context)
#
#
# def get_previous_bill_details(request):
#     bill_no = request.GET.get('bill_no')
#     bill = get_object_or_404(PurchaseBill, billno=bill_no)
#     items = PurchaseItem.objects.filter(billno=bill)
#     data = {
#         'items': [
#             {
#                 'stock_id': item.stock.id,
#                 'stock_name': item.stock.name,
#                 'stock_quantity': item.stock.quantity,
#                 # 'stock_alert': item.stock.alert_level,
#                 'purchase': item.purchase.short_name,
#                 'purchase_id': item.purchase.id,
#                 'quantity': item.quantity,
#                 'perprice': item.perprice,
#                 'totalprice': item.totalprice,
#                 'gst': item.stock.gst,
#             }
#             for item in items
#         ]
#     }
#     return JsonResponse(data)
#
#
# def edit_sale_view(request, pk):
#     sale_bill = get_object_or_404(SaleBill, pk=pk)
#     sale_items = SaleItem.objects.filter(billno=sale_bill)
#
#     # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in sale_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, sales_billno=pk)
#
#     try:
#         sale_bill_details = SaleBillDetails.objects.get(billno=sale_bill)
#     except SaleBillDetails.DoesNotExist:
#         sale_bill_details = None
#     existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     # stocks = Stock.objects.all()
#     stocks = Stock.objects.filter(is_deleted=False)  # Initial stock list
#
#     context = {
#         'sale_bill': sale_bill,
#         'sale_items': sale_items,
#         'sale_bill_details': sale_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#         'existing_stock_ids': list(existing_stock_ids),  # Pass as a list for JavaScript
#
#     }
#
#     if request.method == "POST":
#         # Update SaleBill details
#         sale_bill.name = request.POST.get("name", sale_bill.name)
#         sale_bill.phone = request.POST.get("phone", sale_bill.phone)
#         sale_bill.address = request.POST.get("address", sale_bill.address)
#         sale_bill.email = request.POST.get("email", sale_bill.email)
#         sale_bill.gstin = request.POST.get("gstin", sale_bill.gstin)
#         sale_bill.save()
#
#         # Process submitted data
#         existing_ids = request.POST.getlist('existing_ids[]')
#         serials_data = {
#             key.split('-')[1]: value.split(',')
#             for key, value in request.POST.items() if key.startswith('serials-')
#         }
#
#         for stock_id, serial_numbers in serials_data.items():
#             # Update `sales_billno` field for each serial number
#             PurchaseSerial.objects.filter(
#                 stock_id=stock_id,
#                 serialNo__in=serial_numbers
#             ).update(sales_billno=sale_bill.billno)
#
#         # Update existing SaleItems and Stock quantities
#         for item in sale_items:
#             quantity = request.POST.get(f'quantity_{item.pk}')
#             if quantity:
#                 previous_quantity = item.quantity
#                 item.quantity = int(quantity)
#                 item.save()
#
#                 # Update stock quantity
#                 stock = item.stock
#                 stock_quantity = stock.quantity
#
#                 # Calculate the quantity change
#                 quantity_change = item.quantity - previous_quantity
#                 stock.quantity = stock_quantity - quantity_change  # Deduct the quantity change from the stock
#                 stock.save()
#
#         # Process added items (newly added stock and quantities)
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         for stock_id, quantity in zip(new_stock_ids, new_quantities):
#             stock = Stock.objects.get(pk=stock_id)
#             SaleItem.objects.create(
#                 billno=sale_bill,
#                 stock=stock,
#                 quantity=int(quantity),
#                 totalprice=1 * int(quantity),  # Assuming `price` exists in `Stock`
#                 sale=stock.sales,
#             )
#
#             # Update stock quantity for newly added items
#             stock.quantity -= int(quantity)  # Deduct the quantity from stock
#             stock.save()
#
#             # Update SaleBillDetails fields
#             if sale_bill_details:
#                 sale_bill_details.eway_no = request.POST.get("eway_no", sale_bill_details.eway)
#                 sale_bill_details.bill_date = request.POST.get("bill_date", sale_bill_details.tcs)
#                 sale_bill_details.veh_no = request.POST.get("veh_no", sale_bill_details.veh)
#                 sale_bill_details.arrange = request.POST.get("arrange", sale_bill_details.sgst)
#                 sale_bill_details.handby = request.POST.get("handby", sale_bill_details.igst)
#                 sale_bill_details.destination = request.POST.get("destination", sale_bill_details.sgst)
#                 sale_bill_details.po_no = request.POST.get("po_no", sale_bill_details.po)
#                 sale_bill_details.po_date = request.POST.get("po_date", sale_bill_details.cgst)
#                 sale_bill_details.save()
#
#         # Process removed items
#         existing_ids = set(item.pk for item in sale_items)
#         retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
#         removed_ids = existing_ids - retained_ids
#
#
#         for removed_id in removed_ids:
#             item_to_remove = SaleItem.objects.get(pk=removed_id)
#             stock = item_to_remove.stock
#             quantity_to_remove = item_to_remove.quantity
#
#             # Update PurchaseSerial to set sales_billno to NULL for removed items
#             PurchaseSerial.objects.filter(
#                 stock=stock,
#                 sales_billno=sale_bill.billno
#             ).update(sales_billno=None)
#
#             # Return the removed quantity to stock
#             stock.quantity += quantity_to_remove
#             stock.save()
#
#             # Delete the removed SaleItem
#             item_to_remove.delete()
#
#         return redirect('sales-list')  # Replace with your sales list URL name
#
#     return render(request, 'sales/edit_sale.html', context)
#

@login_required(login_url='user-login')
def final_return_serial_numbers(request):
    stock_id = request.GET.get('stock_id')  # Get the stock ID
    sales_billno = request.GET.get('sales_billno')  # Current bill number

    # Debugging log to print the sales bill number
    # print(f"Sales Bill Number: {sales_billno}")

    # Sanitize and extract the numeric part of the sales_billno
    if sales_billno and sales_billno.startswith("Final Bill No: "):
        sales_billno = sales_billno.replace("Final Bill No: ", "")

    try:
        sales_billno = int(sales_billno)  # Ensure it's an integer
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid sales bill number"}, status=400)

    # Return empty result if stock_id is missing
    if not stock_id:
        return JsonResponse({'serial_numbers': []})

    # Fetch records matching the sales_billno or where sales_billno is NULL
    serials = PurchaseSerial.objects.filter(stock_id=stock_id).filter(models.Q(final_salebill=sales_billno, return_bill=None))

    # Construct response with the required fields
    serial_numbers = [
        {
            'serialNo': serial['serialNo'],  # Ensure 'serialNo' field is used
            'checked': serial['final_salebill'] == sales_billno  # Check if the sales_billno matches the current bill
        }
        for serial in serials.values('serialNo', 'final_salebill')  # Fetch necessary fields
    ]

    return JsonResponse({'serial_numbers': serial_numbers})

@login_required(login_url='user-login')
def return_sale_view(request, pk):
    sale_bill = get_object_or_404(FinalSale, pk=pk)
    sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill)

    # For each item, retrieve the related serial numbers from PurchaseSerial
    for item in sale_items:
        item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=pk)

    try:
        final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
    except FinalBillDetails.DoesNotExist:
        final_bill_details = None

    existing_stock_ids = sale_items.values_list('stock_id', flat=True)
    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.filter(is_deleted=False)

    context = {
        'sale_bill': sale_bill,
        'sale_items': sale_items,
        'final_bill_details': final_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
        'existing_stock_ids': list(existing_stock_ids),
    }

    if request.method == "POST":
        # Update SaleBill fields
        # sale_bill.name = request.POST.get("name", sale_bill.name)
        # sale_bill.phone = request.POST.get("phone", sale_bill.phone)
        # sale_bill.address = request.POST.get("address", sale_bill.address)
        # sale_bill.email = request.POST.get("email", sale_bill.email)
        sale_bill.return_date = timezone.now()
        sale_bill.return_bill = True
        sale_bill.save()
        #
        # sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)
        #
        # Update SaleBillDetails fields
        if final_bill_details:
            # final_bill_details.billno = sale_bill_instance,  # Now passing the correct SaleBill instance
            final_bill_details.eway = request.POST.get("eway_no", final_bill_details.eway)
            final_bill_details.tcs = request.POST.get("bill_date", final_bill_details.tcs)
            final_bill_details.veh = request.POST.get("veh_no", final_bill_details.veh)
            final_bill_details.sgst = request.POST.get("arrange", final_bill_details.sgst)
            final_bill_details.igst = request.POST.get("handby", final_bill_details.igst)
            final_bill_details.destination = request.POST.get("destination", final_bill_details.destination)
            final_bill_details.po = request.POST.get("po_no", final_bill_details.po)
            final_bill_details.cgst = request.POST.get("po_date", final_bill_details.cgst)
            final_bill_details.save()

        # sale_bill_instance = sale_bill.billno  # Replace 'related_salebill' with the actual field name
        # Assuming FinalSale and SaleBill are related, such as through a ForeignKey or OneToOneField
        # sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)
        #
        # final_bill_details = FinalBillDetails(
        #     billno=sale_bill_instance,  # Now passing the correct SaleBill instance
        #     eway=request.POST.get('eway_no'),
        #     cgst=request.POST.get('bill_date'),
        #     veh=request.POST.get('veh_no'),
        #     sgst=request.POST.get('arrange'),
        #     igst=request.POST.get('handby'),
        #     destination=request.POST.get('destination'),
        #     po=request.POST.get('po_no'),
        #     tcs=request.POST.get('po_date'),
        # )
        # final_bill_details.save()

        # Update SaleItems and Stock
        serials_data = {
            key.split('-')[1]: value.split(',')
            for key, value in request.POST.items() if key.startswith('serials-')
        }

        for stock_id, serial_numbers in serials_data.items():
            PurchaseSerial.objects.filter(stock_id=stock_id).update(final_salebill=None)
            PurchaseSerial.objects.filter(
                stock_id=stock_id,
                serialNo__in=serial_numbers
            ).update(final_salebill=sale_bill.billno)


        for item in sale_items:
            quantity = request.POST.get(f'total_quantity_{item.pk}')
            r_quantity = request.POST.get(f'return_quantity_{ item.pk }')
            if quantity:
                previous_quantity = item.total_quantity
                item.quantity = int(quantity)
                item.final_quantity = int(quantity)
                item.r_quantity = int(r_quantity)
                item.save()

                stock = item.stock
                stock_quantity = stock.quantity
                quantity_change = item.quantity - previous_quantity
                stock.quantity = stock_quantity - quantity_change
                stock.save()

        # Process new items
        new_stock_ids = request.POST.getlist("stock_ids[]")
        new_quantities = request.POST.getlist("quantities[]")
        for stock_id, quantity in zip(new_stock_ids, new_quantities):
            stock = Stock.objects.get(pk=stock_id)
            SaleItem.objects.create(
                billno=sale_bill,
                stock=stock,
                quantity=int(quantity),
                totalprice=1 * int(quantity),  # Assuming `price` is handled
                sale=stock.sales,
            )
            stock.quantity -= int(quantity)
            stock.save()

        # Handle removed items
        existing_ids = set(item.pk for item in sale_items)
        retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
        removed_ids = existing_ids - retained_ids

        for removed_id in removed_ids:
            item_to_remove = SaleItem.objects.get(pk=removed_id)
            stock = item_to_remove.stock
            quantity_to_remove = item_to_remove.quantity

            PurchaseSerial.objects.filter(
                stock=stock,
                sales_billno=sale_bill.billno
            ).update(sales_billno=None)

            stock.quantity += quantity_to_remove
            stock.save()
            item_to_remove.delete()

        return redirect('finalsales-list')

    return render(request, 'sales/finalsales_return.html', context)



#
# def finalsale_return(request, pk):
#
#     sale_bill = get_object_or_404(FinalSale, pk=pk)
#
#     customer_type = request.GET.get('customer_type')
#     customer_id = request.GET.get('customer')
#     selected_categories = request.GET.get('categories', '').split(',')
#
#     # Filter categories based on the selected ones
#     categories = Category.objects.filter(id__in=selected_categories) if selected_categories else Category.objects.all()
#
#     # Filter sale items based on multiple selected categories
#     sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill, stock__category__in=categories)
#
#     # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in sale_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=pk)
#
#
#     # # Get the category IDs from the form (if they exist)
#     # category_ids = request.POST.getlist('categories')  # Now retrieves a list of selected category IDs
#     # categories = Category.objects.filter(id__in=category_ids)  # Filter categories based on the selected IDs
#     # print(categories)  # This will print all selected categories
#     #
#     # # Filter sale items based on multiple selected categories
#     # sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill, stock__category__in=categories)
#
#     try:
#         final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
#     except FinalBillDetails.DoesNotExist:
#         final_bill_details = None
#
#     existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     context = {
#         'sale_bill': sale_bill,
#         'sale_items': sale_items,
#         'final_bill_details': final_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#         'existing_stock_ids': list(existing_stock_ids),
#     }
#
#
#     if request.method == "POST":
#         # Update SaleBill fields
#         # sale_bill.name = request.POST.get("name", sale_bill.name)
#         # sale_bill.phone = request.POST.get("phone", sale_bill.phone)
#         # sale_bill.address = request.POST.get("address", sale_bill.address)
#         # sale_bill.email = request.POST.get("email", sale_bill.email)
#         sale_bill.return_date = timezone.now()
#         sale_bill.return_bill = True
#         sale_bill.save()
#         #
#         # sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)
#         #
#         # Update SaleBillDetails fields
#         if final_bill_details:
#             # final_bill_details.billno = sale_bill_instance,  # Now passing the correct SaleBill instance
#             final_bill_details.eway = request.POST.get("eway_no", final_bill_details.eway)
#             final_bill_details.tcs = request.POST.get("bill_date", final_bill_details.tcs)
#             final_bill_details.veh = request.POST.get("veh_no", final_bill_details.veh)
#             final_bill_details.sgst = request.POST.get("arrange", final_bill_details.sgst)
#             final_bill_details.igst = request.POST.get("handby", final_bill_details.igst)
#             final_bill_details.destination = request.POST.get("destination", final_bill_details.destination)
#             final_bill_details.po = request.POST.get("po_no", final_bill_details.po)
#             final_bill_details.cgst = request.POST.get("po_date", final_bill_details.cgst)
#             final_bill_details.save()
#
#         # sale_bill_instance = sale_bill.billno  # Replace 'related_salebill' with the actual field name
#         # Assuming FinalSale and SaleBill are related, such as through a ForeignKey or OneToOneField
#         # sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)
#         #
#         # final_bill_details = FinalBillDetails(
#         #     billno=sale_bill_instance,  # Now passing the correct SaleBill instance
#         #     eway=request.POST.get('eway_no'),
#         #     cgst=request.POST.get('bill_date'),
#         #     veh=request.POST.get('veh_no'),
#         #     sgst=request.POST.get('arrange'),
#         #     igst=request.POST.get('handby'),
#         #     destination=request.POST.get('destination'),
#         #     po=request.POST.get('po_no'),
#         #     tcs=request.POST.get('po_date'),
#         # )
#         # final_bill_details.save()
#
#         # Update SaleItems and Stock
#         serials_data = {
#             key.split('-')[1]: value.split(',')
#             for key, value in request.POST.items() if key.startswith('serials-')
#         }
#
#         for stock_id, serial_numbers in serials_data.items():
#             PurchaseSerial.objects.filter(stock_id=stock_id).update(final_salebill=None)
#             PurchaseSerial.objects.filter(
#                 stock_id=stock_id,
#                 serialNo__in=serial_numbers
#             ).update(final_salebill=sale_bill.billno)
#
#
#         for item in sale_items:
#             quantity = request.POST.get(f'total_quantity_{item.pk}')
#             r_quantity = request.POST.get(f'return_quantity_{ item.pk }')
#             if quantity:
#                 previous_quantity = item.total_quantity
#                 item.quantity = int(quantity)
#                 item.final_quantity = int(quantity)
#                 item.r_quantity = int(r_quantity)
#                 item.save()
#
#                 stock = item.stock
#                 stock_quantity = stock.quantity
#                 quantity_change = item.quantity - previous_quantity
#                 stock.quantity = stock_quantity - quantity_change
#                 stock.save()
#
#         # Process new items
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         for stock_id, quantity in zip(new_stock_ids, new_quantities):
#             stock = Stock.objects.get(pk=stock_id)
#             SaleItem.objects.create(
#                 billno=sale_bill,
#                 stock=stock,
#                 quantity=int(quantity),
#                 totalprice=1 * int(quantity),  # Assuming `price` is handled
#                 sale=stock.sales,
#             )
#             stock.quantity -= int(quantity)
#             stock.save()
#
#         # Handle removed items
#         existing_ids = set(item.pk for item in sale_items)
#         retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
#         removed_ids = existing_ids - retained_ids
#
#         for removed_id in removed_ids:
#             item_to_remove = SaleItem.objects.get(pk=removed_id)
#             stock = item_to_remove.stock
#             quantity_to_remove = item_to_remove.quantity
#
#             PurchaseSerial.objects.filter(
#                 stock=stock,
#                 sales_billno=sale_bill.billno
#             ).update(sales_billno=None)
#
#             stock.quantity += quantity_to_remove
#             stock.save()
#             item_to_remove.delete()
#
#         return redirect('finalsales-list')
#
#     return render(request, 'return/finalsales_return.html', context)


@login_required(login_url='user-login')
def finalsale_return(request, pk):
    # Fetch the final sale bill based on the provided pk
    sale_bill = get_object_or_404(FinalSale, pk=pk)

    # Get the associated SaleBill for the current FinalSale
    related_sales = SaleBill.objects.filter(final_salebill=sale_bill)

    sale_bill_obj = related_sales.first()

    # Get necessary data from the request
    customer_type = request.GET.get('customer_type')
    customer_id = request.GET.get('customer')
    vendor_id = request.GET.get('vendor')
    selected_categories = request.GET.get('categories', '').split(',')

    # Filter categories based on selected ones
    categories = Category.objects.filter(id__in=selected_categories) if selected_categories else Category.objects.all()

    # Filter sale items based on the selected categories
    sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill, stock__category__in=categories)

    # For each item, retrieve related serial numbers and safe category labels.
    # Using safe resolvers avoids MultipleObjectsReturned from legacy duplicate
    # category/subcategory rows when templates access FK descriptors.
    for item in sale_items:
        item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=pk, return_bill=None)
        safe_category = category_for_fk_id(item.stock.category_id)
        safe_subcategory = subcategory_for_fk_id(item.stock.subcategory_id)
        item.safe_category_name = safe_category.name if safe_category else ""
        item.safe_subcategory_name = safe_subcategory.name if safe_subcategory else ""

    # Fetch the final bill details, if they exist
    try:
        final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
    except FinalBillDetails.DoesNotExist:
        final_bill_details = None

    # Existing stock IDs and other necessary data
    existing_stock_ids = sale_items.values_list('stock_id', flat=True)
    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.filter(is_deleted=False)

    # Prepare context for rendering the template
    context = {
        'sale_bill': sale_bill,
        'sale_items': sale_items,
        'final_bill_details': final_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
        'existing_stock_ids': list(existing_stock_ids),
    }

    if request.method == "POST":
        def _clean_serials_map(post_data):
            serial_map = {}
            for key, raw_value in post_data.items():
                if not key.startswith("serials-"):
                    continue
                stock_key = key.split("-", 1)[1].strip()
                if not stock_key:
                    continue
                values = [
                    s.strip()
                    for s in (raw_value or "").split(",")
                    if s and s.strip()
                ]
                serial_map[stock_key] = values
            return serial_map

        serials_data = _clean_serials_map(request.POST)

        # Validate serial reduction before any write:
        # if current return qty is reduced for a serialized stock, user must remove
        # exactly same count of corresponding serial numbers.
        serial_errors = []
        for item in sale_items:
            current_return_raw = request.POST.get(f'current_quantity_{item.pk}')
            current_return_qty = Decimal(current_return_raw or 0)
            if current_return_qty <= 0:
                continue

            active_serial_qs = PurchaseSerial.objects.filter(
                stock=item.stock,
                final_salebill=sale_bill.billno,
                return_bill=None,
            ).exclude(serialNo__isnull=True).exclude(serialNo='')

            if not active_serial_qs.exists():
                continue

            if current_return_qty != current_return_qty.to_integral_value():
                serial_errors.append(
                    f"{item.stock.name}: return quantity must be whole number for serialized stock."
                )
                continue

            required_removed = int(current_return_qty)
            selected_serials = serials_data.get(str(item.stock_id), [])
            selected_set = {s for s in selected_serials if s}
            available_set = set(active_serial_qs.values_list("serialNo", flat=True))

            if len(selected_set) != required_removed:
                serial_errors.append(
                    f"{item.stock.name}: expected {required_removed} serial(s), got {len(selected_set)}."
                )
                continue

            invalid_serials = selected_set - available_set
            if invalid_serials:
                serial_errors.append(
                    f"{item.stock.name}: invalid serial selection."
                )

        if serial_errors:
            messages.error(
                request,
                "Please remove the serial numbers first before saving."
            )
            for err in serial_errors:
                messages.error(request, err)
            return render(request, 'return/finalsales_return.html', context)

        sale_bill.return_date = timezone.now()
        sale_bill.return_bill = True
        sale_bill.save()

        # Step 1: Create a ReturnSale record
        # return_sale = ReturnSale(
        #     customer_id=customer_id,  # Assuming customer_id is passed via GET
        #     time=timezone.now(),
        #     update_time=timezone.now(),
        #     final_bill=sale_bill,
        # )
        # return_sale.save()

        if sale_bill.customer:
            # Sale is associated with a customer
            return_sale = ReturnSale(
                customer_id=customer_id,
                time=timezone.now(),
                update_time=timezone.now(),
                final_bill=sale_bill,
            )
        else:
            # Sale is associated with a vendor
            return_sale = ReturnSale(
                vendor_id=vendor_id,
                time=timezone.now(),
                update_time=timezone.now(),
                final_bill=sale_bill,
            )
        return_sale.save()


        # Step 2: Create ReturnBillDetails
        return_bill_details = ReturnBillDetails(
            billno=return_sale,
            eway=request.POST.get('eway_no'),
            cgst=request.POST.get('bill_date'),
            veh=request.POST.get('veh_no'),
            sgst=request.POST.get('arrange'),
            igst=request.POST.get('handby'),
            destination=request.POST.get('destination'),
            po=request.POST.get('po_no'),
            tcs=request.POST.get('po_date'),
            gst_value=request.POST.get('gst_value'),
            gst_amount=request.POST.get('gst_amount'),
            final_amount=request.POST.get('final_amount'),
            total_amount=request.POST.get('total_amount'),
            round_off=request.POST.get('round_off'),
            final_bill=sale_bill,
        )
        return_bill_details.save()

        # # Step 3: Handle serial numbers and stock updates
        # serials_data = {
        #     key.split('-')[1]: value.split(',')
        #     for key, value in request.POST.items() if key.startswith('serials-')
        # }
        #
        # for stock_id, serial_numbers in serials_data.items():
        #     PurchaseSerial.objects.filter(
        #         stock_id=stock_id,
        #         final_salebill=sale_bill.billno,
        #         return_bill=None
        #     ).update(sales_billno=sale_bill_obj, final_salebill=sale_bill.billno, return_bill=None)
        #
        #     PurchaseSerial.objects.filter(
        #         stock_id=stock_id,
        #         serialNo__in=serial_numbers
        #     # ).update(sales_billno=None, final_salebill=None, return_bill=return_sale)
        #      ).update(return_bill=return_sale)
        #
        #
        #     # ---- Start duplication logic ----
        #     # purchase_serials_with_return = PurchaseSerial.objects.filter(return_bill__isnull=False)
        #     purchase_serials_with_return = PurchaseSerial.objects.filter(return_bill=return_sale)
        #
        #     for ps in purchase_serials_with_return:
        #         PurchaseSerial.objects.create(
        #             billno_id=ps.billno_id,
        #             purchase_id=ps.purchase_id,
        #             stock_id=ps.stock_id,
        #             serialNo=ps.serialNo,
        #             item_id=ps.item_id,
        #             sales_billno_id=None,
        #             final_salebill_id=None,
        #             return_bill_id=None
        #         )
        #     # ---- End duplication logic ----

        # Step 3: Handle serial numbers and stock updates
        for stock_id, serial_numbers in serials_data.items():
            # First update the existing records to mark them as returned
            PurchaseSerial.objects.filter(
                stock_id=stock_id,
                serialNo__in=serial_numbers,
                final_salebill=sale_bill.billno,
                return_bill=None
            ).update(return_bill=return_sale)

            # Then create new records only for the specific serial numbers being returned
            returned_serials = PurchaseSerial.objects.filter(
                stock_id=stock_id,
                serialNo__in=serial_numbers,
                return_bill=return_sale
            )

            for ps in returned_serials:
                # Create new record with cleared sales/final sale references
                PurchaseSerial.objects.create(
                    billno_id=ps.billno_id,
                    purchase_id=ps.purchase_id,
                    stock_id=ps.stock_id,
                    serialNo=ps.serialNo,
                    item_id=ps.item_id,
                    sales_billno_id=None,
                    final_salebill_id=None,
                    return_bill_id=None
                )

        # Step 4: Update ReturnSaleItems and Stock
        # for item in sale_items:
        #     quantity = request.POST.get(f'total_quantity_{item.pk}')
        #     r_quantity = request.POST.get(f'current_quantity_{ item.pk }')
        #     if quantity:
        #         previous_quantity = item.total_quantity
        #         item.quantity = int(quantity)
        #         item.final_quantity = int(quantity)
        #         item.r_quantity = int(r_quantity)
        #         item.save()
        #
        #         stock = item.stock
        #         stock_quantity = stock.quantity
        #         quantity_change = item.quantity - previous_quantity
        #         stock.quantity = stock_quantity + quantity_change  # Adjusting stock quantity for return
        #         stock.save()
        #
                # # Step 5: Create ReturnSaleItem record
                # return_sale_item = ReturnSaleItem(
                #     return_bill=return_sale,
                #     stock=item.stock,
                #     total_quantity=item.total_quantity,
                #     unit_price=item.unit_price,
                #     total_price=item.total_price,
                #     r_quantity=item.r_quantity,
                #     final_quantity=item.final_quantity
                # )
        #         return_sale_item.save()

        # # Step 4: Update ReturnSaleItems and Stock
        # for item in sale_items:
        #     quantity = request.POST.get(f'total_quantity_{item.pk}')
        #     r_quantity = request.POST.get(f'current_quantity_{item.pk}')
        #     return_quantity = request.POST.get(f'return_quantity_{item.pk}')
        #
        #     if quantity:
        #         # Convert input values to integers and handle cases where input might be None
        #         quantity = int(quantity) if quantity else 0
        #         r_quantity = int(r_quantity) if r_quantity else 0
        #         return_quantity = int(return_quantity) if return_quantity else 0
        #
        #         # Update FinalSaleItem table
        #         previous_quantity = item.total_quantity
        #         item.quantity = quantity
        #         item.final_quantity = quantity
        #         item.r_quantity = return_quantity + r_quantity  # Updated logic for r_quantity
        #         item.save()
        #
        #         # Adjust stock quantity for the return
        #         stock = item.stock
        #         stock_quantity = stock.quantity
        #         quantity_change = item.quantity - previous_quantity
        #         stock.quantity = stock_quantity + quantity_change
        #         stock.save()
        #
        #         # Step 5: Create ReturnSaleItem record with return_quantity value
        #         return_sale_item = ReturnSaleItem(
        #             return_bill=return_sale,
        #             stock=item.stock,
        #             total_quantity=item.final_quantity,  # Accessed earlier return_quantity value
        #             unit_price=item.unit_price,
        #             total_price=item.total_price,
        #             r_quantity=r_quantity,  # Use return_quantity for ReturnSaleItem
        #             final_quantity=item.final_quantity
        #         )
        #         # Step 5: Create ReturnSaleItem record
        #
        #         return_sale_item.save()

        # Step 4: Update ReturnSaleItems and Stock
        for item in sale_items:
            quantity = request.POST.get(f'total_quantity_{item.pk}')
            r_quantity = request.POST.get(f'current_quantity_{item.pk}')
            return_quantity = request.POST.get(f'return_quantity_{item.pk}')

            if quantity:
                # Convert input values to integers and handle cases where input might be None
                quantity = Decimal(quantity) if quantity else 0
                r_quantity = Decimal(r_quantity) if r_quantity else 0
                return_quantity = Decimal(return_quantity) if return_quantity else 0

                # Capture the previous value of final_quantity before updating it
                previous_final_quantity = item.final_quantity if item.final_quantity is not None else item.total_quantity

                # Update FinalSaleItem table
                previous_quantity = item.total_quantity
                item.quantity = quantity
                item.final_quantity = quantity
                item.r_quantity = return_quantity + r_quantity  # Updated logic for r_quantity
                item.save()

                # Adjust stock quantity for the return
                stock = item.stock
                stock_quantity = stock.quantity
                # quantity_change = previous_quantity - item.quantity
                stock.quantity = stock_quantity + r_quantity
                stock.save()

                # Step 5: Create ReturnSaleItem record with return_quantity value
                return_sale_item = ReturnSaleItem(
                    return_bill=return_sale,
                    stock=item.stock,
                    total_quantity=previous_final_quantity,  # Accessed earlier return_quantity value
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    r_quantity=r_quantity,  # Use return_quantity for ReturnSaleItem
                    final_quantity=item.final_quantity,
                    final_bill=sale_bill,
                )
                # Step 5: Create ReturnSaleItem record

                return_sale_item.save()

        # Step 6: Process new items and return quantities
        new_stock_ids = request.POST.getlist("stock_ids[]")
        new_quantities = request.POST.getlist("quantities[]")
        for stock_id, quantity in zip(new_stock_ids, new_quantities):
            stock = Stock.objects.get(pk=stock_id)
            # Create new ReturnSaleItem for the new stock
            ReturnSaleItem.objects.create(
                return_bill=return_sale,
                stock=stock,
                total_quantity=Decimal(quantity),
                unit_price=stock.unit_price,  # Assuming stock has a unit_price field
                total_price=stock.unit_price * Decimal(quantity),
                r_quantity=0,
                final_quantity=Decimal(quantity),
            )
            stock.quantity -= Decimal(quantity)
            stock.save()

        # Handle removed items (not needed for returns but kept for completeness)
        existing_ids = set(item.pk for item in sale_items)
        retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
        removed_ids = existing_ids - retained_ids

        for removed_id in removed_ids:
            item_to_remove = FinalSaleItem.objects.get(pk=removed_id)
            stock = item_to_remove.stock
            quantity_to_remove = item_to_remove.quantity

            # PurchaseSerial.objects.filter(
            #     stock=stock,
            #     sales_billno=sale_bill.billno
            # ).update(sales_billno=None)

            stock.quantity += quantity_to_remove
            stock.save()
            item_to_remove.delete()

        return redirect('returnsales-list')  # Redirect to the return sales list after saving

    return render(request, 'return/finalsales_return.html', context)



# def finalsale_return(request, pk):
#     # Fetch the final sale bill based on the provided pk
#     sale_bill = get_object_or_404(FinalSale, pk=pk)
#
#     # Get necessary data from the request
#     customer_type = request.GET.get('customer_type')
#     customer_id = request.GET.get('customer')
#     selected_categories = request.GET.get('categories', '').split(',')
#
#     # Filter categories based on selected ones
#     categories = Category.objects.filter(id__in=selected_categories) if selected_categories else Category.objects.all()
#
#     # Filter sale items based on the selected categories
#     sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill, stock__category__in=categories)
#
#     # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in sale_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=pk)
#
#     # Fetch the final bill details, if they exist
#     try:
#         final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
#     except FinalBillDetails.DoesNotExist:
#         final_bill_details = None
#
#     # Existing stock IDs and other necessary data
#     existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     # Prepare context for rendering the template
#     context = {
#         'sale_bill': sale_bill,
#         'sale_items': sale_items,
#         'final_bill_details': final_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#         'existing_stock_ids': list(existing_stock_ids),
#     }


# def return_view_edit(request, pk):
#     sale_bill = get_object_or_404(ReturnSale, pk=pk)
#     sale_items = ReturnSaleItem.objects.filter(return_bill=sale_bill)
#
#       # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in sale_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=sale_bill.final_bill.billno)
#
#     try:
#         return_bill_details = ReturnBillDetails.objects.get(billno=sale_bill)
#     except ReturnBillDetails.DoesNotExist:
#         return_bill_details = None
#
#     existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     context = {
#           'sale_bill': sale_bill,
#           'sale_items': sale_items,
#           'sale_bill_details': return_bill_details,
#           'categories': categories,
#           'subcategories': subcategories,
#           'stocks': stocks,
#           'existing_stock_ids': list(existing_stock_ids),
#     }
#
#     if request.method == "POST":
#         # final_bill = request.POST.get("final_bill")
#         #
#         # # Sanitize and extract the numeric part of the sales_billno
#         # if final_bill and final_bill.startswith("Final Bill No: "):
#         #     final_bill = final_bill.replace("Final Bill No: ", "")
#         #
#         #
#         #     final_bill = int(final_bill)  # Ensure it's an integer
#
#         final_bill_number = request.POST.get("final_bill")
#
#         final_bill_number = int(final_bill_number)  # Ensure it's an integer
#
#         final_bill = FinalSale.objects.get(billno=final_bill_number)
#
#
#         # Step 1: Create a ReturnSale record
#         return_sale = ReturnSale(
#             # customer_id=customer_id,  # Assuming customer_id is passed via GET
#             time=timezone.now(),
#             update_time=timezone.now(),
#             final_bill=final_bill,
#         )
#         return_sale.save()
#
#         # # Step 2: Create ReturnBillDetails
#         # return_bill_details = ReturnBillDetails(
#         #     billno=return_sale,
#         #     eway=request.POST.get('eway_no'),
#         #     cgst=request.POST.get('bill_date'),
#         #     veh=request.POST.get('veh_no'),
#         #     sgst=request.POST.get('arrange'),
#         #     igst=request.POST.get('handby'),
#         #     destination=request.POST.get('destination'),
#         #     po=request.POST.get('po_no'),
#         #     tcs=request.POST.get('po_date'),
#         #     gst_value=request.POST.get('gst_value'),
#         #     gst_amount=request.POST.get('gst_amount'),
#         #     final_amount=request.POST.get('final_amount'),
#         #     total_amount=request.POST.get('total_amount'),
#         #     round_off=request.POST.get('round_off'),
#         #     final_bill=final_bill,
#         # )
#         # return_bill_details.save()
#
#         # Update SaleBillDetails fields
#         if return_bill_details:
#             # return_bill_details.billno = sale_bill_instance,  # Now passing the correct SaleBill instance
#             return_bill_details.eway = request.POST.get("eway_no", return_bill_details.eway)
#             return_bill_details.tcs = request.POST.get("bill_date", return_bill_details.tcs)
#             return_bill_details.veh = request.POST.get("veh_no", return_bill_details.veh)
#             return_bill_details.sgst = request.POST.get("arrange", return_bill_details.sgst)
#             return_bill_details.igst = request.POST.get("handby", return_bill_details.igst)
#             return_bill_details.destination = request.POST.get("destination", return_bill_details.destination)
#             return_bill_details.po = request.POST.get("po_no", return_bill_details.po)
#             return_bill_details.cgst = request.POST.get("po_date", return_bill_details.cgst)
#             return_bill_details.save()
#
#
#         # Step 3: Handle serial numbers and stock updates
#         serials_data = {
#             key.split('-')[1]: value.split(',')
#             for key, value in request.POST.items() if key.startswith('serials-')
#         }
#
#         for stock_id, serial_numbers in serials_data.items():
#             PurchaseSerial.objects.filter(stock_id=stock_id).update(final_salebill=None, return_bill=return_sale)
#             PurchaseSerial.objects.filter(
#                 stock_id=stock_id,
#                 serialNo__in=serial_numbers
#             ).update(final_salebill=final_bill, return_bill=None)
#
#
#         # # Step 4: Update ReturnSaleItems and Stock
#         # for item in sale_items:
#         #     quantity = request.POST.get(f'total_quantity_{item.pk}')
#         #     r_quantity = request.POST.get(f'return_quantity_{item.pk}')
#         #     return_quantity = request.POST.get(f'return_quantity_{item.pk}')
#         #
#         #     if quantity:
#         #         # Convert input values to integers and handle cases where input might be None
#         #         quantity = int(quantity) if quantity else 0
#         #         r_quantity = int(r_quantity) if r_quantity else 0
#         #         return_quantity = int(return_quantity) if return_quantity else 0
#         #
#         #         # Capture the previous value of final_quantity before updating it
#         #         previous_final_quantity = item.final_quantity if item.final_quantity is not None else item.total_quantity
#
#                 # # Update FinalSaleItem table
#                 # previous_quantity = item.total_quantity
#                 # item.quantity = quantity
#                 # item.final_quantity = quantity
#                 # item.r_quantity = return_quantity + r_quantity  # Updated logic for r_quantity
#                 # item.save()
#                 #
#                 # # Adjust stock quantity for the return
#                 # stock = item.stock
#                 # stock_quantity = stock.quantity
#                 # quantity_change = previous_quantity - item.quantity
#                 # stock.quantity = stock_quantity + quantity_change
#                 # stock.save()
#
#         for item in sale_items:
#                 quantity = request.POST.get(f'total_quantity_{item.pk}')
#                 r_quantity = request.POST.get(f'return_quantity_{item.pk}')
#
#                 previous_final_quantity = item.final_quantity if item.final_quantity is not None else item.total_quantity
#
#                 if quantity:
#                     previous_quantity = item.total_quantity
#                     item.quantity = int(quantity)
#                     item.final_quantity = int(quantity)
#                     item.r_quantity = int(r_quantity)
#                     item.save()
#
#                     stock = item.stock
#                     stock_quantity = stock.quantity
#                     quantity_change = item.quantity - previous_quantity
#                     stock.quantity = stock_quantity - quantity_change
#                     stock.save()
#
#                 # Step 5: Create ReturnSaleItem record with return_quantity value
#                 return_sale_item = ReturnSaleItem(
#                     return_bill=return_sale,
#                     stock=item.stock,
#                     total_quantity=previous_final_quantity,  # Accessed earlier return_quantity value
#                     unit_price=item.unit_price,
#                     total_price=item.total_price,
#                     r_quantity=r_quantity,  # Use return_quantity for ReturnSaleItem
#                     final_quantity=item.final_quantity,
#                     final_bill=final_bill,
#                 )
#                 # Step 5: Create ReturnSaleItem record
#
#                 return_sale_item.save()
#
#         # Step 6: Process new items and return quantities
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         for stock_id, quantity in zip(new_stock_ids, new_quantities):
#             stock = Stock.objects.get(pk=stock_id)
#             # Create new ReturnSaleItem for the new stock
#             ReturnSaleItem.objects.create(
#                 return_bill=return_sale,
#                 stock=stock,
#                 total_quantity=int(quantity),
#                 unit_price=stock.unit_price,  # Assuming stock has a unit_price field
#                 total_price=stock.unit_price * int(quantity),
#                 r_quantity=0,
#                 final_quantity=int(quantity),
#             )
#             stock.quantity -= int(quantity)
#             stock.save()
#
#         # Handle removed items (not needed for returns but kept for completeness)
#         existing_ids = set(item.pk for item in sale_items)
#         retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
#         removed_ids = existing_ids - retained_ids
#
#         for removed_id in removed_ids:
#             item_to_remove = FinalSaleItem.objects.get(pk=removed_id)
#             stock = item_to_remove.stock
#             quantity_to_remove = item_to_remove.quantity
#
#             PurchaseSerial.objects.filter(
#                 stock=stock,
#                 sales_billno=sale_bill.billno
#             ).update(sales_billno=None)
#
#             stock.quantity += quantity_to_remove
#             stock.save()
#             item_to_remove.delete()
#
#         return redirect('returnsales-list')  # Redirect to the return sales list after saving
#
#     return render(request, 'return/return_edit.html', context)

#
# @login_required(login_url='user-login')
# def return_view_edit(request, pk):
#     sale_bill = get_object_or_404(ReturnSale, pk=pk)
#     sale_items = ReturnSaleItem.objects.filter(return_bill=sale_bill)
#
#     # For each item, retrieve the related serial numbers from PurchaseSerial
#     for item in sale_items:
#         item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=sale_bill.final_bill.billno)
#     try:
#         return_bill_details = ReturnBillDetails.objects.get(billno=sale_bill)
#     except ReturnBillDetails.DoesNotExist:
#         return_bill_details = None
#
#     existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#     categories = Category.objects.active_only()
#     subcategories = SubCategory.objects.active_only()
#     stocks = Stock.objects.filter(is_deleted=False)
#
#     context = {
#         'sale_bill': sale_bill,
#         'sale_items': sale_items,
#         'sale_bill_details': return_bill_details,
#         'categories': categories,
#         'subcategories': subcategories,
#         'stocks': stocks,
#         'existing_stock_ids': list(existing_stock_ids),
#     }
#
#     if request.method == "POST":
#         final_bill_number = request.POST.get("final_bill")
#
#         # # Sanitize and extract the numeric part of the sales_billno
#         # if final_bill_number and final_bill_number.startswith("Final Bill No: "):
#         #     final_bill_number = final_bill_number.replace("Final Bill No: ", "")
#
#         final_bill_number = int(final_bill_number)  # Ensure it's an integer
#
#         # Fetch the FinalSale instance based on the final_bill_number
#         # try:
#         final_bill = FinalSale.objects.get(billno=final_bill_number)
#         # except FinalSale.DoesNotExist:
#         #     # Handle the case where the FinalSale is not found (optional)
#         #     return HttpResponse("Final sale not found.", status=404)
#
#         # Step 1: Update the ReturnSale record
#         sale_bill.final_bill = final_bill  # Assign the FinalSale instance
#         sale_bill.save()
#
#         # # Step 2: Update or Create ReturnBillDetails
#         # if return_bill_details:
#         #     return_bill_details.final_bill = final_bill  # Ensure FinalSale instance is assigned
#         # else:
#         #     return_bill_details = ReturnBillDetails(
#         #         billno=sale_bill,
#         #         eway=request.POST.get('eway_no'),
#         #         cgst=request.POST.get('bill_date'),
#         #         veh=request.POST.get('veh_no'),
#         #         sgst=request.POST.get('arrange'),
#         #         igst=request.POST.get('handby'),
#         #         destination=request.POST.get('destination'),
#         #         po=request.POST.get('po_no'),
#         #         tcs=request.POST.get('po_date'),
#         #         gst_value=request.POST.get('gst_value'),
#         #         gst_amount=request.POST.get('gst_amount'),
#         #         final_amount=request.POST.get('final_amount'),
#         #         total_amount=request.POST.get('total_amount'),
#         #         round_off=request.POST.get('round_off'),
#         #         final_bill=final_bill,  # Assign the FinalSale instance
#         #     )
#         # return_bill_details.save()
#         # Update SaleBillDetails fields
#         if return_bill_details:
#             # return_bill_details.billno = sale_bill_instance,  # Now passing the correct SaleBill instance
#             return_bill_details.eway = request.POST.get("eway_no", return_bill_details.eway)
#             return_bill_details.tcs = request.POST.get("bill_date", return_bill_details.tcs)
#             return_bill_details.veh = request.POST.get("veh_no", return_bill_details.veh)
#             return_bill_details.sgst = request.POST.get("arrange", return_bill_details.sgst)
#             return_bill_details.igst = request.POST.get("handby", return_bill_details.igst)
#             return_bill_details.destination = request.POST.get("destination", return_bill_details.destination)
#             return_bill_details.po = request.POST.get("po_no", return_bill_details.po)
#             return_bill_details.cgst = request.POST.get("po_date", return_bill_details.cgst)
#             return_bill_details.save()
#
#         # Step 3: Handle serial numbers and stock updates
#         serials_data = {
#             key.split('-')[1]: value.split(',')
#             for key, value in request.POST.items() if key.startswith('serials-')
#         }
#
#         for stock_id, serial_numbers in serials_data.items():
#             PurchaseSerial.objects.filter(stock_id=stock_id).update(final_salebill=None, return_bill=sale_bill)
#             PurchaseSerial.objects.filter(
#                 stock_id=stock_id,
#                 serialNo__in=serial_numbers
#             ).update(final_salebill=final_bill, return_bill=None)
#
#         # Step 4: Update ReturnSaleItems and Stock
#         for item in sale_items:
#             avb_quantity = request.POST.get(f'quantity_{item.pk}')
#             r_quantity = request.POST.get(f'return_quantity_{item.pk}')
#             final_quantity = request.POST.get(f'current_quantity_{item.pk}')
#
#             if avb_quantity:
#                 quantity = Decimal(avb_quantity) if avb_quantity else 0
#                 r_quantity = Decimal(r_quantity) if r_quantity else 0
#                 final_quantity = Decimal(final_quantity) if final_quantity else 0
#
#                 previous_final_quantity = item.final_quantity if item.final_quantity is not None else item.total_quantity
#
#                 # Update ReturnSaleItem
#                 previous_quantity = item.total_quantity
#                 item.total_quantity = quantity
#                 item.final_quantity = final_quantity
#                 item.r_quantity = r_quantity
#                 item.save()
#
#                 # Adjust stock quantity for the return
#                 stock = item.stock
#                 stock_quantity = stock.quantity
#                 stock.quantity = stock_quantity + r_quantity
#                 stock.save()
#
#         return redirect('returnsales-list')  # Redirect after saving
#
#     return render(request, 'return/return_edit.html', context)
#
from django.db.models import F
@login_required(login_url='user-login')
def return_view_edit(request, pk):
    sale_bill = get_object_or_404(ReturnSale, pk=pk)
    sale_items = ReturnSaleItem.objects.filter(return_bill=sale_bill)

    # For each item, retrieve the related serial numbers from PurchaseSerial
    for item in sale_items:
        item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=sale_bill.final_bill.billno, return_bill=sale_bill.billno)
    try:
        return_bill_details = ReturnBillDetails.objects.get(billno=sale_bill)
    except ReturnBillDetails.DoesNotExist:
        return_bill_details = None

    existing_stock_ids = sale_items.values_list('stock_id', flat=True)
    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.filter(is_deleted=False)

    context = {
        'sale_bill': sale_bill,
        'sale_items': sale_items,
        'sale_bill_details': return_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
        'existing_stock_ids': list(existing_stock_ids),
    }

    if request.method == "POST":
        final_bill_number = request.POST.get("final_bill")
        final_bill = get_object_or_404(FinalSale, billno=final_bill_number)

        # Fetch the final sale bill based on the provided pk
        # sale_bill = get_object_or_404(FinalSale, pk=pk)

        # Get the associated SaleBill for the current FinalSale
        related_sales = SaleBill.objects.filter(final_salebill=final_bill)

        sale_bill_obj = related_sales.first()

        # Parse selected serials from form once.
        serials_data = {}
        for key, value in request.POST.items():
            if key.startswith('serials-'):
                stock_key = key.split('-', 1)[1].strip()
                if stock_key:
                    serials_data[stock_key] = [
                        s.strip() for s in (value or '').split(',') if s and s.strip()
                    ]

        # Validate serial reduction before writes.
        serial_errors = []
        for item in sale_items:
            current_return_qty = Decimal(request.POST.get(f'return_quantity_{item.pk}', 0) or 0)
            if current_return_qty <= 0:
                continue

            available_qs = PurchaseSerial.objects.filter(
                stock=item.stock,
                final_salebill=final_bill.billno,
            ).filter(
                Q(return_bill__isnull=True) | Q(return_bill=sale_bill)
            ).exclude(serialNo__isnull=True).exclude(serialNo='')

            if not available_qs.exists():
                continue

            if current_return_qty != current_return_qty.to_integral_value():
                serial_errors.append(
                    f"{item.stock.name}: return quantity must be whole number for serialized stock."
                )
                continue

            required_removed = int(current_return_qty)
            selected_serials = serials_data.get(str(item.stock_id), [])
            selected_set = {s for s in selected_serials if s}

            # If user didn't reopen serial modal during edit, fallback to already
            # assigned serials for this same return bill.
            if not selected_set:
                selected_set = set(
                    PurchaseSerial.objects.filter(
                        stock=item.stock,
                        final_salebill=final_bill.billno,
                        return_bill=sale_bill
                    ).exclude(serialNo__isnull=True).exclude(serialNo='')
                    .values_list("serialNo", flat=True)
                )

            available_set = set(available_qs.values_list("serialNo", flat=True))
            if len(selected_set) != required_removed:
                serial_errors.append(
                    f"{item.stock.name}: expected {required_removed} serial(s), got {len(selected_set)}."
                )
                continue

            invalid_serials = selected_set - available_set
            if invalid_serials:
                serial_errors.append(f"{item.stock.name}: invalid serial selection.")

        if serial_errors:
            messages.error(
                request,
                "Please remove the serial numbers first before saving."
            )
            for err in serial_errors:
                messages.error(request, err)
            return render(request, 'return/return_edit.html', context)

        with transaction.atomic():  # Use transaction to ensure data consistency
            # Step 1: Update the ReturnSale record
            sale_bill.final_bill = final_bill
            sale_bill.save()

            if return_bill_details:
                return_bill_details.eway = request.POST.get("eway_no", return_bill_details.eway)
                return_bill_details.tcs = request.POST.get("bill_date", return_bill_details.tcs)
                return_bill_details.veh = request.POST.get("veh_no", return_bill_details.veh)
                return_bill_details.sgst = request.POST.get("arrange", return_bill_details.sgst)
                return_bill_details.igst = request.POST.get("handby", return_bill_details.igst)
                return_bill_details.destination = request.POST.get("destination", return_bill_details.destination)
                return_bill_details.po = request.POST.get("po_no", return_bill_details.po)
                return_bill_details.cgst = request.POST.get("po_date", return_bill_details.cgst)
                return_bill_details.save()

            # Step 3: Handle serial numbers and stock updates
            for stock_id, serial_numbers in serials_data.items():
                # PurchaseSerial.objects.filter(stock_id=stock_id).update(sales_billno=None, final_salebill=None, return_bill=sale_bill)
                PurchaseSerial.objects.filter(stock_id=stock_id).update(sales_billno=sale_bill_obj, final_salebill=final_bill, return_bill=None)
                PurchaseSerial.objects.filter(
                    stock_id=stock_id,
                    serialNo__in=serial_numbers
                # ).update(final_salebill=final_bill, return_bill=None)
                # ).update(sales_billno=sale_bill_obj, final_salebill=final_bill, return_bill=None)
                 ).update(return_bill=sale_bill)


            # Step 4: Update ReturnSaleItems and Stock
            for item in sale_items:
                avb_quantity = Decimal(request.POST.get(f'quantity_{item.pk}', 0))
                r_quantity = Decimal(request.POST.get(f'return_quantity_{item.pk}', 0))
                final_quantity = Decimal(request.POST.get(f'current_quantity_{item.pk}', 0))

                # Calculate the difference between new and old return quantity
                quantity_diff = r_quantity - item.r_quantity

                stock = item.stock
                Stock.objects.filter(id=stock.id).update(quantity=F('quantity') + quantity_diff)

                # # Update stock quantity using F() expression
                # Stock.objects.filter(id=item.stock.id).update(quantity=F('quantity') + quantity_diff)
                stock.refresh_from_db()  # Refresh to get updated value

                # Update ReturnSaleItem
                item.total_quantity = avb_quantity
                item.final_quantity = final_quantity
                item.r_quantity = r_quantity
                item.save()

            return redirect('returnsales-list')

    return render(request, 'return/return_edit.html', context)


# def finalsale_return(request, pk):
#     # Fetch the sale bill
#     sale_bill = get_object_or_404(FinalSale, pk=pk)
#
#     # Handle GET request
#     if request.method == "GET":
#         # Fetch required data for rendering the form
#         sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill)
#         try:
#             final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
#         except FinalBillDetails.DoesNotExist:
#             final_bill_details = None
#
#         existing_stock_ids = sale_items.values_list('stock_id', flat=True)
#         categories = Category.objects.active_only()
#         subcategories = SubCategory.objects.active_only()
#         stocks = Stock.objects.filter(is_deleted=False)
#
#         # Context for rendering the page
#         context = {
#             'sale_bill': sale_bill,
#             'sale_items': sale_items,
#             'final_bill_details': final_bill_details,
#             'categories': categories,
#             'subcategories': subcategories,
#             'stocks': stocks,
#             'existing_stock_ids': list(existing_stock_ids),
#         }
#         return render(request, 'return/finalsales_return.html', context)
#
#     # Handle POST request (form submission)
#     elif request.method == "POST":
#         # Update sale bill
#         sale_bill.return_date = timezone.now()
#         sale_bill.return_bill = True
#         sale_bill.save()
#
#         # Update final bill details if they exist
#         try:
#             final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
#             final_bill_details.eway = request.POST.get("eway_no", final_bill_details.eway)
#             final_bill_details.tcs = request.POST.get("bill_date", final_bill_details.tcs)
#             final_bill_details.veh = request.POST.get("veh_no", final_bill_details.veh)
#             final_bill_details.sgst = request.POST.get("arrange", final_bill_details.sgst)
#             final_bill_details.igst = request.POST.get("handby", final_bill_details.igst)
#             final_bill_details.destination = request.POST.get("destination", final_bill_details.destination)
#             final_bill_details.po = request.POST.get("po_no", final_bill_details.po)
#             final_bill_details.cgst = request.POST.get("po_date", final_bill_details.cgst)
#             final_bill_details.save()
#         except FinalBillDetails.DoesNotExist:
#             pass
#
#         # Update Sale Items
#         for item in FinalSaleItem.objects.filter(final_bill=sale_bill):
#             quantity = request.POST.get(f'total_quantity_{item.pk}')
#             r_quantity = request.POST.get(f'return_quantity_{item.pk}')
#             if quantity:
#                 previous_quantity = item.total_quantity
#                 item.quantity = int(quantity)
#                 item.final_quantity = int(quantity)
#                 item.r_quantity = int(r_quantity)
#                 item.save()
#
#                 stock = item.stock
#                 stock_quantity = stock.quantity
#                 quantity_change = item.quantity - previous_quantity
#                 stock.quantity = stock_quantity - quantity_change
#                 stock.save()
#
#         # Handle new items
#         new_stock_ids = request.POST.getlist("stock_ids[]")
#         new_quantities = request.POST.getlist("quantities[]")
#         for stock_id, quantity in zip(new_stock_ids, new_quantities):
#             stock = Stock.objects.get(pk=stock_id)
#             FinalSaleItem.objects.create(
#                 final_bill=sale_bill,
#                 stock=stock,
#                 quantity=int(quantity),
#                 totalprice=1 * int(quantity),  # Assuming `price` is handled elsewhere
#             )
#             stock.quantity -= int(quantity)
#             stock.save()
#
#         return redirect('finalsales-list')

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Customer, Category, FinalSale
#
# def select_customer_view(request):
#     if request.method == "GET":
#         # Fetch only customers with non-deleted FinalSale entries
#         customers = Customer.objects.filter(
#             Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
#         ).order_by('Comp_name')
#         categories = Category.objects.all()
#         return render(request, 'return/select_customer.html', {'customers': customers, 'categories': categories})
#
#     return JsonResponse({'error': 'Invalid request method'}, status=400)
#
# # def get_billnos(request):
# #     if request.method == "GET" and 'customer_id' in request.GET:
# #         customer_id = request.GET.get('customer_id')
# #         # Fetch the bills associated with the selected customer
# #         bills = FinalSale.objects.filter(customer_id=customer_id)
# #         bill_data = list(bills.values('id', 'billno'))
# #         return JsonResponse({'bills': bill_data})
# #
# #     return JsonResponse({'error': 'Invalid request'}, status=400)
# def get_billnos(request, customer_id):
#     if request.method == "GET":
#         # Fetch the bills associated with the selected customer
#         bills = FinalSale.objects.filter(customer_id=customer_id, is_deleted=False)
#         # bill_data = list(bills.values('billno', 'billno'))
#         # return JsonResponse({'bills': bill_data})
#         # Prepare the list of bill numbers to send in the response
#         bill_list = [{'billno': bill.billno} for bill in bills]
#         return JsonResponse({'bills': bill_list})
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#
#
#
# def submit_selection(request):
#     if request.method == "POST":
#         customer_id = request.POST.get('customer_id')
#         bill_id = request.POST.get('bill_id')
#         selected_categories = request.POST.getlist('categories')
#
#         # Redirect to the final sales return URL with the selected customer and bill IDs
#         return redirect('finalsales_return', pk=bill_id)
#
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.http import JsonResponse
from django.shortcuts import render
from .models import Customer, FinalSale, Category

# @login_required(login_url='user-login')
# def select_customer_view(request):
#     if request.method == "GET":
#         # Fetch all customer types from the Customer model
#         # customer_types = Customer.objects.values_list('Cust_type', flat=True).distinct()
#         customer_types = Customer.objects.filter(
#             Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
#         ).values_list('Cust_type', flat=True).distinct()
#
#         # Fetch only customers with non-deleted FinalSale entries
#         customers = Customer.objects.filter(
#             Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
#         ).order_by('Comp_name')
#
#         categories = Category.objects.all()
#         return render(request, 'return/select_customer.html',
#                       {'customers': customers, 'categories': categories, 'customer_types': customer_types})
#
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url='user-login')
def select_customer_view(request):
    if request.method == "GET":
        # Get distinct customer types from FinalSale-related customers
        customer_types = Customer.objects.filter(
            Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
        ).values_list('Cust_type', flat=True).distinct()

        # Get customers that have non-deleted FinalSale entries
        customers = Customer.objects.filter(
            Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
        ).order_by('Comp_name')

        categories = Category.objects.all()

        vendor_types = Vendor.objects.filter(
            id__in=FinalSale.objects.filter(is_deleted=False).values_list('vendor', flat=True)
        ).values_list('category__name', flat=True).distinct()

        vendors = Vendor.objects.filter(
            id__in=FinalSale.objects.filter(is_deleted=False).values_list('vendor', flat=True).distinct()
        ).order_by('name')

        return render(request, 'return/select_customer.html', {
            'customers': customers,
            'categories': categories,
            'customer_types': customer_types,
            'vendors': vendors,
            'vendor_types': vendor_types
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# def get_customers_by_type(request, customer_type):
#     if request.method == "GET":
#         customers = Customer.objects.filter(Cust_type=customer_type)
#         customer_list = [{'Cust_id': customer.Cust_id, 'Comp_name': customer.Comp_name} for customer in customers]
#         return JsonResponse({'customers': customer_list})
#     return JsonResponse({'error': 'Invalid request'}, status=400)

from django.http import JsonResponse
from .models import Customer, FinalSale

# @login_required(login_url='user-login')
# def get_customers_by_type(request, customer_type):
#     if request.method == "GET":
#         # Fetch customers based on customer_type and related FinalSale entries
#         customers = Customer.objects.filter(
#             Cust_type=customer_type,
#             Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
#         ).order_by('Comp_name')
#
#         customer_list = [{'Cust_id': customer.Cust_id, 'Comp_name': customer.Comp_name} for customer in customers]
#         return JsonResponse({'customers': customer_list})
#     return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='user-login')
def get_customers_by_type(request, customer_type):
    if request.method == "GET":
        # Fetch customers with matching type and validated by FinalSale
        customers = Customer.objects.filter(
            Cust_type=customer_type,
            Cust_id__in=FinalSale.objects.filter(is_deleted=False).values_list('customer_id', flat=True)
        ).order_by('Comp_name')

        customer_list = []
        for customer in customers:
            comp_name = customer.Comp_name or ''
            city = customer.City or ''
            consumer = customer.Consumer or ''
            last_four = consumer[-4:] if len(consumer) >= 4 else consumer
            display_name = f"{comp_name}, {city} - (Mseb - {last_four})"
            customer_list.append({
                'Cust_id': customer.Cust_id,
                'Comp_name': display_name
            })

        return JsonResponse({'customers': customer_list})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='user-login')
def get_vendor_by_type(request, vendor_type):
    if request.method == "GET":
        # Filter using the related Category's name
        vendors = Vendor.objects.filter(
            category__name=vendor_type,
            id__in=FinalSale.objects.filter(is_deleted=False).values_list('vendor_id', flat=True)
        ).order_by('name')
        vendor_list = [{'id': v.id,
                        # 'name': v.name
                        'name': f"{v.name},  {v.city}"
        } for v in vendors]
        return JsonResponse({'vendor': vendor_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='user-login')
def get_categories_by_billno(request, billno):
    if request.method == "GET":
        # Fetch all FinalSaleItems related to the selected bill number
        final_sale_items = FinalSaleItem.objects.filter(final_bill__billno=billno)

        # Fetch all stock IDs related to the selected bill number
        stock_ids = final_sale_items.values_list('stock', flat=True)

        # Fetch categories that match the stock_ids
        categories = Category.objects.filter(stock__in=stock_ids).distinct()

        # Return the filtered categories as JSON
        category_list = [{'id': category.id, 'name': category.name} for category in categories]
        return JsonResponse({'categories': category_list})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='user-login')
def get_billnos(request, customer_id):
    if request.method == "GET":
        bills = FinalSale.objects.filter(customer_id=customer_id, is_deleted=False)
        bill_list = [{'billno': bill.billno} for bill in bills]
        return JsonResponse({'bills': bill_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='user-login')
def get_vendor_billnos(request, vendor_id):
    if request.method == "GET":
        # Filter FinalSale by vendor_id (assuming your field is named vendor_id)
        bills = FinalSale.objects.filter(vendor_id=vendor_id, is_deleted=False)
        bill_list = [{'billno': bill.billno} for bill in bills]
        return JsonResponse({'bills': bill_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='user-login')
def return_sale_view_edit(request, pk):
    sale_bill = get_object_or_404(FinalSale, pk=pk)
    sale_items = FinalSaleItem.objects.filter(final_bill=sale_bill)

    # For each item, retrieve the related serial numbers from PurchaseSerial
    for item in sale_items:
        item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=pk)

    try:
        final_bill_details = FinalBillDetails.objects.get(billno=sale_bill)
    except FinalBillDetails.DoesNotExist:
        final_bill_details = None

    existing_stock_ids = sale_items.values_list('stock_id', flat=True)
    categories = Category.objects.active_only()
    subcategories = SubCategory.objects.active_only()
    stocks = Stock.objects.filter(is_deleted=False)

    context = {
        'sale_bill': sale_bill,
        'sale_items': sale_items,
        'sale_bill_details': final_bill_details,
        'categories': categories,
        'subcategories': subcategories,
        'stocks': stocks,
        'existing_stock_ids': list(existing_stock_ids),
    }

    if request.method == "POST":
        # Update SaleBill fields
        # sale_bill.name = request.POST.get("name", sale_bill.name)
        # sale_bill.phone = request.POST.get("phone", sale_bill.phone)
        # sale_bill.address = request.POST.get("address", sale_bill.address)
        # sale_bill.email = request.POST.get("email", sale_bill.email)
        sale_bill.return_date = timezone.now()
        sale_bill.return_bill = True
        sale_bill.save()
        #
        # sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)
        #
        # # Update SaleBillDetails fields
        # if final_bill_details:
        #     final_bill_details.billno = sale_bill_instance,  # Now passing the correct SaleBill instance
        #     final_bill_details.eway = request.POST.get("eway_no", final_bill_details.eway)
        #     final_bill_details.tcs = request.POST.get("bill_date", final_bill_details.tcs)
        #     final_bill_details.veh = request.POST.get("veh_no", final_bill_details.veh)
        #     final_bill_details.sgst = request.POST.get("arrange", final_bill_details.sgst)
        #     final_bill_details.igst = request.POST.get("handby", final_bill_details.igst)
        #     final_bill_details.destination = request.POST.get("destination", final_bill_details.destination)
        #     final_bill_details.po = request.POST.get("po_no", final_bill_details.po)
        #     final_bill_details.cgst = request.POST.get("po_date", final_bill_details.cgst)
        #     final_bill_details.save()

        # sale_bill_instance = sale_bill.billno  # Replace 'related_salebill' with the actual field name
        # Assuming FinalSale and SaleBill are related, such as through a ForeignKey or OneToOneField
        sale_bill_instance = FinalSale.objects.get(billno=sale_bill.billno)

        final_bill_details = FinalBillDetails(
            billno=sale_bill_instance,  # Now passing the correct SaleBill instance
            eway=request.POST.get('eway_no'),
            cgst=request.POST.get('bill_date'),
            veh=request.POST.get('veh_no'),
            sgst=request.POST.get('arrange'),
            igst=request.POST.get('handby'),
            destination=request.POST.get('destination'),
            po=request.POST.get('po_no'),
            tcs=request.POST.get('po_date'),
        )
        final_bill_details.save()

        # Update SaleItems and Stock
        serials_data = {
            key.split('-')[1]: value.split(',')
            for key, value in request.POST.items() if key.startswith('serials-')
        }

        for stock_id, serial_numbers in serials_data.items():
            PurchaseSerial.objects.filter(stock_id=stock_id).update(final_salebill=None)
            PurchaseSerial.objects.filter(
                stock_id=stock_id,
                serialNo__in=serial_numbers
            ).update(final_salebill=sale_bill.billno)


        for item in sale_items:
            quantity = request.POST.get(f'total_quantity_{item.pk}')
            r_quantity = request.POST.get(f'return_quantity_{ item.pk }')
            if quantity:
                previous_quantity = item.total_quantity
                item.quantity = int(quantity)
                item.final_quantity = int(quantity)
                item.r_quantity = int(r_quantity)
                item.save()

                stock = item.stock
                stock_quantity = stock.quantity
                quantity_change = item.quantity - previous_quantity
                stock.quantity = stock_quantity - quantity_change
                stock.save()

        # Process new items
        new_stock_ids = request.POST.getlist("stock_ids[]")
        new_quantities = request.POST.getlist("quantities[]")
        for stock_id, quantity in zip(new_stock_ids, new_quantities):
            stock = Stock.objects.get(pk=stock_id)
            SaleItem.objects.create(
                billno=sale_bill,
                stock=stock,
                quantity=int(quantity),
                totalprice=1 * int(quantity),  # Assuming `price` is handled
                sale=stock.sales,
            )
            stock.quantity -= int(quantity)
            stock.save()

        # Handle removed items
        existing_ids = set(item.pk for item in sale_items)
        retained_ids = set(int(id_) for id_ in request.POST.getlist("existing_ids[]", []))
        removed_ids = existing_ids - retained_ids

        for removed_id in removed_ids:
            item_to_remove = SaleItem.objects.get(pk=removed_id)
            stock = item_to_remove.stock
            quantity_to_remove = item_to_remove.quantity

            PurchaseSerial.objects.filter(
                stock=stock,
                sales_billno=sale_bill.billno
            ).update(sales_billno=None)

            stock.quantity += quantity_to_remove
            stock.save()
            item_to_remove.delete()

        return redirect('finalsales-list')

    return render(request, 'sales/return_edit.html', context)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from .models import SaleBill, SaleItem, Customer, FinalSale

from datetime import datetime, timedelta

# View to render the HTML page

# @login_required(login_url='user-login')
# def merge_sales_bill(request):
#     # customers = Customer.objects.all()
#     # customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()
#
#     customers = SaleBill.objects.filter(final_salebill__isnull=True).values(
#         'Cust_id', 'Cust_id__Comp_name'
#     ).distinct()
#     return render(request, 'sales/return_sale.html', {'customers': customers})

# @login_required(login_url='user-login')
# def merge_sales_bill(request):
#     # Get distinct customers from SaleBill where final_salebill is not created
#     customers = SaleBill.objects.filter(final_salebill__isnull=True, Cust_id__isnull=False).values(
#         'Cust_id', 'Cust_id__Comp_name'
#     ).distinct()
#     # Get distinct vendors from SaleBill (only those with a non-null Vend_id)
#     vendors = SaleBill.objects.filter(final_salebill__isnull=True, Vend_id__isnull=False).values(
#         'Vend_id', 'Vend_id__name'
#     ).distinct()
#     return render(request, 'sales/return_sale.html', {'customers': customers, 'vendors': vendors})

@login_required(login_url='user-login')
def merge_sales_bill(request):
    # Get distinct customers from SaleBill where final_salebill is not created
    # customers = SaleBill.objects.filter(
    #     final_salebill__isnull=True,
    #     Cust_id__isnull=False
    # ).order_by('Cust_id__Comp_name') \
    #  .values('Cust_id', 'Cust_id__Comp_name') \
    #  .distinct()

    customers = SaleBill.objects.filter(
        final_salebill__isnull=True,
        Cust_id__isnull=False
    ).order_by('Cust_id__Comp_name') \
        .values(
        'Cust_id',
        'Cust_id__Comp_name',
        'Cust_id__City',
        'Cust_id__Consumer') \
        .distinct()

    # Get distinct vendors from SaleBill (only those with a non-null Vend_id)
    vendors = SaleBill.objects.filter(
        final_salebill__isnull=True,
        Vend_id__isnull=False
    ).order_by('Vend_id__name') \
     .values('Vend_id', 'Vend_id__name',
             'Vend_id__city') \
     .distinct()

    return render(request, 'sales/return_sale.html', {'customers': customers, 'vendors': vendors})

# # AJAX view to fetch customer bills
# def get_customer_bills(request):
#     customer_id = request.GET.get('customer_id')
#     bills = SaleBill.objects.filter(Cust_id=customer_id)
#     response = []
#     for bill in bills:
#         response.append({
#             'billno': bill.billno,
#             'time': bill.time.strftime('%Y-%m-%d %H:%M:%S'),
#             'total_price': bill.get_total_price(),
#         })
#     return JsonResponse({'bills': response})


def _format_bill_time_for_json(tm):
    """SaleBill.time may be datetime, date, str (legacy/raw DB), or None."""
    if tm is None:
        return ""
    if isinstance(tm, datetime):
        return tm.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(tm, date):
        return tm.strftime("%Y-%m-%d")
    if isinstance(tm, str):
        return tm.strip()
    if hasattr(tm, "strftime"):
        try:
            return tm.strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            return str(tm)
    return str(tm)


def _open_sale_bills_queryset_with_item_total(**filter_kwargs):
    """
    SaleBills matching filter_kwargs with total_calc = sum(SaleItem.totalprice).
    Uses a correlated Subquery so PostgreSQL does not require GROUP BY on all
    SaleBill columns when ordering by time (annotate(Sum(...)) + order_by breaks PG).
    """
    total_subq = (
        SaleItem.objects.filter(billno_id=OuterRef("pk"))
        .values("billno_id")
        .annotate(_t=Sum("totalprice"))
        .values("_t")[:1]
    )
    return (
        SaleBill.objects.filter(**filter_kwargs)
        .annotate(
            total_calc=Coalesce(
                Subquery(total_subq, output_field=IntegerField()),
                Value(0),
            ),
        )
        .order_by("-time", "-billno")
    )


@login_required(login_url='user-login')
def get_customer_bills(request):
    """
    JSON list of open SaleBills (no FinalSale yet) for a customer or vendor.
    Hardened: valid IDs, default queryset, null-safe time, totals via subquery Sum.
    """
    bills = SaleBill.objects.none()
    customer_id = (request.GET.get("customer_id") or "").strip()
    vendor_id = (request.GET.get("vendor_id") or "").strip()

    try:
        if customer_id:
            cid = int(customer_id)
            bills = _open_sale_bills_queryset_with_item_total(
                Cust_id_id=cid,
                final_salebill_id__isnull=True,
            )
        elif vendor_id:
            vid = int(vendor_id)
            bills = _open_sale_bills_queryset_with_item_total(
                Vend_id_id=vid,
                final_salebill_id__isnull=True,
            )

        payload = []
        for bill in bills:
            time_str = _format_bill_time_for_json(bill.time)
            total = getattr(bill, "total_calc", None)
            if total is None:
                total = 0
            try:
                total = int(total)
            except (TypeError, ValueError):
                try:
                    total = float(total)
                except (TypeError, ValueError):
                    total = 0
            payload.append(
                {"billno": bill.billno, "time": time_str, "total": total}
            )

        return JsonResponse({"bills": payload})
    except (TypeError, ValueError):
        return JsonResponse(
            {"bills": [], "error": "Invalid customer_id or vendor_id"},
            status=400,
        )
    except Exception:
        logger.exception("get_customer_bills")
        return JsonResponse(
            {"bills": [], "error": "Could not load bills"},
            status=500,
        )
#
# @login_required(login_url='user-login')
# def get_vendor_bills(request):
#     vendor_id = request.GET.get('vendor_id')
#     if vendor_id:
#         # Use Vend_id_id to filter on the underlying foreign key id
#         bills = SaleBill.objects.filter(Vend_id_id=vendor_id, final_salebill__isnull=True)
#         data = {
#             "bills": [
#                 {
#                     "billno": bill.billno,
#                     "time": bill.time.strftime('%Y-%m-%d %H:%M:%S'),
#                     "total": bill.get_total_price(),
#                 }
#                 for bill in bills
#             ]
#         }
#         return JsonResponse(data)


# # AJAX view to merge bills and create a final bill
# @csrf_exempt
# def generate_final_bill(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         bill_ids = data.get("bill_ids", [])
#
#         # Get selected bills
#         selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
#
#         # Aggregate stock and quantity
#         stock_totals = {}
#         total_quantity = 0
#         for bill in selected_bills:
#             for item in bill.get_items_list():
#                 if item.stock_id not in stock_totals:
#                     stock_totals[item.stock_id] = {
#                         "name": item.stock.name,
#                         "quantity": 0,
#                         "unit_price": item.perprice
#                     }
#                 stock_totals[item.stock_id]["quantity"] += item.quantity
#                 total_quantity += item.quantity
#
#         # Create FinalSale and FinalSaleItems
#         if selected_bills.exists():
#             first_bill = selected_bills.first()
#             final_sale = FinalSale.objects.create(
#                 customer=first_bill.Cust_id,
#                 total_amount=sum(item["quantity"] * item["unit_price"] for item in stock_totals.values())
#             )
#
#             for stock_id, details in stock_totals.items():
#                 FinalSaleItem.objects.create(
#                     final_bill=final_sale,
#                     stock_id=stock_id,
#                     total_quantity=details["quantity"],
#                     unit_price=details["unit_price"],
#                     total_price=details["quantity"] * details["unit_price"]
#                 )
#
#             # Prepare stock details for the response
#             stock_details = [
#                 {"name": details["name"], "quantity": details["quantity"]}
#                 for details in stock_totals.values()
#             ]
#
#             # Return the final bill details in the response
#             return JsonResponse({
#                 "success": True,
#                 "final_bill": {
#                     "billno": final_sale.billno,
#                     "customer_name": final_sale.customer.Comp_name,
#                     "total_quantity": total_quantity,
#                     "total_amount": final_sale.total_amount,
#                     "time": final_sale.time.strftime('%Y-%m-%d %H:%M:%S'),
#                     "stock_details": stock_details
#                 }
#             })
#     return JsonResponse({"success": False})

# @csrf_exempt
# @login_required(login_url='user-login')
# def generate_final_bill(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         bill_ids = data.get("bill_ids", [])
#
#         # Get selected bills
#         selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
#
#         # Aggregate stock and quantity
#         stock_totals = {}
#         total_quantity = 0
#         for bill in selected_bills:
#             for item in bill.get_items_list():
#                 if item.stock_id not in stock_totals:
#                     stock_totals[item.stock_id] = {
#                         "name": item.stock.name,
#                         "quantity": 0,
#                         "unit_price": item.perprice
#                     }
#                 stock_totals[item.stock_id]["quantity"] += item.quantity
#                 total_quantity += item.quantity
#
#         # Create FinalSale and FinalSaleItems
#         if selected_bills.exists():
#             first_bill = selected_bills.first()
#             final_sale = FinalSale.objects.create(
#                 customer=first_bill.Cust_id,
#                 total_amount=sum(item["quantity"] * item["unit_price"] for item in stock_totals.values()),
#                 # total_quantity=total_quantity,
#                 time=timezone.now(),
#             )
#
#             for stock_id, details in stock_totals.items():
#                 FinalSaleItem.objects.create(
#                     final_bill=final_sale,
#                     stock_id=stock_id,
#                     total_quantity=details["quantity"],
#                     unit_price=details["unit_price"],
#                     total_price=details["quantity"] * details["unit_price"]
#                 )
#
#             # Update the `final_salebillno` field in SaleBill table for the selected bills
#             selected_bills.update(final_salebill=final_sale.billno)
#
#             # Update the `final_salebill` field in PurchaseSerial table for the selected bills
#             PurchaseSerial.objects.filter(sales_billno__in=selected_bills).update(final_salebill=final_sale)
#
#             # Prepare stock details for the response
#             stock_details = [
#                 {"name": details["name"], "quantity": details["quantity"]}
#                 for details in stock_totals.values()
#             ]
#
#             # Return the final bill details in the response
#             return JsonResponse({
#                 "success": True,
#                 "final_bill": {
#                     "billno": final_sale.billno,
#                     "customer_name": final_sale.customer.Comp_name,
#                     "total_quantity": total_quantity,
#                     "total_amount": final_sale.total_amount,
#                     "time": final_sale.time.strftime('%Y-%m-%d %H:%M:%S'),
#                     "stock_details": stock_details
#                 }
#             })
#     return JsonResponse({"success": False})
#
@csrf_exempt
@login_required(login_url='user-login')
def generate_final_bill(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        bill_ids = data.get("bill_ids", [])

        # Get selected bills
        selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
        if not selected_bills.exists():
            return JsonResponse({"success": False})

        # Aggregate stock and quantity from selected bills
        stock_totals = {}
        total_quantity = 0
        for bill in selected_bills:
            for item in bill.get_items_list():
                if item.stock_id not in stock_totals:
                    stock_totals[item.stock_id] = {
                        "name": item.stock.name,
                        "quantity": 0,
                        "unit_price": item.perprice
                    }
                stock_totals[item.stock_id]["quantity"] += item.quantity
                total_quantity += item.quantity

        # Use the first bill to determine if it's a vendor bill or a customer bill
        first_bill = selected_bills.first()

        # Initialize party_name for the final response
        if first_bill.Vend_id:
            # Creating final bill for vendor bills
            final_sale = FinalSale.objects.create(
                vendor=first_bill.Vend_id,  # make sure your FinalSale model has a vendor field
                total_amount=sum(details["quantity"] * details["unit_price"] for details in stock_totals.values()),
                time=timezone.now(),
            )
            party_name = final_sale.vendor.name  # adjust field name as needed
        else:
            # Creating final bill for customer bills
            final_sale = FinalSale.objects.create(
                customer=first_bill.Cust_id,
                total_amount=sum(details["quantity"] * details["unit_price"] for details in stock_totals.values()),
                time=timezone.now(),
            )
            party_name = final_sale.customer.Comp_name

        # Create FinalSaleItems for each stock entry
        for stock_id, details in stock_totals.items():
            FinalSaleItem.objects.create(
                final_bill=final_sale,
                stock_id=stock_id,
                total_quantity=details["quantity"],
                unit_price=details["unit_price"],
                total_price=details["quantity"] * details["unit_price"]
            )

        # Update SaleBill and PurchaseSerial records with the generated final bill
        selected_bills.update(final_salebill=final_sale.billno)
        PurchaseSerial.objects.filter(sales_billno__in=selected_bills).update(final_salebill=final_sale)

        # Prepare stock details for the response
        stock_details = [
            {"name": details["name"], "quantity": details["quantity"]}
            for details in stock_totals.values()
        ]

        # Return the final bill details in the response (using 'party_name' instead of customer_name)
        return JsonResponse({
            "success": True,
            "final_bill": {
                "billno": final_sale.billno,
                "customer_name": party_name,
                "total_quantity": total_quantity,
                "total_amount": final_sale.total_amount,
                "time": final_sale.time.strftime('%Y-%m-%d %H:%M:%S'),
                "stock_details": stock_details
            }
        })
    return JsonResponse({"success": False})


# def edit_final_sale(request, billno):
#     # Fetch the final sale record
#     final_sale = FinalSale.objects.get(billno=billno)
#     customer_id = final_sale.customer_id
#
#     # Get all bills related to the customer
#     all_bills = SaleBill.objects.filter(Cust_id=customer_id)
#     bills_data = []
#     for bill in all_bills:
#         bills_data.append({
#             "billno": bill.billno,
#             "time": bill.time.strftime('%Y-%m-%d %H:%M:%S'),
#             "total": bill.get_total_price(),
#             "is_merged": bill.final_salebill == final_sale
#         })
#
#     customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()
#
#     return render(request, 'sales/edit_finalsale.html', {
#         "customers": customers,
#         "bills": bills_data,
#         "final_sale": final_sale,
#         "selected_customer_id": customer_id
#     })


@login_required(login_url='user-login')
def edit_final_sale(request, billno):
    # Fetch the final sale record
    final_sale = FinalSale.objects.get(billno=billno)
    customer_id = final_sale.customer_id

    # Get all bills related to the customer with final_salebill=None or associated with the current final_sale
    all_bills = SaleBill.objects.filter(
        Cust_id=customer_id,
    ).filter(Q(final_salebill__isnull=True) | Q(final_salebill=final_sale))

    bills_data = []
    for bill in all_bills:
        bill_time = bill.time
        if isinstance(bill_time, datetime):
            time_display = bill_time.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(bill_time, date):
            time_display = bill_time.strftime('%Y-%m-%d 00:00:00')
        elif bill_time:
            time_display = str(bill_time)
        else:
            time_display = ""

        bills_data.append({
            "billno": bill.billno,
            "time": time_display,
            "total": bill.get_total_price(),
            "is_merged": bill.final_salebill == final_sale,  # Checked if it is already part of the current final sale
        })

    customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()

    return render(request, 'sales/edit_finalsale.html', {
        "customers": customers,
        "bills": bills_data,
        "final_sale": final_sale,
        "selected_customer_id": customer_id
    })


#
# @csrf_exempt
# def update_final_bill(request):
#     if request.method == "POST":
#         import json
#         data = json.loads(request.body)
#         bill_ids = data.get("bill_ids", [])
#         final_billno = data.get("final_billno")
#
#         # Get the final sale record
#         final_sale = FinalSale.objects.get(billno=final_billno)
#
#         # Remove existing associations not in the new bill_ids
#         SaleBill.objects.filter(final_salebill=final_sale).exclude(billno__in=bill_ids).update(final_salebill=None)
#
#         # Add new associations
#         selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
#         selected_bills.update(final_salebill=final_sale)
#
#         # Update FinalSaleItems
#         stock_totals = {}
#         total_quantity = 0
#         for bill in selected_bills:
#             for item in bill.get_items_list():
#                 if item.stock_id not in stock_totals:
#                     stock_totals[item.stock_id] = {
#                         "name": item.stock.name,
#                         "quantity": 0,
#                         "unit_price": item.perprice
#                     }
#                 stock_totals[item.stock_id]["quantity"] += item.quantity
#                 total_quantity += item.quantity
#
#         final_sale.total_amount = sum(
#             item["quantity"] * item["unit_price"] for item in stock_totals.values()
#         )
#         final_sale.save()
#
#         # Update FinalSaleItems
#         FinalSaleItem.objects.filter(final_bill=final_sale).delete()
#         for stock_id, details in stock_totals.items():
#             FinalSaleItem.objects.create(
#                 final_bill=final_sale,
#                 stock_id=stock_id,
#                 total_quantity=details["quantity"],
#                 unit_price=details["unit_price"],
#                 total_price=details["quantity"] * details["unit_price"]
#             )
#
#         return JsonResponse({"success": True})

@csrf_exempt
@login_required(login_url='user-login')
def update_final_bill(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        bill_ids = data.get("bill_ids", [])
        final_billno = data.get("final_billno")

        # Get the final sale record
        final_sale = FinalSale.objects.get(billno=final_billno)

        # Remove existing associations not in the new bill_ids
        SaleBill.objects.filter(final_salebill=final_sale).exclude(billno__in=bill_ids).update(final_salebill=None)
        PurchaseSerial.objects.filter(final_salebill=final_sale).exclude(sales_billno__in=bill_ids).update(final_salebill=None)

        # Add new associations
        selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
        selected_bills.update(final_salebill=final_sale)

        # Update the PurchaseSerial table
        PurchaseSerial.objects.filter(sales_billno__in=bill_ids).update(final_salebill=final_sale)

        # Update FinalSaleItems
        stock_totals = {}
        total_quantity = 0
        for bill in selected_bills:
            for item in bill.get_items_list():
                if item.stock_id not in stock_totals:
                    stock_totals[item.stock_id] = {
                        "name": item.stock.name,
                        "quantity": 0,
                        "unit_price": item.perprice
                    }
                stock_totals[item.stock_id]["quantity"] += item.quantity
                total_quantity += item.quantity

        # Calculate and update the total amount for the final sale
        final_sale.total_amount = sum(
            item["quantity"] * item["unit_price"] for item in stock_totals.values()
        )
        final_sale.update_time = timezone.now()  # Add the update time
        final_sale.save()

        # Update FinalSaleItems
        FinalSaleItem.objects.filter(final_bill=final_sale).delete()
        for stock_id, details in stock_totals.items():
            FinalSaleItem.objects.create(
                final_bill=final_sale,
                stock_id=stock_id,
                total_quantity=details["quantity"],
                unit_price=details["unit_price"],
                total_price=details["quantity"] * details["unit_price"]
            )

        return JsonResponse({"success": True})


# def delete_final_sale(request, pk):
#         final_sale = get_object_or_404(FinalSale, pk=pk)
#
#         # Update the final_salebill field in all SaleBill records related to this FinalSale
#         sale_bills = SaleBill.objects.filter(final_salebill=final_sale)
#         sale_bills.update(final_salebill=None)  # This will set final_salebill to None for all related SaleBill records
#
#         # Perform the deletion of the FinalSale and related FinalSaleItems
#         final_sale.delete()
#
#         # Add a success message
#         messages.success(request, "Final Sale record and related items deleted successfully, SaleBills updated.")
#
#         # Redirect back to the list view
#         return redirect('finalsales-list')  # Replace 'finalsale-list' with the name of your list view


def cleanup_purchase_serials_before_return_sale_delete(return_sale):
    """
    Before deleting a ReturnSale row, detach PurchaseSerial rows and remove orphan
    duplicates (same stock + serial, all sales_billno/final_salebill/return_bill NULL).
    Keeps the linked row and clears only return_bill on it.
    """
    if return_sale is None:
        return
    linked = list(
        PurchaseSerial.objects.filter(return_bill=return_sale).only(
            "id", "stock_id", "serialNo"
        )
    )
    for ps in linked:
        key = (ps.serialNo or "").strip()
        orphan_ids = []
        if key:
            for cand in PurchaseSerial.objects.filter(stock_id=ps.stock_id).exclude(
                pk=ps.pk
            ).only("id", "serialNo", "sales_billno_id", "final_salebill_id", "return_bill_id"):
                if (cand.serialNo or "").strip() != key:
                    continue
                if (
                    cand.sales_billno_id is None
                    and cand.final_salebill_id is None
                    and cand.return_bill_id is None
                ):
                    orphan_ids.append(cand.pk)
        if orphan_ids:
            PurchaseSerial.objects.filter(pk__in=orphan_ids).delete()
        PurchaseSerial.objects.filter(pk=ps.pk).update(return_bill=None)


def restore_finalsaleitem_quantities_before_return_sale_delete(return_sale):
    """
    Before deleting a ReturnSale row, roll back FinalSaleItem quantities
    using the quantities stored on that return bill's ReturnSaleItem rows.
    """
    if return_sale is None:
        return
    return_items = ReturnSaleItem.objects.filter(return_bill=return_sale).select_related(
        "final_bill", "stock"
    )
    for ret_item in return_items:
        if not ret_item.final_bill_id:
            continue
        fs_item = FinalSaleItem.objects.filter(
            final_bill=ret_item.final_bill, stock=ret_item.stock
        ).first()
        if not fs_item:
            continue
        returned_qty = ret_item.r_quantity or Decimal("0")
        current_r_qty = fs_item.r_quantity or Decimal("0")
        current_final_qty = (
            fs_item.final_quantity
            if fs_item.final_quantity is not None
            else (fs_item.total_quantity or Decimal("0"))
        )
        new_r_qty = current_r_qty - returned_qty
        if new_r_qty < Decimal("0"):
            new_r_qty = Decimal("0")
        fs_item.r_quantity = new_r_qty
        fs_item.final_quantity = current_final_qty + returned_qty
        fs_item.save(update_fields=["r_quantity", "final_quantity"])


def refresh_final_sale_return_flag(final_sale):
    """Clear FinalSale.return_bill when no active return bills remain."""
    if final_sale is None:
        return
    if not ReturnSale.objects.filter(
        final_bill_id=final_sale.pk, is_deleted=False
    ).exists():
        FinalSale.objects.filter(pk=final_sale.pk).update(
            return_bill=False,
            return_date=None,
        )


@login_required
@require_GET
def final_sale_return_bills_for_delete(request, pk):
    """JSON list of return bills linked to a final sale (for delete flow modal)."""
    final_sale = get_object_or_404(FinalSale, pk=pk)
    rows = list(
        ReturnSale.objects.filter(final_bill=final_sale, is_deleted=False)
        .order_by("billno")
        .values("billno", "time")
    )
    payload = [
        {"billno": r["billno"], "date": as_bill_date(r["time"])}
        for r in rows
    ]
    return JsonResponse({"returns": payload, "final_billno": final_sale.billno})


@login_required
@require_POST
def final_sale_delete_return_bills(request, pk):
    """Delete all non-deleted return bills for a final sale; fix PurchaseSerial rows; then client redirects to final delete."""
    final_sale = get_object_or_404(FinalSale, pk=pk)
    returns = list(
        ReturnSale.objects.filter(final_bill=final_sale, is_deleted=False).order_by(
            "billno"
        )
    )
    redir = reverse("delete-final-sale", kwargs={"pk": pk})
    if not returns:
        return JsonResponse({"success": True, "redirect": redir})
    with transaction.atomic():
        for r in returns:
            restore_finalsaleitem_quantities_before_return_sale_delete(r)
            cleanup_purchase_serials_before_return_sale_delete(r)
            r.delete()
        refresh_final_sale_return_flag(final_sale)
    return JsonResponse({"success": True, "redirect": redir})


class ReturnSaleDeleteView(LoginRequiredMixin, View):
    """Delete one return bill with the same PurchaseSerial rules as bulk final-sale delete."""

    template_name = "return/delete_return_sale.html"
    login_url = "/index/"

    def get(self, request, *args, **kwargs):
        return_sale = get_object_or_404(ReturnSale, pk=kwargs["pk"])
        return render(
            request,
            self.template_name,
            {"return_sale": return_sale},
        )

    def post(self, request, *args, **kwargs):
        return_sale = get_object_or_404(ReturnSale, pk=kwargs["pk"])
        final_bill = return_sale.final_bill
        with transaction.atomic():
            restore_finalsaleitem_quantities_before_return_sale_delete(return_sale)
            cleanup_purchase_serials_before_return_sale_delete(return_sale)
            return_sale.delete()
            refresh_final_sale_return_flag(final_bill)
        messages.success(request, "Return bill deleted successfully.")
        return redirect(reverse("returnsales-list"))


class FinalSaleDeleteView(LoginRequiredMixin, View):
    template_name = "sales/delete_final_sale.html"  # Template for confirmation
    login_url = '/index/'

    def get(self, request, *args, **kwargs):
        # Display the confirmation page
        final_sale = get_object_or_404(FinalSale, pk=kwargs['pk'])
        blocking_returns = ReturnSale.objects.filter(
            final_bill=final_sale, is_deleted=False
        ).exists()
        return render(
            request,
            self.template_name,
            {
                'final_sale': final_sale,
                'blocking_returns': blocking_returns,
            },
        )

    def post(self, request, *args, **kwargs):
        # Perform the deletion and stock update
        final_sale = get_object_or_404(FinalSale, pk=kwargs['pk'])
        if ReturnSale.objects.filter(final_bill=final_sale, is_deleted=False).exists():
            messages.error(
                request,
                "A Return Bill is still linked to this Final Bill. Delete the related Return Bill(s) first.",
            )
            return redirect(reverse("finalsales-list"))
        final_sale_items = FinalSaleItem.objects.filter(final_bill=final_sale)

        # # Step 1: Restore stock quantities from FinalSaleItems
        # for item in final_sale_items:
        #     stock = Stock.objects.filter(id=item.stock.id, is_deleted=False).first()
        #     if stock:
        #         stock.quantity += item.total_quantity  # Restore the quantity
        #         stock.save()


        # Step 3: Set 'final_salebill' to None in all SaleBill records related to the FinalSale
        sale_bills = SaleBill.objects.filter(final_salebill=final_sale)
        sale_bills.update(final_salebill=None)  # Unlink SaleBill from FinalSale

        # Step 3: Set 'final_salebill' to None in all SaleBill records related to the FinalSale
        sale_bills_details = PurchaseSerial.objects.filter(final_salebill=final_sale)
        sale_bills_details.update(final_salebill=None)  # Unlink SaleBill from FinalSale



        # Step 4: Delete FinalSaleItems and FinalSale
        final_sale_items.delete()  # Deleting the related FinalSaleItems
        # final_sale.delete()  # Deleting the FinalSale
        # final_sale.update(is_deleted=True)  # Unlink SaleBill from FinalSale
        final_sale.is_deleted = True
        final_sale.save()

        # Add a success message
        messages.success(request, "Final Sale record and related items deleted successfully. SaleBills updated.")

        # Redirect after deletion (ensure you pass the correct pk)
        return redirect(reverse('finalsales-list'))  # Update with correct name for the list view




#
# class FinalSaleBillView(View):
#         model = FinalSale
#         template_name = "bill/final_sale_bill.html"
#         bill_base = "bill/bill_base.html"
#
#         def get(self, request, billno):
#             items = FinalSaleItem.objects.filter(final_bill=billno)
#
#             # For each item, retrieve the related serial numbers from PurchaseSerial
#             for item in items:
#                 item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=billno)
#
#             try:
#                 context = {
#                     'bill': FinalSale.objects.get(billno=billno),
#                     'items': items,
#                     # 'billdetails': FinalSaleItem.objects.get(final_bill=billno),
#                     'bill_base': self.bill_base,
#
#                 }
#                 return render(request, self.template_name, context)
#             except FinalSale.DoesNotExist:
#                 messages.error(request, "Sale bill not found.")
#                 return redirect('some-other-view-name')  # Redirect to a fallback view

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .models import FinalSale, FinalSaleItem, PurchaseSerial, SaleBill, SaleBillDetails

class FinalSaleBillView(LoginRequiredMixin, View):
    model = FinalSale
    template_name = "bill/final_sale_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        # Fetch items from FinalSaleItem based on the final bill number
        items = FinalSaleItem.objects.filter(final_bill=billno)

        # For each item, retrieve the related serial numbers from PurchaseSerial
        for item in items:
            # Criteria 1: return_bill IS NULL (active link)
            serials_return_null = (
                PurchaseSerial.objects
                .filter(
                    stock=item.stock,
                    final_salebill=billno,
                    sales_billno__isnull=False,
                    final_salebill__isnull=False,
                    return_bill__isnull=True,
                )
                .exclude(serialNo__isnull=True)
                .exclude(serialNo='')
                .order_by('serialNo', 'id')
            )

            # Criteria 2: return_bill IS NOT NULL (duplicate same serial case)
            serials_return_not_null = (
                PurchaseSerial.objects
                .filter(
                    stock=item.stock,
                    final_salebill=billno,
                    sales_billno__isnull=False,
                    final_salebill__isnull=False,
                    return_bill__isnull=False,
                )
                .exclude(serialNo__isnull=True)
                .exclude(serialNo='')
                .order_by('serialNo', 'id')
            )

            # If same serial exists in both criteria, prefer return_bill IS NOT NULL row.
            serial_choice = {}
            for serial_obj in serials_return_not_null:
                serial_choice[(serial_obj.serialNo or '').strip()] = serial_obj.id
            for serial_obj in serials_return_null:
                key = (serial_obj.serialNo or '').strip()
                if key and key not in serial_choice:
                    serial_choice[key] = serial_obj.id

            selected_ids = list(serial_choice.values())
            item.serials = (
                PurchaseSerial.objects
                .filter(id__in=selected_ids)
                .order_by('serialNo', 'id')
            )

        # Filter SaleBill records based on the final_salebill (billno in this case)
        sale_bills = SaleBill.objects.filter(final_salebill=billno)

        # Filter SaleBill records based on the final_salebill (billno in this case)
        return_bills = ReturnSale.objects.filter(final_bill=billno)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        sale_bill_details = SaleBillDetails.objects.filter(billno__in=sale_bills)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        return_bill_details = ReturnBillDetails.objects.filter(billno__in=return_bills)

        # Fetch previous SaleBill records (those with a lower billno value)
        previous_bills = SaleBill.objects.filter(final_salebill=billno).exclude(billno=billno).order_by('billno')

        try:
            context = {
                'bill': FinalSale.objects.get(billno=billno),  # Current final sale bill
                'items': items,  # FinalSaleItem data
                'sale_bills': sale_bills,  # Filtered SaleBill records
                'sale_bill_details': sale_bill_details,  # SaleBillDetails related to the SaleBills
                'return_bill_details': return_bill_details,  # SaleBillDetails related to the SaleBills
                'previous_bills': previous_bills,  # Previous SaleBill records
                'bill_base': self.bill_base,
            }
            return render(request, self.template_name, context)
        except FinalSale.DoesNotExist:
            messages.error(request, "Sale bill not found.")
            return redirect('some-other-view-name')  # Redirect to a fallback view



class FinalReturnBillView(LoginRequiredMixin, View):
    model = FinalSale
    template_name = "bill/final_return_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        # Show only returned items on Final Return Bill (hide r_quantity=0/null).
        items = FinalSaleItem.objects.filter(
            final_bill=billno,
            r_quantity__isnull=False,
            r_quantity__gt=0,
        )



        # Filter SaleBill records based on the final_salebill (billno in this case)
        sale_bills = SaleBill.objects.filter(final_salebill=billno)

        # Filter SaleBill records based on the final_salebill (billno in this case)
        return_bills = ReturnSale.objects.filter(final_bill=billno)

        # For each item, retrieve the related serial numbers from PurchaseSerial
        for item in items:
            item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=billno, return_bill__in=return_bills)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        sale_bill_details = SaleBillDetails.objects.filter(billno__in=sale_bills)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        return_bill_details = ReturnBillDetails.objects.filter(billno__in=return_bills)

        # Fetch previous SaleBill records (those with a lower billno value)
        previous_bills = ReturnSale.objects.filter(final_bill=billno).exclude(billno=billno).order_by('billno')

        try:
            context = {
                'bill': FinalSale.objects.get(billno=billno),  # Current final sale bill
                'items': items,  # FinalSaleItem data
                'sale_bills': sale_bills,  # Filtered SaleBill records
                'sale_bill_details': sale_bill_details,  # SaleBillDetails related to the SaleBills
                'return_bill_details': return_bill_details,  # SaleBillDetails related to the SaleBills
                'previous_bills': previous_bills,  # Previous SaleBill records
                'bill_base': self.bill_base,
            }
            return render(request, self.template_name, context)
        except FinalSale.DoesNotExist:
            messages.error(request, "Sale bill not found.")
            return redirect('some-other-view-name')  # Redirect to a fallback view


class GenrateFinalBillView(LoginRequiredMixin, View):
    model = FinalSale
    template_name = "bill/genrate_final_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        # Fetch items from FinalSaleItem based on the final bill number
        items = FinalSaleItem.objects.filter(final_bill=billno)

        # For each item, retrieve the related serial numbers from PurchaseSerial
        for item in items:
            item.serials = PurchaseSerial.objects.filter(stock=item.stock, final_salebill=billno,  return_bill__isnull=True)

        # Filter SaleBill records based on the final_salebill (billno in this case)
        sale_bills = SaleBill.objects.filter(final_salebill=billno)

        # Filter SaleBill records based on the final_salebill (billno in this case)
        return_bills = ReturnSale.objects.filter(final_bill=billno)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        sale_bill_details = SaleBillDetails.objects.filter(billno__in=sale_bills)

        # Fetch the associated SaleBillDetails based on the filtered SaleBill records
        return_bill_details = ReturnBillDetails.objects.filter(billno__in=return_bills)

        # Fetch previous SaleBill records (those with a lower billno value)
        previous_bills = SaleBill.objects.filter(final_salebill=billno).exclude(billno=billno).order_by('billno')

        # Fetch previous SaleBill records (those with a lower billno value)
        previous_return_bills = ReturnSale.objects.filter(final_bill=billno).exclude(billno=billno).order_by('billno')

        try:
            context = {
                'bill': FinalSale.objects.get(billno=billno),  # Current final sale bill
                'items': items,  # FinalSaleItem data
                'sale_bills': sale_bills,  # Filtered SaleBill records
                'sale_bill_details': sale_bill_details,  # SaleBillDetails related to the SaleBills
                'return_bill_details': return_bill_details,  # SaleBillDetails related to the SaleBills
                'previous_bills': previous_bills,  # Previous SaleBill records
                'previous_return_bills': previous_return_bills,  # Previous SaleBill records
                'bill_base': self.bill_base,
            }
            return render(request, self.template_name, context)
        except FinalSale.DoesNotExist:
            messages.error(request, "Sale bill not found.")
            return redirect('some-other-view-name')  # Redirect to a fallback view




#
# # Genrate Return Bill list
# class ReturnSaleView(LoginRequiredMixin, ListView):
#     model = ReturnSale
#     template_name = "return/returnsales_list.html"
#     context_object_name = 'bills'
#     ordering = ['-time']  # Default ordering by 'time'
#     login_url = '/index/'
#
#     def get_queryset(self):
#         # queryset = super().get_queryset()
#         # queryset = super().get_queryset().prefetch_related('return_sale_items',
#         #                                                    'sale_bills')  # Prefetch related SaleBill
#         queryset = super().get_queryset().select_related('customer').prefetch_related('return_sale_items')
#
#         # Start with the base queryset, filtered for is_deleted=False
#         # queryset = super().get_queryset().filter(is_deleted=False).prefetch_related(
#         #     'final_sale_items', 'sale_bills'
#         # )
#
#         # Cust_type filter
#         cust_type = self.request.GET.get('cust_type')
#         if cust_type:
#             queryset = queryset.filter(customer__Cust_type=cust_type)
#
#         # Date filter logic (same as before)
#         filter_value = self.request.GET.get('filter', 'All')
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_value == 'Today':
#             start_date = today
#             end_date = today
#             queryset = queryset.filter(time__date=today)
#         elif filter_value == 'Last7Days':
#             start_date = today - timedelta(days=7)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'Last30Days':
#             start_date = today - timedelta(days=30)
#             end_date = today
#             queryset = queryset.filter(time__gte=start_date)
#         elif filter_value == 'ThisMonth':
#             start_date = today.replace(day=1)
#             end_date = today
#             queryset = queryset.filter(time__month=start_date.month)
#         elif filter_value == 'Custom':
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date and end_date:
#                 queryset = queryset.filter(time__date__range=[start_date, end_date])
#             else:
#                 queryset = queryset.none()
#
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all customer types for cust_type dropdown
#         context['customers'] = Customer.objects.values('Cust_type').distinct()
#
#         # Handle selected cust_type for filtering
#         selected_cust_type = self.request.GET.get('cust_type')
#         context['selected_Cust_type'] = selected_cust_type
#
#
#
#         # Pass filter value to the context
#         filter_option = self.request.GET.get('filter', 'All')
#         context['selected_filter'] = filter_option
#
#         # Date filter caption logic (same as before)
#         today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         start_date, end_date = None, None
#
#         if filter_option == "All":
#             caption_text = "Display All Days View"
#             caption_text1 = "Up To Date"
#         elif filter_option == "Today":
#             start_date = today
#             end_date = today
#             caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Today"
#         elif filter_option == "Last7Days":
#             start_date = today - timedelta(days=7)
#             end_date = today
#             caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 7 Days"
#         elif filter_option == "Last30Days":
#             start_date = today - timedelta(days=30)
#             end_date = today
#             caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "Last 30 Days"
#         elif filter_option == "ThisMonth":
#             start_date = today.replace(day=1)
#             end_date = today
#             caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             caption_text1 = "This Month"
#         elif filter_option == "Custom":
#             start_date_str = self.request.GET.get('start_date')
#             end_date_str = self.request.GET.get('end_date')
#
#             start_date = parse_date(start_date_str) if start_date_str else None
#             end_date = parse_date(end_date_str) if end_date_str else None
#
#             if start_date_str and end_date_str:
#                 caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
#             else:
#                 caption_text = "Display Custom Range View"
#             caption_text1 = "Custom Range"
#         else:
#             caption_text = "The option is not selected, so all records show"
#             caption_text1 = ""
#
#         context['caption_text'] = caption_text
#         context['caption_text1'] = caption_text1
#
#         # Pass custom date range values to the context
#         context['start_date'] = self.request.GET.get('start_date', '')
#         context['end_date'] = self.request.GET.get('end_date', '')
#
#         return context


# Genrate Return Bill list
class ReturnSaleView(LoginRequiredMixin, ListView):
    model = ReturnSale
    template_name = "return/returnsales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']  # Default ordering by 'time'
    login_url = '/index/'

    def get_queryset(self):
        # queryset = super().get_queryset()
        # queryset = super().get_queryset().select_related('customer').prefetch_related('return_sale_items')
        queryset = super().get_queryset().select_related('customer', 'vendor').prefetch_related(
            Prefetch(
                'return_sale_items',
                queryset=ReturnSaleItem.objects.filter(r_quantity__gt=0),
                to_attr='positive_return_items'
            )
        )

        # Get user type (default to All)
        user_type = self.request.GET.get("user_type", "All")

        if user_type == "Consumer":
            # Only show consumer records.
            # Apply consumer category filter if provided and not "All"
            cust_type = self.request.GET.get("cust_type", "All")
            if cust_type != "All" and cust_type:
                queryset = queryset.filter(customer__Cust_type=cust_type)
            else:
                # Assuming consumer records are identified by having a non-null Cust_id.
                queryset = queryset.filter(customer__isnull=False)
        elif user_type == "Vendor":
            # Only show vendor records.
            # Apply vendor category filter if provided and not "All"
            vendor_category = self.request.GET.get("vendor_category", "All")
            if vendor_category != "All" and vendor_category:
                # queryset = queryset.filter(vendor__category_id=vendor_category)
                queryset = queryset.filter(vendor__category_id=vendor_category)
            else:
                # Assuming vendor records are identified by having a non-null vendor field.
                queryset = queryset.filter(vendor__isnull=False)
        elif user_type == "All":
            # No filtering based on user type; show all records.
            pass

        # Date filter logic (safe for legacy schemas where `time` may be text-like)
        filter_value = self.request.GET.get("filter", "All")
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None
        table_name = ReturnSale._meta.db_table

        def _apply_text_date_between(qs, start_dt, end_dt):
            # Avoid ORM __date/__month transforms that generate AT TIME ZONE on PostgreSQL.
            return qs.extra(
                where=[
                    f"substring(COALESCE({table_name}.time::text, ''), 1, 10) BETWEEN %s AND %s"
                ],
                params=[start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")],
            )

        if filter_value == "Today":
            start_date = today
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            queryset = _apply_text_date_between(queryset, start_date, end_date)
        elif filter_value == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")

            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            if start_date and end_date:
                queryset = _apply_text_date_between(queryset, start_date, end_date)
            else:
                queryset = queryset.none()

        queryset = _scope_dc_list_queryset_for_associate(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # For Consumer category dropdown
        context["customers"] = Customer.objects.values("Cust_type").distinct()
        selected_cust_type = self.request.GET.get("cust_type", "All")
        context["selected_Cust_type"] = selected_cust_type

        # For Vendor category dropdown (using Category model)
        context["vendor_categories"] = Category.objects.all()
        selected_vendor_category = self.request.GET.get("vendor_category", "All")
        context["selected_vendor_category"] = selected_vendor_category

        # User type (default to All)
        selected_user_type = self.request.GET.get("user_type", "All")
        context["selected_user_type"] = selected_user_type

        # Date filter value
        filter_option = self.request.GET.get("filter", "All")
        context["selected_filter"] = filter_option

        # Date filter caption logic
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date, end_date = None, None

        if filter_option == "All":
            caption_text = "Display All Days View"
            caption_text1 = "Up To Date"
        elif filter_option == "Today":
            start_date = today
            end_date = today
            caption_text = f"Display Today View {start_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Today"
        elif filter_option == "Last7Days":
            start_date = today - timedelta(days=7)
            end_date = today
            caption_text = f"Display Last 7 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 7 Days"
        elif filter_option == "Last30Days":
            start_date = today - timedelta(days=30)
            end_date = today
            caption_text = f"Display Last 30 Days View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "Last 30 Days"
        elif filter_option == "ThisMonth":
            start_date = today.replace(day=1)
            end_date = today
            caption_text = f"Display This Month View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            caption_text1 = "This Month"
        elif filter_option == "Custom":
            start_date_str = self.request.GET.get("start_date")
            end_date_str = self.request.GET.get("end_date")

            start_date = parse_date(start_date_str) if start_date_str else None
            end_date = parse_date(end_date_str) if end_date_str else None

            if start_date and end_date:
                caption_text = f"Display Custom Range View {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            else:
                caption_text = "Display Custom Range View"
            caption_text1 = "Custom Range"
        else:
            caption_text = "The option is not selected, so all records show"
            caption_text1 = ""

        context["caption_text"] = caption_text
        context["caption_text1"] = caption_text1

        # Pass custom date range values to the context
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")

        return context


# Return bill genrate
class ReturnBillView(LoginRequiredMixin, View):
    model = ReturnSale
    template_name = "bill/return_bill.html"
    bill_base = "bill/bill_base.html"
    login_url = '/index/'

    def get(self, request, billno):
        # items = ReturnSaleItem.objects.filter(return_bill=billno)
        items = [item for item in ReturnSaleItem.objects.filter(return_bill=billno) if item.r_quantity > 0]

        # For each item, retrieve the related serial numbers from PurchaseSerial
        for item in items:
            item.serials = PurchaseSerial.objects.filter(stock=item.stock, return_bill=billno)


        try:
             context = {
                    'bill': ReturnSale.objects.get(billno=billno),
                    'items': items,
                    'billdetails': ReturnBillDetails.objects.get(billno=billno),
                    'bill_base': self.bill_base,
             }
             return render(request, self.template_name, context)
        except ReturnSale.DoesNotExist:
            messages.error(request, "Return bill not found.")
            return redirect('some-other-view-name')  # Redirect to a fallback view




#     # View to render the HTML page for editing a sale
# def edit_finalsale(request, billno):
#         sale_bill = get_object_or_404(FinalSale, billno=billno)
#         customer = sale_bill.customer
#
#         # Get all bills related to the customer, including those linked to FinalSale
#         related_bills = SaleBill.objects.filter(Cust_id=customer)
#         final_sale_bills = FinalSale.objects.filter(customer=customer)
#
#         # Prepare the data for the template
#         related_bills_data = [
#             {
#                 "billno": bill.billno,
#                 "is_final_sale": False,
#                 "checked": bill.final_salebill is not None
#             }
#             for bill in related_bills
#         ]
#         final_sale_bills_data = [
#             {
#                 "billno": final_bill.billno,
#                 "is_final_sale": True,
#                 "checked": True
#             }
#             for final_bill in final_sale_bills
#         ]
#
#         context = {
#             "sale_bill": sale_bill,
#             "customer": customer,
#             "related_bills": related_bills_data,
#             "final_sale_bills": final_sale_bills_data
#         }
#         return render(request, "sales/edit_finalsale.html", context)
#
#     # View to handle merging bills
# @csrf_exempt
# def update_and_merge_bills(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         selected_bill_ids = data.get("bill_ids", [])
#         current_billno = data.get("current_billno")
#
#         # Fetch FinalSale bill numbers only
#         final_sale_billnos = FinalSale.objects.values_list('billno', flat=True)
#
#         # Filter selected_bill_ids to include only those that exist in FinalSale
#         valid_bill_ids = [bill_id for bill_id in selected_bill_ids if bill_id in final_sale_billnos]
#
#         # Fetch the current SaleBill
#         current_sale_bill = get_object_or_404(SaleBill, billno=current_billno)
#
#         # Unlink SaleBills not in the valid bill IDs
#         SaleBill.objects.filter(final_salebill=current_sale_bill.final_salebill).exclude(billno__in=valid_bill_ids).update(final_salebill=None)
#
#         # Handle linking to the valid FinalSale
#         if valid_bill_ids:
#             final_sale = FinalSale.objects.filter(billno__in=valid_bill_ids).first()
#
#             # Update SaleBills to link them to the selected FinalSale
#             SaleBill.objects.filter(billno__in=valid_bill_ids).update(final_salebill=final_sale)
#
#             # Update the total amount of the selected FinalSale
#             total_amount = 0
#             for sale_bill in SaleBill.objects.filter(billno__in=valid_bill_ids):
#                 total_amount += sale_bill.get_total_price()
#
#             final_sale.total_amount = total_amount
#             final_sale.save()
#
#             # Unlink the current SaleBill if its checkbox is unchecked
#             if current_billno not in valid_bill_ids:
#                 current_sale_bill.final_salebill = None
#                 current_sale_bill.save()
#
#         return JsonResponse({
#             "success": True,
#             "message": "Bills updated successfully."
#         })
#
#     return JsonResponse({"success": False, "message": "Invalid request."})
#
#


    # if request.method == "POST":
    #     import json
    #     data = json.loads(request.body)
    #     bill_ids = data.get("bill_ids", [])
    #
    #     # Get selected bills
    #     selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
    #
    #     # Aggregate stock and quantity
    #     stock_totals = {}
    #     total_quantity = 0
    #     for bill in selected_bills:
    #         for item in bill.get_items_list():
    #             if item.stock_id not in stock_totals:
    #                 stock_totals[item.stock_id] = {
    #                     "name": item.stock.name,
    #                     "quantity": 0,
    #                     "unit_price": item.perprice
    #                 }
    #             stock_totals[item.stock_id]["quantity"] += item.quantity
    #             total_quantity += item.quantity
    #
    #     # Create FinalSale and FinalSaleItems
    #     if selected_bills.exists():
    #         first_bill = selected_bills.first()
    #         final_sale = FinalSale.objects.create(
    #             customer=first_bill.Cust_id,
    #             total_amount=sum(item["quantity"] * item["unit_price"] for item in stock_totals.values())
    #         )
    #
    #         for stock_id, details in stock_totals.items():
    #             FinalSaleItem.objects.create(
    #                 final_bill=final_sale,
    #                 stock_id=stock_id,
    #                 total_quantity=details["quantity"],
    #                 unit_price=details["unit_price"],
    #                 total_price=details["quantity"] * details["unit_price"]
    #             )
    #
    #         # Prepare stock details for the response
    #         stock_details = [
    #             {"name": details["name"], "quantity": details["quantity"]}
    #             for details in stock_totals.values()
    #         ]
    #
    #         # Return the final bill details in the response
    #         return JsonResponse({
    #             "success": True,
    #             "final_bill": {
    #                 "billno": final_sale.billno,
    #                 "customer_name": final_sale.customer.Comp_name,
    #                 "total_quantity": total_quantity,
    #                 "total_amount": final_sale.total_amount,
    #                 "time": final_sale.time.strftime('%Y-%m-%d %H:%M:%S'),
    #                 "stock_details": stock_details
    #             }
    #         })
    # return JsonResponse({"success": False})

    # if request.method == "POST":
    #     import json
    #     data = json.loads(request.body)
    #     bill_ids = data.get("bill_ids", [])
    #
    #     # Get selected bills
    #     selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
    #
    #     # Aggregate stock and quantity
    #     stock_totals = {}
    #     for bill in selected_bills:
    #         for item in bill.get_items_list():
    #             if item.stock_id not in stock_totals:
    #                 stock_totals[item.stock_id] = {"quantity": 0, "unit_price": item.perprice}
    #             stock_totals[item.stock_id]["quantity"] += item.quantity
    #
    #     # Create FinalSale and FinalSaleItems
    #     if selected_bills.exists():
    #         first_bill = selected_bills.first()
    #         final_sale = FinalSale.objects.create(
    #             customer=first_bill.Cust_id,
    #             total_amount=sum(item["quantity"] * item["unit_price"] for item in stock_totals.values())
    #         )
    #
    #         for stock_id, details in stock_totals.items():
    #             FinalSaleItem.objects.create(
    #                 final_bill=final_sale,
    #                 stock_id=stock_id,
    #                 total_quantity=details["quantity"],
    #                 unit_price=details["unit_price"],
    #                 total_price=details["quantity"] * details["unit_price"]
    #             )
    #
    #         # Return the final bill details in the response
    #         return JsonResponse({
    #             "success": True,
    #             "final_bill": {
    #                 "billno": final_sale.billno,
    #                 "customer_name": final_sale.customer.Comp_name,
    #                 "total_amount": final_sale.total_amount,
    #                 "time": final_sale.time.strftime('%Y-%m-%d %H:%M:%S'),
    #             }
    #         })
    # return JsonResponse({"success": False})

    # if request.method == "POST":
    #     import json
    #     data = json.loads(request.body)
    #     bill_ids = data.get("bill_ids", [])
    #
    #     # Get selected bills
    #     selected_bills = SaleBill.objects.filter(billno__in=bill_ids)
    #
    #     # Aggregate stock and quantity
    #     stock_totals = {}
    #     for bill in selected_bills:
    #         for item in bill.get_items_list():
    #             if item.stock_id not in stock_totals:
    #                 stock_totals[item.stock_id] = {"quantity": 0, "unit_price": item.perprice}
    #             stock_totals[item.stock_id]["quantity"] += item.quantity
    #
    #     # Create FinalSale and FinalSaleItems
    #     if selected_bills.exists():
    #         first_bill = selected_bills.first()
    #         final_sale = FinalSale.objects.create(
    #             customer=first_bill.Cust_id,
    #             total_amount=sum(item["quantity"] * item["unit_price"] for item in stock_totals.values())
    #         )
    #
    #         for stock_id, details in stock_totals.items():
    #             FinalSaleItem.objects.create(
    #                 final_bill=final_sale,
    #                 stock_id=stock_id,
    #                 total_quantity=details["quantity"],
    #                 unit_price=details["unit_price"],
    #                 total_price=details["quantity"] * details["unit_price"]
    #             )
    #         return JsonResponse({"success": True, "final_bill_id": final_sale.billno})
    # return JsonResponse({"success": False})

    # import json
    # data = json.loads(request.POST.get('bills'))
    # selected_bills = SaleBill.objects.filter(billno__in=data)
    #
    # # Create Final Bill
    # final_bill = FinalSale.objects.create(
    #     name="Merged Bill",
    #     total_quantity=0,
    #     total_price=0
    # )
    # total_price = 0
    # total_quantity = 0
    #
    # for bill in selected_bills:
    #     items = bill.get_items_list()
    #     for item in items:
    #         final_bill.items.create(
    #             stock=item.stock,
    #             quantity=item.quantity,
    #             perprice=item.perprice,
    #             totalprice=item.totalprice,
    #         )
    #         total_price += item.totalprice
    #         total_quantity += item.quantity
    #
    # final_bill.total_price = total_price
    # final_bill.total_quantity = total_quantity
    # final_bill.save()
    #
    # return JsonResponse({'final_bill_id': final_bill.id})

#
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import SaleBill, SaleItem, SaleBillDetails
#
# def bill_merge_view(request):
#     if request.method == "GET":
#         # Fetch unique customers from SaleBill
#         customers = SaleBill.objects.values('Cust_id__Cust_id', 'Cust_id__Comp_name').distinct()
#         return render(request, "sales/return_sale.html", {'customers': customers})
#
#     if request.method == "POST":
#         # Handle merging bills
#         selected_bills = request.POST.getlist('billnos[]')  # Get selected bill numbers
#         final_sale_data = merge_bills(selected_bills)
#         return JsonResponse({'success': True, 'final_sale': final_sale_data})
#
# # def get_bills(request, customer_id):
# #     # Fetch bills related to the selected customer
# #     bills = SaleBill.objects.filter(Cust_id__id=customer_id).values('billno', 'time', 'name', 'phone')
# #     return JsonResponse(list(bills), safe=False)
#
# def get_bills(request, customer_id):
#     try:
#         # Filter bills by the given customer_id
#         bills = SaleBill.objects.filter(Cust_id=customer_id).values('billno', 'time')
#         return JsonResponse(list(bills), safe=False)
#     except SaleBill.DoesNotExist:
#         return JsonResponse({"error": "No bills found for the given customer."}, status=404)
#
# def merge_bills(selected_bills):
#     # Example function to merge bills
#     final_bill = {
#         'customer': None,
#         'items': [],
#         'total_price': 0
#     }
#
#     for bill_id in selected_bills:
#         bill = SaleBill.objects.get(billno=bill_id)
#         sale_items = SaleItem.objects.filter(billno=bill)
#
#         # Update the final bill with items and total price
#         if final_bill['customer'] is None:
#             final_bill['customer'] = bill.Cust_id.name
#
#         for item in sale_items:
#             final_bill['items'].append({
#                 'stock': item.stock.name,
#                 'quantity': item.quantity,
#                 'price': item.totalprice,
#             })
#             final_bill['total_price'] += item.totalprice
#
#     # Store the final bill in FinalSale (or similar model)
#     # Save logic goes here...
#
#     return final_bill

# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import SaleBill, SaleItem
#
# def bill_merge_view(request):
#     if request.method == "GET":
#         # Fetch unique customers from SaleBill
#         # customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()
#         customers = SaleBill.objects.values('Cust_id__Cust_id', 'Cust_id__Comp_name').distinct()
#         return render(request, "sales/return_sale.html", {'customers': customers})
#
#     if request.method == "POST":
#         # Handle merging bills
#         selected_bills = request.POST.getlist('billnos[]')  # Get selected bill numbers
#         final_sale_data = merge_bills(selected_bills)
#         return JsonResponse({'success': True, 'final_sale': final_sale_data})

#
# def get_bills(request, customer_id):
#     try:
#         # Filter bills by the given customer_id
#         bills = SaleBill.objects.filter(Cust_id=customer_id).values(
#             'billno', 'time', 'name', 'phone'
#         )
#         return JsonResponse(list(bills), safe=False)
#     except SaleBill.DoesNotExist:
#         return JsonResponse({"error": "No bills found for the given customer."}, status=404)
# from django.http import JsonResponse
#
#
# def get_bills(request, customerId):
#     print(customerId)
#     try:
#         # Filter SaleBill records by the given customer_id
#         bills = SaleBill.objects.filter(Cust_id_id__Cust_id_id=customerId).values(
#             'billno', 'time', 'Cust_id__Comp_name'
#         )
#
#         # If no bills are found, return an empty list
#         if not bills.exists():
#             return JsonResponse([], safe=False)
#
#         # Return the bills in JSON format
#         return JsonResponse(list(bills), safe=False)
#
#     except Exception as e:
#         # Return a 404 error with a message if there's an exception
#         return JsonResponse({"error": str(e)}, status=404)
#
#
# def merge_bills(selected_bills):
#     # Example function to merge bills
#     final_bill = {
#         'customer': None,
#         'items': [],
#         'total_price': 0
#     }
#
#     for bill_id in selected_bills:
#         bill = SaleBill.objects.get(billno=bill_id)
#         sale_items = SaleItem.objects.filter(billno=bill)
#
#         # Update the final bill with items and total price
#         if final_bill['customer'] is None:
#             final_bill['customer'] = bill.Cust_id.Comp_name
#
#         for item in sale_items:
#             final_bill['items'].append({
#                 'stock': item.stock.name,
#                 'quantity': item.quantity,
#                 'price': item.totalprice,
#             })
#             final_bill['total_price'] += item.totalprice
#
#     return final_bill
#



# def customer_bills(request):
#     customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()
#     bills = None
#
#     # If a customer is selected, get the related bills
#     if request.method == "POST" and request.POST.get("customer"):
#         customer_id = request.POST.get("customer")
#         customer = Customer.objects.get(id=customer_id)
#         bills = SaleBill.objects.filter(Cust_id=customer)
#
#     return render(request, 'sales/return_sale.html', {'customers': customers, 'bills': bills})
#
# def get_bills_for_customer(request, customer_id):
#     # Retrieve the customer object using the customer_id
#     customer = get_object_or_404(Customer, Cust_id=customer_id)
#
#     # Retrieve all SaleBills for this customer
#     bills = SaleBill.objects.filter(Cust_id=customer)
#
#     # bills = SaleBill.objects.filter(Cust_id=customer_id)
#     bill_data = []
#     for bill in bills:
#         bill_data.append({
#             'billno': bill.billno,
#             'totalprice': bill.get_total_price(),
#             'final_amount': bill.get_final_amount()
#         })
#     return JsonResponse({'bills': bill_data})
#
# def generate_final_bill(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         bills = data['bills']
#
#         # Logic to generate a new final bill
#         # Merge all selected bills, and store them in final_sale table
#
#         try:
#             final_bill = SaleBill.objects.create(
#                 # Cust_id=customer,  # Set customer, other required fields
#                 name='Final Bill',  # Set any default values
#                 phone='',
#                 address='',
#                 email='',
#                 gstin='',
#             )
#
#             # Assuming you have logic to create the final bill details and stock updates
#             for bill in bills:
#                 # Create a new record for the final bill
#                 # You may need to adjust this based on your models
#                 SaleBillDetails.objects.create(
#                     billno=final_bill,
#                     total=bill['totalprice'],
#                     final_amount=bill['final_amount'],
#                     # other fields...
#                 )
#
#             return JsonResponse({'success': True})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#


#
#
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import SaleBill, Customer
#
# def sale_bill_management(request):
#     # customers = Customer.objects.all()  # Fetch all customers
#     customers = SaleBill.objects.values('Cust_id', 'Cust_id__Comp_name').distinct()
#
#     return render(request, 'sales/return_sale.html', {'customers': customers})
#
# def get_customer_bills(request):
#     customer_id = request.GET.get('customer_id')
#     print(customer_id)
#     if customer_id:
#         # Get SaleBill records for the selected customer
#         bills = SaleBill.objects.filter(Cust_id=customer_id).select_related('Cust_id')
#         response_data = []
#         for bill in bills:
#             response_data.append({
#                 'billno': bill.billno,
#
#                 'time': bill.time.strftime('%Y-%m-%d %H:%M:%S'),
#             })
#         return JsonResponse({'bills': response_data}, status=200)
#     else:
#         return JsonResponse({'error': 'Customer ID not provided.'}, status=400)


#
# from django.http import JsonResponse
# from .models import SaleBill
#
# def get_bills(request):
#     cust_id = request.GET.get('Cust_id')
#     bills = SaleBill.objects.filter(Cust_id=cust_id).values('billno', 'time')
#     return JsonResponse({'bills': list(bills)})
#
#
# from django.shortcuts import render
# from .models import SaleBill, SaleItem, SaleBillDetails
#
# def generate_final_bill(request):
#     if request.method == 'POST':
#         bill_ids = request.POST.getlist('bills[]')
#         final_bill = SaleBill.objects.create(
#             Cust_id=request.user.customer,
#             name="Merged Bill",
#             phone="N/A",
#             address="N/A",
#             email="N/A",
#             gstin="N/A",
#         )
#         for bill_id in bill_ids:
#             sale_items = SaleItem.objects.filter(billno_id=bill_id)
#             for item in sale_items:
#                 SaleItem.objects.create(
#                     billno=final_bill,
#                     stock=item.stock,
#                     quantity=item.quantity,
#                     perprice=item.perprice,
#                     totalprice=item.totalprice,
#                 )
#         return JsonResponse({'success': True})



from .forms import SerialSearchForm
#
# def search_serial(request):
#     results = None
#     if request.method == 'GET':
#         form = SerialSearchForm(request.GET)
#         if form.is_valid():
#             serial_no = form.cleaned_data['serial_no']
#             results = PurchaseSerial.objects.filter(serialNo__iexact=serial_no)  # Exact match ignoring case
#     else:
#         form = SerialSearchForm()
#
#     return render(request, 'purchases/search_serial.html', {'form': form, 'results': results})
from django.shortcuts import render
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.formats import date_format
from .models import PurchaseSerial, PurchaseBillDetails, SaleBillDetails, ReturnBillDetails
from .forms import SerialSearchForm

# Indian display: dd/mm/yyyy (slashes)
_SEARCH_SERIAL_DATE_FMT = "d/m/Y"


def _search_serial_format_indian(val):
    """
    Show dates as dd/mm/yyyy. Accepts date, datetime, or common string forms (e.g. YYYY-MM-DD).
    Unparseable strings are returned as-is (stripped).
    """
    if val is None or val == "":
        return ""
    if hasattr(val, "strftime") and not isinstance(val, str):
        try:
            return date_format(val, _SEARCH_SERIAL_DATE_FMT)
        except (TypeError, ValueError, AttributeError):
            return str(val)[:19]
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return ""
        parsed = parse_datetime(s)
        if parsed is not None:
            return date_format(parsed, _SEARCH_SERIAL_DATE_FMT)
        d = parse_date(s)
        if d is not None:
            return date_format(d, _SEARCH_SERIAL_DATE_FMT)
        return s
    try:
        return date_format(val, _SEARCH_SERIAL_DATE_FMT)
    except (TypeError, ValueError, AttributeError):
        return str(val)[:19]


def _search_serial_purchase_date_str(details, bill):
    """
    Purchase form stores bill_date in PurchaseBillDetails.tcs (see PurchaseCreateView).
    Fallback: PurchaseBill.time; then cgst (some legacy saves used different fields).
    """
    if details:
        tcs = (details.tcs or "").strip()
        if tcs:
            out = _search_serial_format_indian(tcs)
            return out if out else "N/A"
    if bill is not None:
        bt = getattr(bill, "time", None)
        if bt:
            out = _search_serial_format_indian(bt)
            return out if out else "N/A"
    if details:
        cgst = (details.cgst or "").strip()
        if cgst:
            out = _search_serial_format_indian(cgst)
            return out if out else "N/A"
    return "N/A"


def _search_serial_dt_str(dt):
    if dt is None or dt == "":
        return "N/A"
    out = _search_serial_format_indian(dt)
    return out if out else "N/A"


def search_serial(request):
    results = None
    if request.method == 'GET':
        form = SerialSearchForm(request.GET)
        if form.is_valid():
            serial_no = form.cleaned_data["serial_no"]
            results = (
                PurchaseSerial.objects.filter(serialNo__iexact=serial_no)
                .select_related(
                    "billno",
                    "billno__supplier",
                    "stock",
                    "sales_billno",
                    "final_salebill",
                    "return_bill",
                )
            )
            for r in results:
                r.purchase_bill_details = (
                    PurchaseBillDetails.objects.filter(billno=r.billno).order_by("id").first()
                )

                if r.sales_billno:
                    r.sale_bill_details = (
                        SaleBillDetails.objects.filter(billno=r.sales_billno)
                        .order_by("id")
                        .first()
                    )
                else:
                    r.sale_bill_details = None

                if r.return_bill:
                    r.return_sale_bill_details = (
                        ReturnBillDetails.objects.filter(billno=r.return_bill)
                        .order_by("id")
                        .first()
                    )
                else:
                    r.return_sale_bill_details = None

                r.purchase_date_display = _search_serial_purchase_date_str(
                    r.purchase_bill_details, r.billno
                )
                if r.sales_billno:
                    st = r.sales_billno.time
                    if not st and r.sale_bill_details:
                        raw = (
                            (getattr(r.sale_bill_details, "tcs", None) or "")
                            or (getattr(r.sale_bill_details, "cgst", None) or "")
                        ).strip()
                        r.sale_date_display = (
                            _search_serial_format_indian(raw) if raw else "N/A"
                        ) or "N/A"
                    else:
                        r.sale_date_display = _search_serial_dt_str(st)
                else:
                    r.sale_date_display = "N/A"
                if r.return_bill:
                    rt = r.return_bill.time
                    if not rt and r.return_sale_bill_details:
                        raw = (
                            (getattr(r.return_sale_bill_details, "tcs", None) or "")
                            or (getattr(r.return_sale_bill_details, "cgst", None) or "")
                        ).strip()
                        r.return_date_display = (
                            _search_serial_format_indian(raw) if raw else "N/A"
                        ) or "N/A"
                    else:
                        r.return_date_display = _search_serial_dt_str(rt)
                else:
                    r.return_date_display = "N/A"
                if r.final_salebill:
                    ft = r.final_salebill.time
                    r.final_sale_date_display = _search_serial_dt_str(ft)
                else:
                    r.final_sale_date_display = "N/A"

    else:
        form = SerialSearchForm()

    return render(request, "purchases/search_serial.html", {"form": form, "results": results})
