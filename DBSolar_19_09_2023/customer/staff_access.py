"""
Staff-scoped Customer querysets: Associates see Assoc_Assign; engineers see Engg_Assign.
"""
from .models import Customer


def is_associate_staff(user):
    if not getattr(user, "is_authenticated", False) or not user.is_staff:
        return False
    prof = getattr(user, "profile", None)
    return bool(prof and getattr(prof, "department", None) == "Associate")


def associate_consumer_user_ids(user):
    """
    Auth User ids for consumer logins (Customer.new_customer) tied to this associate
    via Assoc_Assign. Used to scope complaints (Firereport.Account_id).
    """
    if not getattr(user, "is_authenticated", False):
        return []
    return list(
        Customer.objects.filter(Assoc_Assign_id=user.id)
        .exclude(new_customer_id__isnull=True)
        .values_list("new_customer_id", flat=True)
    )


def associate_users_for_quotation_dropdown(user):
    """
    Users eligible for "Assign Associate" on quotations: staff with Associate department.
    Associates (non-superuser) only see themselves in the dropdown.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    qs = (
        User.objects.filter(is_staff=True, profile__department="Associate")
        .order_by("first_name", "last_name", "username")
    )
    if (
        getattr(user, "is_authenticated", False)
        and user.is_staff
        and is_associate_staff(user)
        and not user.is_superuser
    ):
        qs = qs.filter(pk=user.pk)
    return qs


def quotation_queryset_for_request(user):
    """
    Quotation list/detail/PDF access.
    - Superuser (staff): all quotations
    - Associate (staff): only quotations assigned to that user (assigned_associate)
    - Other staff: all quotations
    - Anonymous: all quotations (same as legacy list behaviour)
    """
    from quotation.models import Quotation

    if not getattr(user, "is_authenticated", False):
        return Quotation.objects.all()
    if user.is_superuser and user.is_staff:
        return Quotation.objects.all()
    if user.is_staff and is_associate_staff(user):
        return Quotation.objects.filter(assigned_associate_id=user.id)
    if user.is_staff:
        return Quotation.objects.all()
    return Quotation.objects.all()


def customer_queryset_for_request(user):
    """
    Base Customer queryset for list / dashboard / PDF views.
    - Superuser (staff): all customers
    - Associate (staff): only customers where Assoc_Assign == user
    - Other staff: only customers where Engg_Assign == user
    - Non-staff: all customers (legacy behaviour for shared templates)
    """
    if not user.is_authenticated:
        return Customer.objects.none()
    if user.is_superuser and user.is_staff:
        return Customer.objects.all()
    if user.is_staff:
        if is_associate_staff(user):
            return Customer.objects.filter(Assoc_Assign_id=user.id)
        return Customer.objects.filter(Engg_Assign_id=user.id)
    return Customer.objects.all()


def associate_assigned_customer_pk_list(user):
    """
    Customer primary keys (Cust_id) the associate may access (inventory/transactions scoping).
    Empty list if user is not an associate. Superuser associates get all customer pks (same as queryset).
    """
    if not getattr(user, "is_authenticated", False) or not is_associate_staff(user):
        return []
    if getattr(user, "is_superuser", False):
        return list(Customer.objects.values_list("pk", flat=True))
    return list(
        Customer.objects.filter(Assoc_Assign_id=user.id).values_list("pk", flat=True)
    )


def associate_assert_customer_pk_allowed(user, customer_pk):
    """
    Raise PermissionDenied if an associate (non-superuser) accesses a customer outside their list.
    No-op for non-associates and for superusers.
    """
    from django.core.exceptions import PermissionDenied

    if not getattr(user, "is_authenticated", False) or not is_associate_staff(user):
        return
    if getattr(user, "is_superuser", False):
        return
    try:
        pk = int(customer_pk)
    except (TypeError, ValueError):
        raise PermissionDenied("Invalid customer.") from None
    allowed = associate_assigned_customer_pk_list(user)
    if pk not in allowed:
        raise PermissionDenied("You may only access customers assigned to you.")


def associate_forbid_transactions_write(user):
    """
    True if sale/purchase (etc.) create/update should be blocked for this user.
    Associates are read-only for transactions unless superuser.
    """
    return bool(
        getattr(user, "is_authenticated", False)
        and is_associate_staff(user)
        and not getattr(user, "is_superuser", False)
    )
