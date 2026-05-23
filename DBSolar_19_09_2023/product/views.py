from django.http import JsonResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Category, SubCategory, Product, Brand, Unit, Supplier
from .forms import CategoryForm, SubCategoryForm, ProductForm, BrandForm, UnitForm, SupplierForm
from .category_maintenance import merge_duplicate_product_categories
from inventory.models import Stock
from transactions.models import PurchaseItem, SaleItem, FinalSaleItem, ReturnSaleItem, PurchaseSerial
from django.db import transaction
from django.db.utils import IntegrityError
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


def _unique_stock_name(base: str, product_pk: int) -> str:
    """Stock.name is globally unique; pick a free name tied to product id."""
    base = (base or f"Product-{product_pk}")[:100]
    candidate = base
    n = 0
    while Stock.objects.filter(name=candidate).exists():
        n += 1
        suffix = f"-{product_pk}" if n == 1 else f"-{product_pk}-{n}"
        candidate = (base[: max(1, 100 - len(suffix))] + suffix)[:100]
    return candidate


def add_category(request):
    # Clean legacy duplicate categories so ModelChoiceField / FK resolution cannot break.
    try:
        merge_duplicate_product_categories()
    except Exception:
        logger.exception("merge_duplicate_product_categories failed")

    if request.method == "POST":
        # Handle Category Actions
        if 'add_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                try:
                    category_form.save()
                    messages.success(request, 'Category added successfully.')
                except IntegrityError:
                    messages.error(
                        request,
                        'Could not add category: that name or short code is already used.',
                    )
            else:
                err_text = ' '.join(
                    f"{f}: {', '.join(e)}" for f, e in category_form.errors.items()
                )
                messages.error(
                    request,
                    err_text or 'Failed to add category. Check all fields.',
                )
        elif 'edit_category' in request.POST:
            category_id = request.POST.get('category_id')
            if category_id:
                category = get_object_or_404(Category, id=category_id)
                category_form = CategoryForm(request.POST, instance=category)
                if category_form.is_valid():
                    try:
                        category_form.save()
                        messages.success(request, 'Category Updated successfully.')
                    except IntegrityError:
                        messages.error(
                            request,
                            'Could not update: that name or short code is already used.',
                        )
                else:
                    err_text = ' '.join(
                        f"{f}: {', '.join(e)}"
                        for f, e in category_form.errors.items()
                    )
                    messages.error(
                        request,
                        err_text or 'Failed to Update Category.',
                    )


        # Handle SubCategory Actions
        elif 'add_subcategory' in request.POST:
            subcategory_form = SubCategoryForm(request.POST)
            if subcategory_form.is_valid():
                subcategory_form.save()
                messages.success(request, 'SubCategory added successfully.')
            else:
                messages.error(request, 'Failed to add SubCategory.')


        elif 'add_product' in request.POST:

            def _clean_pk(val):
                if val in (None, ""):
                    return None
                try:
                    return int(val)
                except (TypeError, ValueError):
                    return None

            category_id = _clean_pk(request.POST.get("category"))
            subcategory_id = _clean_pk(request.POST.get("subcategory"))
            purchase_id = _clean_pk(request.POST.get("purchase_unit"))
            sales_id = _clean_pk(request.POST.get("sales_unit"))
            name = (request.POST.get("name") or "").strip()
            prod_description = (request.POST.get("prod_description") or "").strip()
            try:
                stock_alert = int(request.POST.get("stock_alert") or 0)
            except (TypeError, ValueError):
                stock_alert = 0
            try:
                gst = Decimal(str(request.POST.get("gst") or "0"))
            except (InvalidOperation, TypeError, ValueError):
                gst = Decimal("0")
            status = request.POST.get("status") == "on"

            if not name:
                messages.error(request, "Product name is required.")
            elif not all([category_id, subcategory_id, purchase_id, sales_id]):
                messages.error(
                    request,
                    "Please select category, subcategory, purchase unit, and sales unit.",
                )
            elif Product.objects.filter(name=name).exists():
                messages.error(request, "A product with this name already exists.")
            else:
                try:
                    with transaction.atomic():
                        product = Product.objects.create(
                            category_id=category_id,
                            subcategory_id=subcategory_id,
                            purchase_id=purchase_id,
                            sales_id=sales_id,
                            name=name,
                            prod_description=prod_description or None,
                            stock_alert=stock_alert,
                            gst=gst,
                            status=status,
                        )
                        stock_name = _unique_stock_name(name, product.id)
                        Stock.objects.create(
                            category_id=category_id,
                            subcategory_id=subcategory_id,
                            purchase_id=purchase_id,
                            sales_id=sales_id,
                            product_id=product.id,
                            name=stock_name,
                            quantity=Decimal("0"),
                            stock_alert=stock_alert,
                            gst=gst,
                            status=status,
                        )
                    messages.success(
                        request,
                        "Product and stock record added successfully.",
                    )
                except IntegrityError:
                    logger.exception("add_product IntegrityError")
                    messages.error(
                        request,
                        "Could not add product (database conflict). Try a different name or contact support.",
                    )


        # Handle Brand Actions
        elif 'add_brand' in request.POST:
            brand_form = BrandForm(request.POST)
            if brand_form.is_valid():
                brand_form.save()
                messages.success(request, 'Brand added successfully.')
            else:
                messages.error(request, 'Failed to add Brand.')

        elif 'edit_brand' in request.POST:
            brand_id = request.POST.get('brand_id')
            if brand_id:
                brand = get_object_or_404(Brand, id=brand_id)
                brand_form = BrandForm(request.POST, instance=brand)
                if brand_form.is_valid():
                    brand_form.save()
                    messages.success(request, 'Brand Updated successfully.')
                else:
                    messages.error(request, 'Failed to Update Brand.')


        # Handle Unit Actions
        elif 'add_unit' in request.POST:
            unit_form = UnitForm(request.POST)
            if unit_form.is_valid():
                unit_form.save()
                messages.success(request, 'Unit added successfully.')
            else:
                messages.error(request, 'Failed to add Unit.')

        elif 'edit_unit' in request.POST:
            unit_id = request.POST.get('unit_id')
            if unit_id:
                unit = get_object_or_404(Unit, id=unit_id)
                unit_form = UnitForm(request.POST, instance=unit)
                if unit_form.is_valid():
                    unit_form.save()
                    messages.success(request, 'Unit Updated successfully.')
                else:
                    messages.error(request, 'Failed to Update Unit.')

        # Handle Supplier Actions
        elif 'add_supplier' in request.POST:
            supplier_form = SupplierForm(request.POST)
            if supplier_form.is_valid():
                supplier_form.save()
                messages.success(request, 'Supplier added successfully.')
            else:
                messages.error(request, 'Failed to add Supplier.')

    # Initial form instances for modals
    category_form = CategoryForm()
    subcategory_form = SubCategoryForm()
    product_form = ProductForm()
    brand_form = BrandForm()
    unit_form = UnitForm()
    supplier_form = SupplierForm()

    # Fetch data for lists (newest / highest id first — Sr No 1 = latest row)
    categories = Category.objects.all().order_by("-id")
    subcategories = SubCategory.objects.all().order_by("-id")
    products = Product.objects.all().order_by("-id")
    brands = Brand.objects.all().order_by("-id")
    units = Unit.objects.all().order_by("-id")
    suppliers = Supplier.objects.all().order_by("-id")

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
        'brands': brands,
        'units': units,
        'suppliers': suppliers,
        'category_form': category_form,
        'subcategory_form': subcategory_form,
        'product_form': product_form,
        'brand_form': brand_form,
        'unit_form': unit_form,
        'supplier_form': supplier_form,
    }
    return render(request, 'product/add_category.html', context)

