
from django.shortcuts import render
from django.views.generic import View, TemplateView

from dashboard.models import staff_Notification
from inventory.models import Stock
from product.models import Category, SubCategory
from transactions.models import SaleBill, PurchaseBill

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import F  # Import F for field references

from django.http import JsonResponse
from django.views import View
from django.db.models import F
from inventory.models import Stock
from product.models import Category

from django.http import JsonResponse
from django.views import View
from inventory.models import Stock
from product.models import Category
import json

class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        # NOTE: some DBs store boolean fields as BIT/VARYING (legacy schema),
        # which can break boolean filtering in PostgreSQL. Avoid SQL boolean
        # negation here and filter in Python.
        stockqueryset = Stock.objects.all().order_by('-quantity')
        categories = Category.objects.all()
        sales = SaleBill.objects.order_by('-time')[:3]
        purchases = PurchaseBill.objects.order_by('-time')[:3]
        count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
        notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by(
            '-created_at')


        stock_data = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'stock_alert': item.stock_alert,
                'subcategory_id': item.subcategory_id
            }
            for item in stockqueryset
            if not bool(getattr(item, "is_deleted", False))
        ]

        context = {
            'categories': categories,
            'stock_data': stock_data,
            'sales': sales,
            'purchases': purchases,
            'notification1': notification1,
            'count1': count1,
        }
        return render(request, self.template_name, context)


@csrf_exempt
def filter_stock(request):
    if request.method == 'POST':
        filters = json.loads(request.body)
        queryset = Stock.objects.all()
        queryset = [s for s in queryset if not bool(getattr(s, "is_deleted", False))]

        # If subcategory is provided and not an empty string, filter by subcategory
        if filters.get('subcategory') and filters['subcategory'] != "":
            queryset = [s for s in queryset if str(s.subcategory_id) == str(filters['subcategory'])]
        # If subcategory is an empty string, filter by category_id only
        elif filters.get('subcategory') == "":
            queryset = [s for s in queryset if str(s.category_id) == str(filters['category'])]

        # # Filter by subcategory if provided
        # if filters.get('subcategory'):
        #     queryset = queryset.filter(subcategory_id=filters['subcategory'])

        # Filter stocks that are completely out of stock
        if filters.get('out_of_stock'):
            queryset = [s for s in queryset if s.quantity == 0]

        # Filter stocks that are available (quantity > 0)
        if filters.get('available_stock'):
            queryset = [s for s in queryset if s.quantity > 0]

        # Filter stocks where quantity is less than or equal to alert_stock
        if filters.get('alert_stock'):
            queryset = [s for s in queryset if s.quantity <= s.stock_alert]

        # Prepare the stock data with alert status
        stock_data = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'stock_alert': item.stock_alert,  # Add an alert flag
                'alert': item.quantity <= item.stock_alert  # Add an alert flag
            }
            for item in queryset
        ]

        return JsonResponse({'stock_data': stock_data})



class GetSubcategoriesView(View):
    def get(self, request, category_id):
        subcategories = SubCategory.objects.active_only().filter(
            category_id=category_id
        ).values("id", "name", "category_id")
        return JsonResponse(list(subcategories), safe=False)
