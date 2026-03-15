from audioop import reverse
from datetime import timezone
from itertools import product

from django.http import JsonResponse
import itertools

# or to avoid confusion
from itertools import product as itertools_product

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Category, SubCategory, Product, Brand, Unit, Supplier
from .forms import CategoryForm, SubCategoryForm, ProductForm, BrandForm, UnitForm, SupplierForm
from inventory.models import Stock
from django.db.utils import IntegrityError

def add_category(request):
    if request.method == "POST":
        # Handle Category Actions
        if 'add_category' in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Category added successfully.')
            else:
                messages.error(request, 'Failed to add category.')
        elif 'edit_category' in request.POST:
            category_id = request.POST.get('category_id')
            if category_id:
                category = get_object_or_404(Category, id=category_id)
                category_form = CategoryForm(request.POST, instance=category)
                if category_form.is_valid():
                    category_form.save()
                    messages.success(request, 'Category Updated successfully.')
                else:
                    messages.error(request, 'Failed to Update Category.')


        # Handle SubCategory Actions
        elif 'add_subcategory' in request.POST:
            subcategory_form = SubCategoryForm(request.POST)
            if subcategory_form.is_valid():
                subcategory_form.save()
                messages.success(request, 'SubCategory added successfully.')
            else:
                messages.error(request, 'Failed to add SubCategory.')


        elif 'add_product' in request.POST:
            category_id = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')
            purchase_id = request.POST.get('purchase_unit')
            sales_id = request.POST.get('sales_unit')
            name = request.POST.get('name')
            prod_description = request.POST.get('prod_description')
            stock_alert = request.POST.get('stock_alert')
            gst = request.POST.get('gst')
            status = request.POST.get('status') == 'on'

            # Check if a product with the same name already exists
            if Product.objects.filter(name=name).exists():
                messages.error(request, 'A product name already exists.')
            else:
                try:
                    # Create the product first
                    product = Product.objects.create(
                        category_id=category_id,
                        subcategory_id=subcategory_id,
                        purchase_id=purchase_id,
                        sales_id=sales_id,
                        name=name,
                        prod_description=prod_description,
                        stock_alert=stock_alert,
                        gst=gst,
                        status=status
                    )

                    # Now create or update the stock related to the product
                    Stock.objects.create(
                        category_id=category_id,
                        subcategory_id=subcategory_id,
                        purchase_id=purchase_id,
                        sales_id=sales_id,
                        product_id=product.id,
                        name=name,
                        quantity=0,  # Initial stock quantity
                        stock_alert=stock_alert,
                        gst=gst,
                        # is_deleted=not status,  # Assuming is_deleted is inverse of status
                        status=status,

                    )

                    messages.success(request, 'Product and Stock record added successfully.')

                except IntegrityError:
                    messages.error(request, 'There was an issue adding the product. Please try again.')


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

    # Fetch data for lists
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    products = Product.objects.all()
    brands = Brand.objects.all()
    units = Unit.objects.all()
    suppliers = Supplier.objects.all()

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
            'category_id': product.category.id,
            'subcategory_id': product.subcategory.id,
            'name': product.name,
            'prod_description': product.prod_description,
            'stock_alert': product.stock_alert,
            'gst': product.gst,
            'purchase_id': product.purchase.id,
            'sales_id': product.sales.id,
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

        # Now update the corresponding stock entry for this product
        stock = get_object_or_404(Stock, product_id=product.id)

        # Update stock fields related to the product
        stock.category_id = product.category_id
        stock.subcategory_id = product.subcategory_id
        stock.purchase_id = product.purchase_id
        stock.sales_id = product.sales_id
        stock.name = product.name
        stock.stock_alert = product.stock_alert
        stock.gst = product.gst
        # stock.is_deleted = not product.status  # Assuming is_deleted is the inverse of status
        stock.status = product.status
        # Save the updated stock entry to the database
        stock.save()
        messages.success(request, 'Product Updated successfully.')

        # Redirect back to the appropriate page after saving
        return redirect('product_add_category') # Replace with your URL name


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
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('product_add_category')

# Delete Category
def delete_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    subcategory.delete()
    messages.success(request, 'SubCategory deleted successfully.')
    return redirect('product_add_category')



# Delete Product
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    stock = Stock.objects.filter(product_id=product.id).first()
    if stock:
        stock.delete()
    product.delete()
    messages.success(request, 'Product and related Stock deleted successfully.')
    return redirect('product_add_category')  # Replace with your actual URL name

# Delete Brand
def delete_brand(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.delete()
    messages.success(request, 'Brand deleted successfully.')
    return redirect('product_add_category')

# Delete Unit
def delete_unit(request, id):
    unit = get_object_or_404(Unit, id=id)
    unit.delete()
    messages.success(request, 'Unit deleted successfully.')
    return redirect('product_add_category')

# Delete Supplier
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully.')
    return redirect('product_add_category')