def get_category(request, id):
    category = get_object_or_404(Category, id=id)
    return JsonResponse({'name': category.name, 'short_name': category.short_name, 'status': category.status})



def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})

#
# Edit Category
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category Updated successfully.')
            return redirect('product_add_category')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'product/add_category.html', {'form': form})


def get_subcategory(request, id):
    # subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    subcategory = SubCategory.objects.get(id=id)
    data = {
        # 'category_id': subcategory.category.name,
        'category_id': subcategory.category_id,  # This is crucial
        'name': subcategory.name,
        'short_name': subcategory.short_name,
        'status': subcategory.status,  # Boolean value
        'id': subcategory.id,  # Boolean value
    }
    return JsonResponse(data)


def update_subcategory(request):
    if request.method == 'POST':
        subcategory_id = request.POST.get('id')
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)

        # Update the fields with the data from the form
        subcategory.category_id = request.POST.get('category_id')
        subcategory.name = request.POST.get('name')
        subcategory.short_name = request.POST.get('short_name')
        subcategory.status = request.POST.get('status') == 'on'

        # Save the updated object to the database
        subcategory.save()

        messages.success(request, 'SubCategory Updated successfully.')
        # Redirect back to the appropriate page after saving
        return redirect('product_add_category') # Replace with your URL name


def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        data = {
            'id': product.id,
            'category_id': product.category_id,
            'subcategory_id': product.subcategory_id,
            'name': product.name,
            'prod_description': product.prod_description,
            'stock_alert': product.stock_alert,
            'gst': product.gst,
            'purchase_id': product.purchase_id,
            'sales_id': product.sales_id,
            'status': product.status,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)



def update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        product = get_object_or_404(Product, id=product_id)

        # Update the fields with the data from the form
        product.category_id = request.POST.get('category_id')
        product.subcategory_id = request.POST.get('subcategory_id')
        product.purchase_id = request.POST.get('purchase_id')
        product.sales_id = request.POST.get('sales_id')
        product.name = request.POST.get('name')
        product.prod_description = request.POST.get('prod_description')
        product.stock_alert = request.POST.get('stock_alert')
        product.gst = request.POST.get('gst')
        product.status = request.POST.get('status') == 'on'

        # Save the updated object to the database
        product.save()

        # Sync inventory row — legacy products may have no Stock (avoid 404)
        stock = Stock.objects.filter(product_id=product.id).order_by("id").first()
        if stock is None:
            stock = Stock(
                category_id=product.category_id,
                subcategory_id=product.subcategory_id,
                purchase_id=product.purchase_id,
                sales_id=product.sales_id,
                product_id=product.id,
                name=_unique_stock_name(product.name, product.id),
                quantity=Decimal("0"),
                stock_alert=product.stock_alert,
                gst=product.gst,
                status=product.status,
            )
            stock.save()
        else:
            stock.category_id = product.category_id
            stock.subcategory_id = product.subcategory_id
            stock.purchase_id = product.purchase_id
            stock.sales_id = product.sales_id
            desired = (product.name or f"Product-{product.id}")[:100]
            if Stock.objects.filter(name=desired).exclude(pk=stock.pk).exists():
                stock.name = _unique_stock_name(product.name, product.id)
            else:
                stock.name = desired
            stock.stock_alert = product.stock_alert
            stock.gst = product.gst
            stock.status = product.status
            stock.save()

        messages.success(request, "Product updated successfully.")
        return redirect("product_add_category")


def get_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    data = {
        'name': brand.name,
        'status': brand.status,  # Boolean value
    }
    return JsonResponse(data)

def get_unit(request, id):
    unit = get_object_or_404(Unit, id=id)
    data = {
        'name': unit.name,
        'short_name': unit.short_name,
    }
    return JsonResponse(data)

def get_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    data = {
        'category_id': supplier.category_id,  # This is crucial
        'supplier_name': supplier.supplier_name,
        'contact_person': supplier.contact_person,
        'contact_email': supplier.contact_email,
        'contact_phone': supplier.contact_phone,
        'address': supplier.address,
        'city': supplier.city,
        'state': supplier.state,
        'post_code': supplier.post_code,
        'gst_no': supplier.gst_no,
        'status': supplier.status,
    }
    return JsonResponse(data)


def update_supplier(request):
    if request.method == 'POST':
        supplier1_id = request.POST.get('id')
        supplier = get_object_or_404(Supplier, id=supplier1_id)

        # Update the fields with the data from the form
        supplier.supplier_name = request.POST.get('supplier_name')
        supplier.contact_person = request.POST.get('contact_person')
        supplier.contact_email = request.POST.get('contact_email')
        supplier.contact_phone = request.POST.get('contact_phone')
        supplier.address = request.POST.get('address')
        supplier.city = request.POST.get('city')
        supplier.state = request.POST.get('state')
        supplier.post_code = request.POST.get('post_code')
        supplier.gst_no = request.POST.get('gst_no')
        supplier.category_id = request.POST.get('category_id')
        supplier.status = request.POST.get('status') == 'on'

        # Save the updated object to the database
        supplier.save()
        messages.success(request, 'Supplier Updated successfully.')

        # Redirect back to the appropriate page after saving
        return redirect('product_add_category') # Replace with your URL name



# Delete Category
def delete_category(request, id):
    category = Category.objects.filter(id=id).order_by("id").first()
    if not category:
        messages.error(request, "Category not found.")
        return redirect('product_add_category')
    usage_error = _build_entity_usage_error("category", category)
    if usage_error:
        messages.error(request, usage_error)
        return redirect('product_add_category')
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('product_add_category')

# Delete Category
def delete_subcategory(request, id):
    subcategory = SubCategory.objects.filter(id=id).order_by("id").first()
    if not subcategory:
        messages.error(request, "SubCategory not found.")
        return redirect('product_add_category')
    usage_error = _build_entity_usage_error("subcategory", subcategory)
    if usage_error:
        messages.error(request, usage_error)
        return redirect('product_add_category')
    subcategory.delete()
    messages.success(request, 'SubCategory deleted successfully.')
    return redirect('product_add_category')



# Delete Product
def delete_product(request, id):
    product = Product.objects.filter(id=id).order_by("id").first()
    if not product:
        messages.error(request, "Product not found.")
        return redirect('product_add_category')
    usage_error = _build_entity_usage_error("product", product)
    if usage_error:
        messages.error(request, usage_error)
        return redirect('product_add_category')
    stock = Stock.objects.filter(product_id=product.id).first()
    if stock:
        stock.delete()
    product.delete()
    messages.success(request, 'Product and related Stock deleted successfully.')
    return redirect('product_add_category')  # Replace with your actual URL name

# Delete Brand
def delete_brand(request, id):
    brand = Brand.objects.filter(id=id).order_by("id").first()
    if not brand:
        messages.error(request, "Brand not found.")
        return redirect('product_add_category')
    usage_error = _build_entity_usage_error("brand", brand)
    if usage_error:
        messages.error(request, usage_error)
        return redirect('product_add_category')
    brand.delete()
    messages.success(request, 'Brand deleted successfully.')
    return redirect('product_add_category')

# Delete Unit
def delete_unit(request, id):
    unit = Unit.objects.filter(id=id).order_by("id").first()
    if not unit:
        messages.error(request, "Unit not found.")
        return redirect('product_add_category')
    usage_error = _build_entity_usage_error("unit", unit)
    if usage_error:
        messages.error(request, usage_error)
        return redirect('product_add_category')
    unit.delete()
    messages.success(request, 'Unit deleted successfully.')
    return redirect('product_add_category')

# Delete Supplier
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully.')
    return redirect('product_add_category')


def precheck_delete_usage(request, entity, id):
    entity_map = {
        "category": Category,
        "subcategory": SubCategory,
        "product": Product,
        "brand": Brand,
        "unit": Unit,
    }
    model_cls = entity_map.get((entity or "").lower())
    if model_cls is None:
        return JsonResponse({"blocked": True, "message": "Invalid delete pre-check request."}, status=400)

    obj = model_cls.objects.filter(id=id).order_by("id").first()
    if not obj:
        return JsonResponse({"blocked": True, "message": "Record not found."}, status=404)

    error_message = _build_entity_usage_error((entity or "").lower(), obj)
    return JsonResponse({"blocked": bool(error_message), "message": error_message or ""})


def _bill_refs_for_stocks(stock_qs):
    stock_ids = list(stock_qs.values_list("id", flat=True))
    if not stock_ids:
        return {"purchase": [], "sale": [], "final_sale": [], "return": []}

    purchase_refs = list(
        PurchaseItem.objects.filter(stock_id__in=stock_ids)
        .values_list("billno__billno", flat=True)
        .distinct()
    )
    sale_refs = list(
        SaleItem.objects.filter(stock_id__in=stock_ids)
        .values_list("billno__billno", flat=True)
        .distinct()
    )
    final_sale_refs = list(
        FinalSaleItem.objects.filter(stock_id__in=stock_ids)
        .values_list("final_bill__billno", flat=True)
        .distinct()
    )
    return_refs = list(
        ReturnSaleItem.objects.filter(stock_id__in=stock_ids)
        .values_list("return_bill__billno", flat=True)
        .distinct()
    )

    # Include serial-based links too, as these also represent bill usage.
    purchase_refs.extend(
        list(
            PurchaseSerial.objects.filter(stock_id__in=stock_ids)
            .values_list("billno__billno", flat=True)
            .distinct()
        )
    )
    sale_refs.extend(
        list(
            PurchaseSerial.objects.filter(stock_id__in=stock_ids, sales_billno__isnull=False)
            .values_list("sales_billno__billno", flat=True)
            .distinct()
        )
    )
    final_sale_refs.extend(
        list(
            PurchaseSerial.objects.filter(stock_id__in=stock_ids, final_salebill__isnull=False)
            .values_list("final_salebill__billno", flat=True)
            .distinct()
        )
    )
    return_refs.extend(
        list(
            PurchaseSerial.objects.filter(stock_id__in=stock_ids, return_bill__isnull=False)
            .values_list("return_bill__billno", flat=True)
            .distinct()
        )
    )

    return {
        "purchase": [str(x) for x in dict.fromkeys([x for x in purchase_refs if x is not None])],
        "sale": [str(x) for x in dict.fromkeys([x for x in sale_refs if x is not None])],
        "final_sale": [str(x) for x in dict.fromkeys([x for x in final_sale_refs if x is not None])],
        "return": [str(x) for x in dict.fromkeys([x for x in return_refs if x is not None])],
    }


def _build_entity_usage_error(entity_type, entity_obj):
    """
    Return user-facing error string when an entity is used in bills, else empty string.
    """
    if entity_type == "category":
        stock_qs = Stock.objects.filter(category_id=entity_obj.id)
        title = f'Category "{entity_obj.name}"'
        linked_subcategory_ids = list(
            SubCategory.objects.filter(category_id=entity_obj.id)
            .values_list("id", flat=True)
            .distinct()
        )
        linked_product_ids = list(
            Product.objects.filter(category_id=entity_obj.id)
            .values_list("id", flat=True)
            .distinct()
        )
    elif entity_type == "subcategory":
        stock_qs = Stock.objects.filter(subcategory_id=entity_obj.id)
        title = f'SubCategory "{entity_obj.name}"'
        linked_product_ids = list(
            Product.objects.filter(subcategory_id=entity_obj.id)
            .values_list("id", flat=True)
            .distinct()
        )
    elif entity_type == "product":
        stock_qs = Stock.objects.filter(product_id=entity_obj.id)
        title = f'Product "{entity_obj.name}"'
    elif entity_type == "unit":
        stock_qs = Stock.objects.filter(purchase_id=entity_obj.id) | Stock.objects.filter(sales_id=entity_obj.id)
        title = f'Unit "{entity_obj.name}"'
        linked_product_ids = list(
            Product.objects.filter(purchase_id=entity_obj.id)
            .values_list("id", flat=True)
            .distinct()
        )
        linked_product_ids.extend(
            list(
                Product.objects.filter(sales_id=entity_obj.id)
                .values_list("id", flat=True)
                .distinct()
            )
        )
        linked_product_ids = list(dict.fromkeys(linked_product_ids))
    elif entity_type == "brand":
        # Brand is currently not linked in transaction bill models.
        return ""
    else:
        return ""

    refs = _bill_refs_for_stocks(stock_qs.distinct())

    # Extra direct unit usage in transaction rows (not only via stock table).
    if entity_type == "unit":
        refs["purchase"].extend(
            [
                str(x)
                for x in PurchaseItem.objects.filter(purchase_id=entity_obj.id)
                .values_list("billno__billno", flat=True)
                .distinct()
                if x is not None
            ]
        )
        refs["sale"].extend(
            [
                str(x)
                for x in SaleItem.objects.filter(sale_id=entity_obj.id)
                .values_list("billno__billno", flat=True)
                .distinct()
                if x is not None
            ]
        )
        refs["purchase"] = list(dict.fromkeys(refs["purchase"]))
        refs["sale"] = list(dict.fromkeys(refs["sale"]))

    has_master_dependency = False
    if entity_type == "category":
        has_master_dependency = bool(linked_subcategory_ids or linked_product_ids)
    elif entity_type == "subcategory":
        has_master_dependency = bool(linked_product_ids)
    elif entity_type == "unit":
        has_master_dependency = bool(linked_product_ids)

    if not any(refs.values()) and not has_master_dependency:
        return ""

    lines = [f"Cannot delete {title}."]
    if any(refs.values()):
        lines.append("This record is already used in bills:")
    if has_master_dependency:
        lines.append("This record is also used in master data:")
    if refs["purchase"]:
        lines.append(f"Purchase Bills: {', '.join(refs['purchase'])}")
    if refs["sale"]:
        lines.append(f"Sale Bills: {', '.join(refs['sale'])}")
    if refs["final_sale"]:
        lines.append(f"Final Sale Bills: {', '.join(refs['final_sale'])}")
    if refs["return"]:
        lines.append(f"Return Bills: {', '.join(refs['return'])}")

    # Extra master-data dependency validations (as requested).
    if entity_type == "category":
        if linked_subcategory_ids:
            lines.append(
                f"Linked SubCategories: {', '.join(str(x) for x in linked_subcategory_ids)}"
            )
        if linked_product_ids:
            lines.append(
                f"Linked Products: {', '.join(str(x) for x in linked_product_ids)}"
            )
    elif entity_type == "subcategory":
        if linked_product_ids:
            lines.append(
                f"Linked Products: {', '.join(str(x) for x in linked_product_ids)}"
            )
    elif entity_type == "unit":
        if linked_product_ids:
            lines.append(
                f"Linked Products: {', '.join(str(x) for x in linked_product_ids)}"
            )

    return "\n".join(lines)




