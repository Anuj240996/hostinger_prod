

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages


# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.generic import (
#     View,
#     CreateView,
#     UpdateView
# )
# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib import messages

# from product.models import Product, SubCategory, Category
# from .models import Stock, FavoriteList
# from .forms import StockForm
# from django_filters.views import FilterView
# from .filters import StockFilter

# #
# # class StockListView(FilterView):
# #     filterset_class = StockFilter
# #     queryset = Stock.objects.filter(is_deleted=False)
# #     template_name = 'inventory.html'
# #     paginate_by = 10


# from django.views.generic import ListView
# from django.db.models import F

# # Add this to your StockListView or create a new view for these endpoints
# def get_subcategories(request, category_id):
#     subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
#     return JsonResponse(list(subcategories), safe=False)
# #
# # def get_stocks(request, subcategory_id):
# #     stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name', 'quantity', 'status', 'stock_alert')
# #     return JsonResponse(list(stocks), safe=False)

# class StockListView(ListView):
#     model = Stock
#     template_name = 'inventory.html'
#     paginate_by = 10

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.active_only()
#         context['subcategories'] = SubCategory.objects.active_only()
#         return context

# #
# # def get_all_stocks(request):
# #     if request.method == 'GET':
# #         stocks = Stock.objects.filter(is_deleted=False)  # Assuming you have a filter for active stocks
# #         stock_list = []
# #         for stock in stocks:
# #             stock_list.append({
# #                 'id': stock.id,
# #                 'name': stock.name,
# #                 'quantity': stock.quantity,
# #                 'status': stock.status,  # Adjust as necessary for your status logic
# #                 'stock_alert': stock.stock_alert,  # Include stock_alert here as well
# #             })
# #         return JsonResponse(stock_list, safe=False)


# # View to fetch stocks based on different filter criteria
# def get_stocks_by_all(request, filter_type):
#     if filter_type == 'all':
#         stocks = Stock.objects.filter(is_deleted=False)
#     elif filter_type == 'all_active':
#         stocks = Stock.objects.filter(is_deleted=False, status=True)
#     elif filter_type == 'all_inactive':
#         stocks = Stock.objects.filter(is_deleted=False, status=False)
#     elif filter_type == 'all_stock_alert':
#         stocks = Stock.objects.filter(is_deleted=False, status=True, quantity__lte=F('stock_alert'))
#     else:
#         # If no valid option is selected, initialize stocks to an empty queryset
#         stocks = Stock.objects.none()

#     stock_list = []
#     for stock in stocks:
#         stock_list.append({
#             'id': stock.id,
#             'name': stock.name,
#             'quantity': stock.quantity,
#             'status': stock.status,
#             'stock_alert': stock.stock_alert,
#             'category': stock.category.short_name,
#             'subcategory': stock.subcategory.short_name,
#             'purchase': stock.purchase.short_name,
#         })
#     return JsonResponse(stock_list, safe=False)

# def get_stocks_by_filter(request, filter_type, category_id=None, subcategory_id=None):
#     stocks = Stock.objects.filter(is_deleted=False)

#     # Apply the filter based on the filter type
#     if filter_type == 'select_all':
#         pass
#     elif filter_type == 'select_active':
#         stocks = stocks.filter(status=True)
#     elif filter_type == 'select_inactive':
#         stocks = stocks.filter(status=False)
#     elif filter_type == 'select_stock_alert':
#         stocks = stocks.filter(status=True, quantity__lte=F('stock_alert'))

#     # Filter by category if provided
#     if category_id:
#         stocks = stocks.filter(category_id=category_id)

#     # Filter by subcategory if provided
#     if subcategory_id:
#         stocks = stocks.filter(subcategory_id=subcategory_id)

#     # Prepare the stock list to return
#     stock_list = [{
#         'id': stock.id,
#         'name': stock.name,
#         'quantity': stock.quantity,
#         'status': stock.status,
#         'stock_alert': stock.stock_alert,
#         'category': stock.category.short_name,
#         'subcategory': stock.subcategory.short_name,
#         'purchase': stock.purchase.short_name,
#     } for stock in stocks]

#     return JsonResponse(stock_list, safe=False)


# class StockCreateView(SuccessMessageMixin,
#                       CreateView):  # createview class to add new stock, mixin used to display message
#     model = Stock  # setting 'Stock' model as model
#     form_class = StockForm  # setting 'StockForm' form as form
#     template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
#     success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
#     success_message = "Stock has been created successfully"  # displays message when form is submitted

#     def get_context_data(self, **kwargs):  # used to send additional context
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'New Stock'
#         context["savebtn"] = 'Add to Inventory'
#         return context

# #
# # class StockUpdateView(SuccessMessageMixin, UpdateView):  # updateview class to edit stock, mixin used to display message
# #     model = Stock  # setting 'Stock' model as model
# #     form_class = StockForm  # setting 'StockForm' form as form
# #     template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
# #     success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
# #     success_message = "Stock has been updated successfully"  # displays message when form is submitted
# #
# #     def get_context_data(self, **kwargs):  # used to send additional context
# #         context = super().get_context_data(**kwargs)
# #         context["title"] = 'Edit Stock'
# #         context["savebtn"] = 'Update Stock'
# #         context["delbtn"] = 'Delete Stock'
# #         return context


# class StockUpdateView(SuccessMessageMixin, UpdateView):  # updateview class to edit stock, mixin used to display message
#     model = Stock  # setting 'Stock' model as model
#     form_class = StockForm  # setting 'StockForm' form as form
#     template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
#     success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
#     success_message = "Stock has been updated successfully"  # displays message when form is submitted

#     def get_context_data(self, **kwargs):  # used to send additional context
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edit Stock'
#         context["savebtn"] = 'Update Stock'
#         context["delbtn"] = 'Delete Stock'
#         return context

#     def form_valid(self, form):
#         # Save the Stock form and get the stock instance
#         stock = form.save()

#         # Check if there's a related product and update its status
#         if stock.product:
#             # Update the related Product's status to match the Stock's status
#             product = stock.product
#             product.status = stock.status
#             product.save()  # Save the updated product status

#         return super().form_valid(form)  # Continue with the default form_valid logic


# class StockDeleteView(View):  # view class to delete stock
#     template_name = "delete_stock.html"  # 'delete_stock.html' used as the template
#     success_message = "Stock has been deleted successfully"  # displays message when form is submitted

#     def get(self, request, pk):
#         stock = get_object_or_404(Stock, pk=pk)
#         return render(request, self.template_name, {'object': stock})

#     def post(self, request, pk):
#         stock = get_object_or_404(Stock, pk=pk)
#         stock.is_deleted = True
#         stock.save()
#         messages.success(request, self.success_message)
#         return redirect('inventory')

# #
# # def create_favorite_list(request):
# #     favorite_list_name = request.POST.get('favorite_list_name')
# #     selected_stocks = request.POST.getlist('selected_stocks[]')
# #
# #     # Create or update the favorite list
# #     favorite_list, created = FavoriteList.objects.get_or_create(name=favorite_list_name)
# #
# #     # Update the stocks associated with the favorite list
# #     favorite_list.stocks.clear()
# #     favorite_list.stocks.add(*selected_stocks)
# #     favorite_list.save()
# #
# #     return JsonResponse({'message': 'Favorite list created successfully!'})


# from django.http import JsonResponse
# from django.views.decorators.http import require_POST, require_GET
# from .models import Stock, FavoriteList
# from django.db import IntegrityError

# # from django.http import JsonResponse
# # from django.views.decorators.http import require_POST
# # from .models import Stock, FavoriteList
# #
# #
# # @require_POST
# # def create_favorite_list(request):
# #     favorite_list_name = request.POST.get('favorite_list_name')
# #     selected_stocks = request.POST.getlist('selected_stocks[]')
# #
# #     # Create or update the favorite list
# #     favorite_list, created = FavoriteList.objects.get_or_create(name=favorite_list_name)
# #
# #     # Update the stocks associated with the favorite list
# #     favorite_list.stocks.clear()
# #     favorite_list.stocks.add(*selected_stocks)
# #     favorite_list.save()
# #
# #     return JsonResponse({'message': 'Favorite list created successfully!'})

# #
# # from django.http import JsonResponse, HttpResponseRedirect
# # from django.views.generic import ListView
# # from .models import FavoriteList
# # from django.shortcuts import get_object_or_404
# #
# #
# # class StockListView1(ListView):
# #     model = Stock
# #     template_name = 'favorite.html'
# #     paginate_by = 10
# #
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['categories'] = Category.objects.active_only()
# #         context['subcategories'] = SubCategory.objects.active_only()
# #         return context
# #
# #     # View to fetch stocks based on different filter criteria
# #     def get_stocks_by_all(request, filter_type):
# #         if filter_type == 'all':
# #             stocks = Stock.objects.filter(is_deleted=False)
# #         elif filter_type == 'all_active':
# #             stocks = Stock.objects.filter(is_deleted=False, status=True)
# #         elif filter_type == 'all_inactive':
# #             stocks = Stock.objects.filter(is_deleted=False, status=False)
# #         elif filter_type == 'all_stock_alert':
# #             stocks = Stock.objects.filter(is_deleted=False, status=True, quantity__lte=F('stock_alert'))
# #         else:
# #             # If no valid option is selected, initialize stocks to an empty queryset
# #             stocks = Stock.objects.none()
# #
# #         stock_list = []
# #         for stock in stocks:
# #             stock_list.append({
# #                 'id': stock.id,
# #                 'name': stock.name,
# #                 'quantity': stock.quantity,
# #                 'status': stock.status,
# #                 'stock_alert': stock.stock_alert,
# #                 'category': stock.category.short_name,
# #                 'subcategory': stock.subcategory.short_name,
# #                 'purchase': stock.purchase.short_name,
# #             })
# #         return JsonResponse(stock_list, safe=False)
# #
# #
# # # Create favorite list view
# # def create_favorite_list(request):
# #     if request.method == 'POST':
# #         list_name = request.POST.get('list_name', 'New Favorite List')
# #         selected_stock_ids = request.POST.getlist('selected_stocks[]')
# #
# #         # Create a new FavoriteList instance
# #         favorite_list = FavoriteList.objects.create(name=list_name)
# #
# #         # Add selected stocks to the favorite list
# #         for stock_id in selected_stock_ids:
# #             stock = get_object_or_404(Stock, id=stock_id)
# #             favorite_list.stocks.add(stock)
# #
# #         return JsonResponse({'message': 'Favorite list created successfully', 'list_name': favorite_list.name})
# #     return JsonResponse({'error': 'Invalid request'}, status=400)
# #


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from .models import Stock, FavoriteList


# # @csrf_exempt
# # def create_favorite_list(request):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         list_name = data.get('name')
# #         stock_ids = [stock['id'] for stock in data.get('stocks', [])]
# #
# #         favorite_list = FavoriteList.objects.create(name=list_name)
# #         favorite_list.stocks.set(Stock.objects.filter(id__in=stock_ids))
# #
# #         return JsonResponse({'message': 'Favorite list created successfully'})

# @csrf_exempt
# def create_favorite_list(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         list_name = data.get('name')
#         stock_ids = [stock['id'] for stock in data.get('stocks', [])]

#         # Check if a FavoriteList with the same name already exists
#         # if FavoriteList.objects.filter(name=list_name).exists():
#         if FavoriteList.objects.filter(name__iexact=list_name).exists():
#             return JsonResponse({'message': 'Favorite list with this name already exists.'}, status=400)

#         favorite_list = FavoriteList.objects.create(name=list_name)
#         favorite_list.stocks.set(Stock.objects.filter(id__in=stock_ids))

#         return JsonResponse({'message': 'Favorite list created successfully'})


# # Update context to pass CSRF token and stock data
# class StockListView1(ListView):
#     model = Stock
#     template_name = 'favorite.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.active_only()
#         return context

# # @require_GET
# # def get_stocks_all(request):
# #     # stocks = Stock.objects.all().values('id', 'name', 'quantity', 'status', 'category__short_name')
# #     # stocks_data = list(stocks)
# #     # return JsonResponse(stocks_data, safe=False)
# #     category_id = request.GET.get('category_id')
# #     subcategory_id = request.GET.get('subcategory_id')
# #
# #     stocks = Stock.objects.all()
# #     if category_id:
# #         stocks = stocks.filter(category_id=category_id)
# #     if subcategory_id:
# #         stocks = stocks.filter(subcategory_id=subcategory_id)
# #
# #     stocks_data = [
# #         {
# #             'id': stock.id,
# #             'category': stock.category.name,
# #             'subcategory': stock.subcategory.name,
# #             'name': stock.name,
# #             'quantity': stock.quantity,
# #             'status': stock.status,
# #         }
# #         for stock in stocks
# #     ]
# #     return JsonResponse(stocks_data, safe=False)
# #
# # # Fetch subcategories based on category ID
# # def get_subcategories(request, category_id):
# #     subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
# #     return JsonResponse({'subcategories': list(subcategories)})


# # def get_stocks_all(request):
# #     category_id = request.GET.get('category_id')
# #     subcategory_id = request.GET.get('subcategory_id')
# #
# #     stocks = Stock.objects.all()
# #     if category_id:
# #         stocks = stocks.filter(category_id=category_id)
# #     if subcategory_id:
# #         stocks = stocks.filter(subcategory_id=subcategory_id)
# #
# #     stocks_data = [
# #         {
# #             'id': stock.id,
# #             'category': stock.category.name,
# #             'subcategory': stock.subcategory.name,
# #             'name': stock.name,
# #             'quantity': stock.quantity,
# #             'status': stock.status,
# #         }
# #         for stock in stocks
# #     ]
# #     return JsonResponse(stocks_data, safe=False)
# #
# # @require_GET
# # def get_stocks_all(request):
# #     category_id = request.GET.get('category_id')
# #     subcategory_id = request.GET.get('subcategory_id')
# #
# #     stocks = Stock.objects.all()
# #     if category_id and category_id != 'all':
# #         stocks = stocks.filter(category_id=category_id)
# #     if subcategory_id and subcategory_id != 'all':
# #         stocks = stocks.filter(subcategory_id=subcategory_id)
# #
# #     stocks_data = [
# #         {
# #             'id': stock.id,
# #             'category': stock.category.name,
# #             'subcategory': stock.subcategory.name,
# #             'name': stock.name,
# #             'quantity': stock.quantity,
# #             'status': stock.status,
# #         }
# #         for stock in stocks
# #     ]
# #     return JsonResponse(stocks_data, safe=False)


# @require_GET
# def get_stocks_all(request):
#     category_id = request.GET.get('category_id')
#     subcategory_id = request.GET.get('subcategory_id')

#     # Filter stocks where is_deleted is False
#     stocks = Stock.objects.filter(is_deleted=False, status=True).distinct()

#     if category_id and category_id != 'all':
#         stocks = stocks.filter(category_id=category_id)
#     if subcategory_id and subcategory_id != 'all':
#         stocks = stocks.filter(subcategory_id=subcategory_id)

#     stocks_data = [
#         {
#             'id': stock.id,
#             'category': stock.category.name,
#             'subcategory': stock.subcategory.name,
#             'name': stock.name,
#             'quantity': stock.quantity,
#             'status': stock.status,
#         }
#         for stock in stocks
#     ]
#     return JsonResponse(stocks_data, safe=False)


# @require_GET
# def get_subcategories1(request):
#     category_id = request.GET.get('category_id')
#     subcategories = SubCategory.objects.active_only().filter(category_id=category_id)
#     subcategory_data = [{'id': subcat.id, 'name': subcat.name} for subcat in subcategories]
#     return JsonResponse(subcategory_data, safe=False)



# # @require_GET
# # def get_subcategories(request):
# #     category_id = request.GET.get('category_id')
# #     subcategories = SubCategory.objects.filter(category_id=category_id)
# #     subcategory_data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
# #     return JsonResponse(subcategory_data, safe=False)



# from django.shortcuts import render
# from .models import FavoriteList, Stock
# from django.http import JsonResponse
# from django.views.generic import ListView



# # View to display all favorite lists and their associated stock
# class FavoriteListView(ListView):
#     model = FavoriteList
#     template_name = 'favorite_list.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Get the stocks for each favorite list
#         for favorite_list in context['object_list']:
#             favorite_list_stocks = favorite_list.stocks.all()  # Fetch related stocks
#             context['favorite_list_stocks'] = favorite_list_stocks  # Add to context
#         return context


# from django.http import JsonResponse
# from .models import FavoriteList

# @require_GET
# def favorite_list_details(request, favorite_list_id):
#     try:
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#         stocks = favorite_list.stocks.values('name')  # Only return stock names
#         return JsonResponse({
#             'name': favorite_list.name,
#             'stocks': list(stocks)
#         })
#     except FavoriteList.DoesNotExist:
#         return JsonResponse({'message': 'Favorite list not found.'}, status=404)


# # def get_favorite_list(request):
# #     favorite_list_id = request.GET.get('favorite_list_id')
# #     try:
# #         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
# #         data = {
# #             'name': favorite_list.name,
# #             'stocks': [
# #                 {'id': stock.id, 'name': stock.name, 'category': stock.category.name, 'subcategory': stock.subcategory.name}
# #                 for stock in favorite_list.stocks.all()
# #             ]
# #         }
# #         return JsonResponse(data)
# #     except FavoriteList.DoesNotExist:
# #         return JsonResponse({'error': 'Favorite list not found'}, status=404)


# # from django.http import JsonResponse
# # from .models import FavoriteList, Stock
# #
# #
# # @csrf_exempt
# # def get_favorite_stock_list(request, favorite_list_id):
# #     stocks = FavoriteList.objects.filter(favorite_list_id=favorite_list_id)
# #     stock_data = [{
# #         'id': stock.id,
# #         'name': stock.name,
# #         'category': stock.category.name,
# #         'subcategory': stock.subcategory.name,
# #     } for stock in stocks]
# #     return JsonResponse(stock_data, safe=False)
# #
# #
# # @csrf_exempt
# # def update_favorite_stock_list(request, favorite_list_id):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         selected_stocks = data.get('stocks', [])
# #         # Assuming FavoriteStockList is a model for storing favorite stocks
# #         favorite_list = FavoriteStockList.objects.get(id=favorite_list_id)
# #
# #         # Clear the existing favorite list and add the selected stocks
# #         favorite_list.stocks.clear()
# #         for stock in selected_stocks:
# #             stock_instance = Stock.objects.get(id=stock['id'])
# #             favorite_list.stocks.add(stock_instance)
# #
# #         return JsonResponse({'success': True})
# #     return JsonResponse({'success': False})

# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from .models import FavoriteList, Stock
# import json


# # # def edit_favorite_list(request, favorite_id):
# # def edit_favorite_list(request, favorite_id):
# #         favorite_list = get_object_or_404(FavoriteList, id=favorite_id)
# #
# #         # If POST, update favorite list
# #         if request.method == 'POST':
# #             # Retrieve stock IDs from form data
# #             stock_ids = request.POST.getlist('stock_ids[]')
# #
# #             # Get Stock objects corresponding to these IDs
# #             selected_stocks = Stock.objects.filter(id__in=stock_ids)
# #
# #             # Update the FavoriteList stocks with the selected stocks
# #             favorite_list.stocks.set(selected_stocks)
# #
# #             # Save changes to the database
# #             favorite_list.save()
# #
# #             # Redirect to some confirmation or success page
# #             return redirect('favorite_list_view')  # Replace with the appropriate URL name
# #
# #         # If GET, render the page with existing stocks
# #         existing_stocks = favorite_list.stocks.all()
# #         all_stocks = Stock.objects.exclude(id__in=existing_stocks.values_list('id', flat=True))
# #
# #         context = {
# #             'favorite_records': existing_stocks,
# #             'stock_options': all_stocks,
# #             'favorite_list': favorite_list,
# #         }
# #         return render(request, 'edit_favorite.html', context)



# # from django.shortcuts import render, get_object_or_404, redirect
# # from .models import FavoriteList, Stock, Category, SubCategory
# #
# # def edit_favorite_list(request, favorite_id):
# #     favorite_list = get_object_or_404(FavoriteList, id=favorite_id)
# #
# #     if request.method == 'POST':
# #         stock_ids = request.POST.getlist('stock_ids[]')
# #         selected_stocks = Stock.objects.filter(id__in=stock_ids)
# #         favorite_list.stocks.set(selected_stocks)
# #         favorite_list.save()
# #         return redirect('favorite_list_view')
# #
# #     existing_stocks = favorite_list.stocks.select_related('category', 'subcategory').all()
# #     all_stocks = Stock.objects.exclude(id__in=existing_stocks.values_list('id', flat=True)).select_related('category', 'subcategory')
# #
# #     context = {
# #         'favorite_records': existing_stocks,
# #         'stock_options': all_stocks,
# #         'favorite_list': favorite_list,
# #     }
# #     return render(request, 'edit_favorite.html', context)
# #


# from django.shortcuts import render, get_object_or_404, redirect
# from .models import FavoriteList, Stock, Category, SubCategory

# def edit_favorite_list(request, favorite_id):
#     favorite_list = get_object_or_404(FavoriteList, id=favorite_id)

#     if request.method == 'POST':
#         stock_ids = request.POST.getlist('stock_ids[]')
#         selected_stocks = Stock.objects.filter(id__in=stock_ids)
#         favorite_list.stocks.set(selected_stocks)
#         favorite_list.save()
#         # messages.success(request, "FavoriteList Records saved successfully!")
#         return redirect('favorite_list_view')

#     existing_stocks = favorite_list.stocks.select_related('category', 'subcategory').all()
#     all_categories = Category.objects.all()
#     all_subcategories = SubCategory.objects.all()
#     all_stocks = Stock.objects.all()

#     context = {
#         'favorite_records': existing_stocks,
#         'categories': all_categories,
#         'subcategories': all_subcategories,
#         'stocks': all_stocks,
#         'favorite_list': favorite_list,
#     }
#     return render(request, 'edit_favorite.html', context)


# def get_subcategories_edit(request):
#     category_id = request.GET.get('category_id')
#     subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
#     return JsonResponse({'subcategories': list(subcategories)})

# def get_stocks_edit(request):
#     subcategory_id = request.GET.get('subcategory_id')
#     # stocks = Stock.objects.filter(subcategory_id=subcategory_id).values('id', 'name')
#     # stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name')
#     stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False, status=True).values('id', 'name', 'gst')
#     return JsonResponse({'stocks': list(stocks)})


# #
# # def get_stock_quantity(request):
# #     stock_id = request.GET.get('stock_id')
# #     stock = Stock.objects.get(id=stock_id)
# #     return JsonResponse({'quantity': stock.quantity})


# def get_stock_quantity(request):
#     stock_id = request.GET.get('stock_id')
#     stock = Stock.objects.filter(id=stock_id).first()
#     if stock:
#         return JsonResponse({
#             'quantity': stock.quantity,
#             'stock_alert': stock.stock_alert,
#             'purchase': stock.purchase.short_name,

#             'gst': stock.gst,

#             'purchase_id': stock.purchase.id,
#         })
#     return JsonResponse({'error': 'Stock not found'}, status=404)

# def get_stock_detail(request):
#     stock_id = request.GET.get('stock_id')
#     try:
#         stock = Stock.objects.get(pk=stock_id, is_deleted=False, status=True)
#         data = {
#             'stock': {
#                 'id': stock.id,
#                 'name': stock.name,
#                 'quantity': stock.quantity,
#             }
#         }
#         return JsonResponse(data)
#     except Stock.DoesNotExist:
#         return JsonResponse({'error': 'Stock not found'}, status=404)
# #
# # def edit_favorite_list(request, favorite_list_id):
# #     # Fetch the favorite stock list for the given ID
# #     favorite_list = get_object_or_404(FavoriteList, id=favorite_list_id)
# #
# #     # Fetch the stocks related to this favorite list
# #     stocks = favorite_list.stocks.all()
# #
# #     # Prepare the data to pass to the template
# #     stock_data = [{
# #         'id': stock.id,
# #         'name': stock.name,
# #         'category': stock.category.name,
# #         'subcategory': stock.subcategory.name,
# #     } for stock in stocks]
# #
# #     return render(request, 'edit_favorite.html', {
# #         'favorite_list': favorite_list,
# #         'stock_data': stock_data
# #     })

# #
# # def update_favorite_stock_list(request, favorite_list_id):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         selected_stocks = data.get('stocks', [])
# #
# #         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
# #         favorite_list.stocks.clear()
# #
# #         # Add the selected stocks to the favorite list
# #         for stock in selected_stocks:
# #             stock_instance = Stock.objects.get(id=stock['id'])
# #             favorite_list.stocks.add(stock_instance)
# #
# #         return JsonResponse({'success': True})
# #     return JsonResponse({'success': False})

# # def update_favorite_stock_list(request, favorite_list_id):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         stocks_to_add = data.get('stocks_to_add', [])
# #         stocks_to_remove = data.get('stocks_to_remove', [])
# #
# #         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
# #
# #         # Remove stocks
# #         for stock_id in stocks_to_remove:
# #             stock = Stock.objects.get(id=stock_id)
# #             favorite_list.stocks.remove(stock)
# #
# #         # Add new stocks
# #         for stock_data in stocks_to_add:
# #             stock = Stock.objects.get(id=stock_data['id'])
# #             favorite_list.stocks.add(stock)
# #
# #         return JsonResponse({'success': True})
# #     return JsonResponse({'success': False})
# #
# # from django.http import JsonResponse
# # from .models import FavoriteList, Stock
# #
# # from django.http import JsonResponse
# # from .models import FavoriteList, Stock
# #
# # def remove_stock_from_favorite_list(request, favorite_list_id, stock_id):
# #     if request.method == 'POST':
# #         try:
# #             # Retrieve the specific favorite list by ID
# #             favorite_list = FavoriteList.objects.get(id=favorite_list_id)
# #
# #             # Find the stock and remove it from the list
# #             stock = Stock.objects.get(id=stock_id)
# #             favorite_list.stocks.remove(stock)
# #
# #             return JsonResponse({'success': True})
# #         except FavoriteList.DoesNotExist:
# #             return JsonResponse({'success': False, 'message': 'Favorite list not found.'})
# #         except Stock.DoesNotExist:
# #             return JsonResponse({'success': False, 'message': 'Stock not found.'})
# #     return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# def delete_favorite_list(request, favorite_list_id):
#     try:
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#         favorite_list.delete()
#         return JsonResponse({'message': 'Favorite list deleted successfully.'})
#     except FavoriteList.DoesNotExist:
#         return JsonResponse({'message': 'Favorite list not found.'}, status=404)






# import datetime
# from django.db.models import Q
# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render,redirect
#
# from customer.models import Customer
# from dashboard.models import staff_Notification
# from user.models import Profile
# from .models import *
# from datetime import date
# from datetime import datetime
# from django.contrib.auth.models import User
# from django.contrib.auth import login,logout,authenticate
# from django.contrib.auth.decorators import login_required
# from .decorators import auth_users, allowed_users
# from django.contrib.auth import get_user, logout, login
# from django.contrib.auth import get_user_model
# from django.contrib.sessions.middleware import SessionMiddleware
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone
# from django.db.models import Q
#
# #from django.shortcuts import render, HttpResponse
#
#
# #
# # from django.shortcuts import render, redirect
# # from .forms import CategoryForm, SubCategoryForm, ProductForm
# #
# # def add_category(request):
# #     if request.method == "POST":
# #         form = CategoryForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_category')
# #     else:
# #         form = CategoryForm()
# #     return render(request, 'product/add_category.html', {'form': form})
# #
# # def add_subcategory(request):
# #     if request.method == "POST":
# #         form = SubCategoryForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_subcategory')
# #     else:
# #         form = SubCategoryForm()
# #     return render(request, 'product/add_subcategory.html', {'form': form})
# #
# # def add_product(request):
# #     if request.method == "POST":
# #         form = ProductForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_product')
# #     else:
# #         form = ProductForm()
# #     return render(request, 'product/add_product.html', {'form': form})
#
#
# from django.shortcuts import render, redirect
# from .forms import CategoryForm, SubCategoryForm, ProductForm
# from .models import Category, SubCategory, Product
#
# def add_category(request):
#     # subcategory_form = None
#     # product_form = None
#     # if request.method == "POST":
#     #     if 'add_category' in request.POST:
#     #         category_form = CategoryForm(request.POST)
#     #         if category_form.is_valid():
#     #             category_form.save()
#     #             return redirect('product_add_category')
#     #     elif 'add_subcategory' in request.POST:
#     #         subcategory_form = SubCategoryForm(request.POST)
#     #         if subcategory_form.is_valid():
#     #             subcategory_form.save()
#     #             return redirect('product_add_category')
#     #     elif 'add_product' in request.POST:
#     #         product_form = ProductForm(request.POST)
#     #         if product_form.is_valid():
#     #             product_form.save()
#     #             return redirect('product_add_category')
#     # else:
#     #     category_form = CategoryForm()
#     #     subcategory_form = SubCategoryForm()
#     #     product_form = ProductForm()
#     #
#     # categories = Category.objects.all()
#     # subcategories = SubCategory.objects.all()
#     # products = Product.objects.all()
#     #
#     # context = {
#     #     'category_form': category_form,
#     #     'subcategory_form': subcategory_form,
#     #     'product_form': product_form,
#     #     'categories': categories,
#     #     'subcategories': subcategories,
#     #     'products': products,
#     # }
#     category_form = CategoryForm()
#     subcategory_form = SubCategoryForm()
#     product_form = ProductForm()
#
#     if request.method == "POST":
#         if 'add_category' in request.POST:
#             category_form = CategoryForm(request.POST)
#             if category_form.is_valid():
#                 category_form.save()
#                 return redirect('product_add_category')
#         elif 'add_subcategory' in request.POST:
#             subcategory_form = SubCategoryForm(request.POST)
#             if subcategory_form.is_valid():
#                 subcategory_form.save()
#                 return redirect('product_add_category')
#         elif 'add_product' in request.POST:
#             product_form = ProductForm(request.POST)
#             if product_form.is_valid():
#                 product_form.save()
#                 return redirect('product_add_category')
#
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     products = Product.objects.all()
#
#     context = {
#         'category_form': category_form,
#         'subcategory_form': subcategory_form,
#         'product_form': product_form,
#         'categories': categories,
#         'subcategories': subcategories,
#         'products': products,
#     }
#     return render(request, 'product/add_category.html', context)
#
#
# def load_subcategories(request):
#     category_id = request.GET.get('category_id')
#     subcategories = SubCategory.objects.filter(category_id=category_id).all()
#     return JsonResponse(list(subcategories.values('id', 'name')), safe=False)
from audioop import reverse

from django.http import JsonResponse
# from django.http import JsonResponse
# from django.shortcuts import render, redirect
# from .forms import CategoryForm, SubCategoryForm, ProductForm
# from .models import Category, SubCategory, Product
#
# def add_category(request):
#     if request.method == "POST":
#         if 'add_category' in request.POST:
#             category_form = CategoryForm(request.POST)
#             if category_form.is_valid():
#                 category_form.save()
#                 return redirect('product_add_category')
#         elif 'add_subcategory' in request.POST:
#             subcategory_form = SubCategoryForm(request.POST)
#             if subcategory_form.is_valid():
#                 subcategory_form.save()
#                 return redirect('product_add_category')
#         elif 'add_product' in request.POST:
#             product_form = ProductForm(request.POST)
#             if product_form.is_valid():
#                 product_form.save()
#                 return redirect('product_add_category')
#     else:
#         category_form = CategoryForm()
#         subcategory_form = SubCategoryForm()
#         product_form = ProductForm()
#
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     products = Product.objects.all()
#
#     context = {
#         'category_form': category_form,
#         'subcategory_form': subcategory_form,
#         'product_form': product_form,
#         'categories': categories,
#         'subcategories': subcategories,
#         'products': products,
#     }
#
#     return render(request, 'product/add_category.html', context)

#
# from django.shortcuts import render, redirect, get_object_or_404
#
# from .forms import CategoryForm, SubCategoryForm, BrandForm, UnitForm, SupplierForm
# from .models import Category, SubCategory, Product, Brand, Unit, Supplier
#
#
# def add_category(request):
#     category_form = None
#     subcategory_form = None
#     brand_form = None
#     unit_form = None
#     supplier_form = None
#     if request.method == "POST":
#         if 'add_category' in request.POST:
#             category_form = CategoryForm(request.POST)
#             if category_form.is_valid():
#                 category_form.save()
#                 # return redirect('product_add_category')
#         # elif 'edit_category' in request.POST:
#         #     category = get_object_or_404(Category, id=request.POST.get('category_id'))
#         #     category_form = CategoryForm(request.POST, instance=category)
#         #     if category_form.is_valid():
#         #         category_form.save()
#         elif 'add_subcategory' in request.POST:
#             subcategory_form = SubCategoryForm(request.POST)
#             if subcategory_form.is_valid():
#                 subcategory_form.save()
#                 # return redirect('product_add_category')
#         elif 'add_product' in request.POST:
#             category_id = request.POST.get('category')
#             subcategory_id = request.POST.get('subcategory')
#             purchase_id = request.POST.get('purchase_unit')
#             sales_id = request.POST.get('sales_unit')
#             name = request.POST.get('name')
#             prod_description = request.POST.get('prod_description')
#             stock_alert = request.POST.get('stock_alert')
#             status = request.POST.get('status') == 'on'
#             Product.objects.create(
#                 category_id=category_id,
#                 subcategory_id=subcategory_id,
#                 purchase_id=purchase_id,
#                 sales_id=sales_id,
#                 name=name,
#                 prod_description=prod_description,
#                 stock_alert=stock_alert,
#                 status=status
#             )
#             # return redirect('product_add_category')
#         elif 'add_brand' in request.POST:
#             brand_form = BrandForm(request.POST)
#             if brand_form.is_valid():
#                 brand_form.save()
#                 # return redirect('product_add_category')
#         elif 'add_unit' in request.POST:
#             unit_form = UnitForm(request.POST)
#             if unit_form.is_valid():
#                 unit_form.save()
#                 # return redirect('product_add_category')
#         elif 'add_supplier' in request.POST:
#             supplier_form = SupplierForm(request.POST)
#             if supplier_form.is_valid():
#                 supplier_form.save()
#                 # return redirect('product_add_category')
#
#     # else:
#     category_form = CategoryForm()
#     subcategory_form = SubCategoryForm()
#     brand_form = BrandForm()
#     unit_form = UnitForm()
#     supplier_form = SupplierForm()
#     # product_form = ProductForm()
#
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     products = Product.objects.all()
#     brands = Brand.objects.all()
#     units = Unit.objects.all()
#     suppliers = Supplier.objects.all()
#
#     context = {
#         'categories': categories,
#         'subcategories': subcategories,
#         'products': products,
#         'brands': brands,
#         'units': units,
#         'suppliers': suppliers,
#         'category_form': category_form,
#         'subcategory_form': subcategory_form,
#         'brand_form': brand_form,
#         'unit_form': unit_form,
#         'supplier_form': supplier_form,
#         # 'product_form': product_form,
#     }
#     return render(request, 'product/add_category.html', context)
#
# #
# # def load_subcategories(request):
# #     category_id = request.GET.get('category_id')
# #     print(category_id)
# #     # subcategories = SubCategory.objects.filter(category_id=category_id).order_by('name')
# #     subcategories = SubCategory.objects.filter(category_id=category_id).order_by('name').values('id', 'name')
# #     # return JsonResponse(list(subcategories.values('id', 'name')), safe=False)
# #     return JsonResponse(list(subcategories), safe=False)
#

#
# # SubCategory Edit and Delete Views
# def edit_subcategory(request, id):
#     subcategory = get_object_or_404(SubCategory, id=id)
#     if request.method == "POST":
#         form = SubCategoryForm(request.POST, instance=subcategory)
#         if form.is_valid():
#             form.save()
#             return redirect('product_add_category')
#     else:
#         form = SubCategoryForm(instance=subcategory)
#     return render(request, 'product/add_category.html', {'form': form})
#
# def delete_subcategory(request, id):
#     subcategory = get_object_or_404(SubCategory, id=id)
#     subcategory.delete()
#     return redirect('product_add_category')
# #
# # # Product Edit and Delete Views
# # def edit_product(request, pk):
# #     product = get_object_or_404(Product, pk=pk)
# #     if request.method == "POST":
# #         form = ProductForm(request.POST, instance=product)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_category')
# #     else:
# #         form = ProductForm(instance=product)
# #     return render(request, 'product/add_category.html', {'form': form})
# #
# # def delete_product(request, pk):
# #     product = get_object_or_404(Product, pk=pk)
# #     product.delete()
# #     return redirect('product_add_category')
# #
# # # Brand Edit and Delete Views
# # def edit_brand(request, pk):
# #     brand = get_object_or_404(Brand, pk=pk)
# #     if request.method == "POST":
# #         form = BrandForm(request.POST, instance=brand)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_category')
# #     else:
# #         form = BrandForm(instance=brand)
# #     return render(request, 'product/add_category.html', {'form': form})
# #
# # def delete_brand(request, pk):
# #     brand = get_object_or_404(Brand, pk=pk)
# #     brand.delete()
# #     return redirect('product_add_category')
# #
# # # Unit Edit and Delete Views
# # def edit_unit(request, pk):
# #     unit = get_object_or_404(Unit, pk=pk)
# #     if request.method == "POST":
# #         form = UnitForm(request.POST, instance=unit)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_category')
# #     else:
# #         form = UnitForm(instance=unit)
# #     return render(request, 'product/add_category.html', {'form': form})
# #
# # def delete_unit(request, pk):
# #     unit = get_object_or_404(Unit, pk=pk)
# #     unit.delete()
# #     return redirect('product_add_category')
# #
# # # Supplier Edit and Delete Views
# # def edit_supplier(request, pk):
# #     supplier = get_object_or_404(Supplier, pk=pk)
# #     if request.method == "POST":
# #         form = SupplierForm(request.POST, instance=supplier)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('product_add_category')
# #     else:
# #         form = SupplierForm(instance=supplier)
# #     return render(request, 'product/add_category.html', {'form': form})
# #
# # def delete_supplier(request, pk):
# #     supplier = get_object_or_404(Supplier, pk=pk)
# #     supplier.delete()
# #     return redirect('product_add_category')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    CreateView,
    UpdateView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from product.models import Product, SubCategory, Category
from .models import Stock, FavoriteList, FavoriteListStock
from transactions.models import PurchaseItem, SaleItem, FinalSaleItem, ReturnSaleItem, PurchaseSerial
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter

#
# class StockListView(FilterView):
#     filterset_class = StockFilter
#     queryset = Stock.objects.filter(is_deleted=False)
#     template_name = 'inventory.html'
#     paginate_by = 10


from django.views.generic import ListView
from django.db.models import F

# Add this to your StockListView or create a new view for these endpoints
def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)
#
# def get_stocks(request, subcategory_id):
#     stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name', 'quantity', 'status', 'stock_alert')
#     return JsonResponse(list(stocks), safe=False)

class StockListView(ListView):
    model = Stock
    template_name = 'inventory.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.active_only()
        context['subcategories'] = SubCategory.objects.active_only()
        return context

#
# def get_all_stocks(request):
#     if request.method == 'GET':
#         stocks = Stock.objects.filter(is_deleted=False)  # Assuming you have a filter for active stocks
#         stock_list = []
#         for stock in stocks:
#             stock_list.append({
#                 'id': stock.id,
#                 'name': stock.name,
#                 'quantity': stock.quantity,
#                 'status': stock.status,  # Adjust as necessary for your status logic
#                 'stock_alert': stock.stock_alert,  # Include stock_alert here as well
#             })
#         return JsonResponse(stock_list, safe=False)


# View to fetch stocks based on different filter criteria
def get_stocks_by_all(request, filter_type):
    if filter_type == 'all':
        stocks = Stock.objects.filter(is_deleted=False)
    elif filter_type == 'all_active':
        stocks = Stock.objects.filter(is_deleted=False, status=True)
    elif filter_type == 'all_inactive':
        stocks = Stock.objects.filter(is_deleted=False, status=False)
    elif filter_type == 'all_stock_alert':
        stocks = Stock.objects.filter(is_deleted=False, status=True, quantity__lte=F('stock_alert'))
    else:
        # If no valid option is selected, initialize stocks to an empty queryset
        stocks = Stock.objects.none()

    stock_list = []
    for stock in stocks:
        stock_list.append({
            'id': stock.id,
            'name': stock.name,
            'quantity': stock.quantity,
            'status': stock.status,
            'stock_alert': stock.stock_alert,
            'category': (stock.safe_category.short_name or '') if stock.safe_category else '',
            'subcategory': (stock.safe_subcategory.short_name or '') if stock.safe_subcategory else '',
            'purchase': (stock.safe_purchase.short_name or '') if stock.safe_purchase else '',
        })
    return JsonResponse(stock_list, safe=False)

def get_stocks_by_filter(request, filter_type, category_id=None, subcategory_id=None):
    stocks = Stock.objects.filter(is_deleted=False)

    # Apply the filter based on the filter type
    if filter_type == 'select_all':
        pass
    elif filter_type == 'select_active':
        stocks = stocks.filter(status=True)
    elif filter_type == 'select_inactive':
        stocks = stocks.filter(status=False)
    elif filter_type == 'select_stock_alert':
        stocks = stocks.filter(status=True, quantity__lte=F('stock_alert'))

    # Filter by category if provided
    if category_id:
        stocks = stocks.filter(category_id=category_id)

    # Filter by subcategory if provided
    if subcategory_id:
        stocks = stocks.filter(subcategory_id=subcategory_id)

    # Prepare the stock list to return
    stock_list = [{
        'id': stock.id,
        'name': stock.name,
        'quantity': stock.quantity,
        'status': stock.status,
        'stock_alert': stock.stock_alert,
        'category': (stock.safe_category.short_name or '') if stock.safe_category else '',
        'subcategory': (stock.safe_subcategory.short_name or '') if stock.safe_subcategory else '',
        'purchase': (stock.safe_purchase.short_name or '') if stock.safe_purchase else '',
    } for stock in stocks]

    return JsonResponse(stock_list, safe=False)


class StockCreateView(SuccessMessageMixin,
                      CreateView):  # createview class to add new stock, mixin used to display message
    model = Stock  # setting 'Stock' model as model
    form_class = StockForm  # setting 'StockForm' form as form
    template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
    success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been created successfully"  # displays message when form is submitted

    def get_context_data(self, **kwargs):  # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        return context

#
# class StockUpdateView(SuccessMessageMixin, UpdateView):  # updateview class to edit stock, mixin used to display message
#     model = Stock  # setting 'Stock' model as model
#     form_class = StockForm  # setting 'StockForm' form as form
#     template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
#     success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
#     success_message = "Stock has been updated successfully"  # displays message when form is submitted
#
#     def get_context_data(self, **kwargs):  # used to send additional context
#         context = super().get_context_data(**kwargs)
#         context["title"] = 'Edit Stock'
#         context["savebtn"] = 'Update Stock'
#         context["delbtn"] = 'Delete Stock'
#         return context


class StockUpdateView(SuccessMessageMixin, UpdateView):  # updateview class to edit stock, mixin used to display message
    model = Stock  # setting 'Stock' model as model
    form_class = StockForm  # setting 'StockForm' form as form
    template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
    success_url = '/inventory'  # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been updated successfully"  # displays message when form is submitted

    def get_context_data(self, **kwargs):  # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Stock'
        context["savebtn"] = 'Update Stock'
        context["delbtn"] = 'Delete Stock'
        return context

    def form_valid(self, form):
        # Save the Stock form and get the stock instance
        stock = form.save()

        # Check if there's a related product and update its status
        if stock.product:
            # Update the related Product's status to match the Stock's status
            product = stock.product
            product.status = stock.status
            product.save()  # Save the updated product status

        return super().form_valid(form)  # Continue with the default form_valid logic


class StockDeleteView(View):  # view class to delete stock
    template_name = "delete_stock.html"  # 'delete_stock.html' used as the template
    success_message = "Stock has been deleted successfully"  # displays message when form is submitted

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

    @staticmethod
    def _format_bill_refs(items, bill_attr, party_attr):
        refs = []
        for item in items:
            bill_obj = getattr(item, bill_attr, None)
            if not bill_obj:
                continue

            bill_no = getattr(bill_obj, "billno", "")
            party_obj = getattr(bill_obj, party_attr, None)
            party_name = getattr(party_obj, "name", "") if party_obj else ""

            if party_name:
                refs.append(f"{bill_no} ({party_name})")
            else:
                refs.append(f"{bill_no}")

        return refs

    def _build_stock_usage_error(self, stock):
        purchase_items = (
            PurchaseItem.objects.filter(stock=stock)
            .select_related("billno__supplier")
            .order_by("billno__billno")
            .distinct()
        )
        sale_bill_items = (
            SaleItem.objects.filter(stock=stock)
            .select_related("billno__Cust_id", "billno__Vend_id")
            .order_by("billno__billno")
            .distinct()
        )
        final_sale_items = (
            FinalSaleItem.objects.filter(stock=stock)
            .select_related("final_bill__customer", "final_bill__vendor")
            .order_by("final_bill__billno")
            .distinct()
        )
        return_items = (
            ReturnSaleItem.objects.filter(stock=stock)
            .select_related("return_bill__customer", "return_bill__vendor")
            .order_by("return_bill__billno")
            .distinct()
        )
        serial_items = (
            PurchaseSerial.objects.filter(stock=stock)
            .select_related(
                "billno__supplier",
                "sales_billno__Cust_id",
                "sales_billno__Vend_id",
                "final_salebill__customer",
                "final_salebill__vendor",
                "return_bill__customer",
                "return_bill__vendor",
            )
            .order_by("billno__billno")
            .distinct()
        )

        purchase_refs = self._format_bill_refs(purchase_items, "billno", "supplier")
        sale_bill_refs = []
        for item in sale_bill_items:
            sale_bill = item.billno
            if not sale_bill:
                continue
            party = sale_bill.Cust_id or sale_bill.Vend_id
            if party:
                party_name = self._party_display_name(party)
                sale_bill_refs.append(f"{sale_bill.billno} ({party_name})" if party_name else f"{sale_bill.billno}")
            else:
                sale_bill_refs.append(f"{sale_bill.billno}")

        final_sale_refs = []
        for item in final_sale_items:
            final_bill = item.final_bill
            if not final_bill:
                continue
            party = final_bill.customer or final_bill.vendor
            if party:
                party_name = self._party_display_name(party)
                final_sale_refs.append(f"{final_bill.billno} ({party_name})" if party_name else f"{final_bill.billno}")
            else:
                final_sale_refs.append(f"{final_bill.billno}")

        return_refs = []
        for item in return_items:
            return_bill = item.return_bill
            if not return_bill:
                continue
            party = return_bill.customer or return_bill.vendor
            if party:
                party_name = self._party_display_name(party)
                return_refs.append(f"{return_bill.billno} ({party_name})" if party_name else f"{return_bill.billno}")
            else:
                return_refs.append(f"{return_bill.billno}")

        serial_sale_refs = []
        serial_final_refs = []
        serial_return_refs = []
        for serial in serial_items:
            if serial.sales_billno_id:
                cust = serial.sales_billno.Cust_id or serial.sales_billno.Vend_id
                cust_name = self._party_display_name(cust)
                serial_sale_refs.append(
                    f"{serial.sales_billno.billno} ({cust_name})" if cust_name else f"{serial.sales_billno.billno}"
                )
            if serial.final_salebill_id:
                party = serial.final_salebill.customer or serial.final_salebill.vendor
                party_name = self._party_display_name(party)
                serial_final_refs.append(
                    f"{serial.final_salebill.billno} ({party_name})" if party_name else f"{serial.final_salebill.billno}"
                )
            if serial.return_bill_id:
                party = serial.return_bill.customer or serial.return_bill.vendor
                party_name = self._party_display_name(party)
                serial_return_refs.append(
                    f"{serial.return_bill.billno} ({party_name})" if party_name else f"{serial.return_bill.billno}"
                )

        sale_refs = list(dict.fromkeys(sale_bill_refs + final_sale_refs + serial_sale_refs + serial_final_refs))
        return_refs = list(dict.fromkeys(return_refs + serial_return_refs))
        purchase_refs = list(dict.fromkeys(purchase_refs))

        if not (purchase_refs or sale_refs or return_refs):
            return ""

        usage_parts = []
        if purchase_refs:
            usage_parts.append(f"Purchase Bills: {', '.join(purchase_refs)}")
        if sale_refs:
            usage_parts.append(f"Sale Bills: {', '.join(sale_refs)}")
        if return_refs:
            usage_parts.append(f"Return Bills: {', '.join(return_refs)}")

        return "\n".join(
            [
                f'Cannot delete stock "{stock.name}".',
                "This stock is already used in the following bills:",
                *usage_parts,
                "Please use Stock Active/Deactive only.",
            ]
        )

    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        usage_error = self._build_stock_usage_error(stock)
        if usage_error:
            messages.error(request, usage_error)
            return redirect('inventory')
        return render(request, self.template_name, {'object': stock})

    def post(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        usage_error = self._build_stock_usage_error(stock)
        if usage_error:
            messages.error(request, usage_error)
            return redirect('inventory')

        stock.is_deleted = True
        stock.save()
        messages.success(request, self.success_message)
        return redirect('inventory')

#
# def create_favorite_list(request):
#     favorite_list_name = request.POST.get('favorite_list_name')
#     selected_stocks = request.POST.getlist('selected_stocks[]')
#
#     # Create or update the favorite list
#     favorite_list, created = FavoriteList.objects.get_or_create(name=favorite_list_name)
#
#     # Update the stocks associated with the favorite list
#     favorite_list.stocks.clear()
#     favorite_list.stocks.add(*selected_stocks)
#     favorite_list.save()
#
#     return JsonResponse({'message': 'Favorite list created successfully!'})


from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import Stock, FavoriteList
from django.db import IntegrityError

# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from .models import Stock, FavoriteList
#
#
# @require_POST
# def create_favorite_list(request):
#     favorite_list_name = request.POST.get('favorite_list_name')
#     selected_stocks = request.POST.getlist('selected_stocks[]')
#
#     # Create or update the favorite list
#     favorite_list, created = FavoriteList.objects.get_or_create(name=favorite_list_name)
#
#     # Update the stocks associated with the favorite list
#     favorite_list.stocks.clear()
#     favorite_list.stocks.add(*selected_stocks)
#     favorite_list.save()
#
#     return JsonResponse({'message': 'Favorite list created successfully!'})

#
# from django.http import JsonResponse, HttpResponseRedirect
# from django.views.generic import ListView
# from .models import FavoriteList
# from django.shortcuts import get_object_or_404
#
#
# class StockListView1(ListView):
#     model = Stock
#     template_name = 'favorite.html'
#     paginate_by = 10
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.active_only()
#         context['subcategories'] = SubCategory.objects.active_only()
#         return context
#
#     # View to fetch stocks based on different filter criteria
#     def get_stocks_by_all(request, filter_type):
#         if filter_type == 'all':
#             stocks = Stock.objects.filter(is_deleted=False)
#         elif filter_type == 'all_active':
#             stocks = Stock.objects.filter(is_deleted=False, status=True)
#         elif filter_type == 'all_inactive':
#             stocks = Stock.objects.filter(is_deleted=False, status=False)
#         elif filter_type == 'all_stock_alert':
#             stocks = Stock.objects.filter(is_deleted=False, status=True, quantity__lte=F('stock_alert'))
#         else:
#             # If no valid option is selected, initialize stocks to an empty queryset
#             stocks = Stock.objects.none()
#
#         stock_list = []
#         for stock in stocks:
#             stock_list.append({
#                 'id': stock.id,
#                 'name': stock.name,
#                 'quantity': stock.quantity,
#                 'status': stock.status,
#                 'stock_alert': stock.stock_alert,
#                 'category': stock.category.short_name,
#                 'subcategory': stock.subcategory.short_name,
#                 'purchase': stock.purchase.short_name,
#             })
#         return JsonResponse(stock_list, safe=False)
#
#
# # Create favorite list view
# def create_favorite_list(request):
#     if request.method == 'POST':
#         list_name = request.POST.get('list_name', 'New Favorite List')
#         selected_stock_ids = request.POST.getlist('selected_stocks[]')
#
#         # Create a new FavoriteList instance
#         favorite_list = FavoriteList.objects.create(name=list_name)
#
#         # Add selected stocks to the favorite list
#         for stock_id in selected_stock_ids:
#             stock = get_object_or_404(Stock, id=stock_id)
#             favorite_list.stocks.add(stock)
#
#         return JsonResponse({'message': 'Favorite list created successfully', 'list_name': favorite_list.name})
#     return JsonResponse({'error': 'Invalid request'}, status=400)
#


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Stock, FavoriteList


# @csrf_exempt
# def create_favorite_list(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         list_name = data.get('name')
#         stock_ids = [stock['id'] for stock in data.get('stocks', [])]
#
#         favorite_list = FavoriteList.objects.create(name=list_name)
#         favorite_list.stocks.set(Stock.objects.filter(id__in=stock_ids))
#
#         return JsonResponse({'message': 'Favorite list created successfully'})

@csrf_exempt
def create_favorite_list(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        list_name = data.get('name')
        stock_ids = [stock['id'] for stock in data.get('stocks', [])]

        # Check if a FavoriteList with the same name already exists
        # if FavoriteList.objects.filter(name=list_name).exists():
        if FavoriteList.objects.filter(name__iexact=list_name).exists():
            return JsonResponse({'message': 'Favorite list with this name already exists.'}, status=400)

        favorite_list = FavoriteList.objects.create(name=list_name)
        favorite_list.stocks.set(Stock.objects.filter(id__in=stock_ids))

        return JsonResponse({'message': 'Favorite list created successfully'})


# Update context to pass CSRF token and stock data
class StockListView1(ListView):
    model = Stock
    template_name = 'favorite.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.active_only().order_by("name", "id")
        return context


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def create_favorite_list(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        stocks = data.get('stocks', [])

        if FavoriteList.objects.filter(name=name).exists():
            return JsonResponse({'message': f'Favorite list "{name}" already exists.'})

        favorite_list = FavoriteList.objects.create(name=name)

        for stock_data in stocks:
            stock_id = stock_data.get('id')
            quantity = stock_data.get('quantity', 1)

            stock = Stock.objects.get(id=stock_id)
            # Create a record in through model with quantity
            FavoriteListStock.objects.create(
                favorite_list=favorite_list,
                stock=stock,
                quantity=quantity
            )

        return JsonResponse({'message': 'Favorite list created successfully.'})


# @require_GET
# def get_stocks_all(request):
#     # stocks = Stock.objects.all().values('id', 'name', 'quantity', 'status', 'category__short_name')
#     # stocks_data = list(stocks)
#     # return JsonResponse(stocks_data, safe=False)
#     category_id = request.GET.get('category_id')
#     subcategory_id = request.GET.get('subcategory_id')
#
#     stocks = Stock.objects.all()
#     if category_id:
#         stocks = stocks.filter(category_id=category_id)
#     if subcategory_id:
#         stocks = stocks.filter(subcategory_id=subcategory_id)
#
#     stocks_data = [
#         {
#             'id': stock.id,
#             'category': stock.category.name,
#             'subcategory': stock.subcategory.name,
#             'name': stock.name,
#             'quantity': stock.quantity,
#             'status': stock.status,
#         }
#         for stock in stocks
#     ]
#     return JsonResponse(stocks_data, safe=False)
#
# # Fetch subcategories based on category ID
# def get_subcategories(request, category_id):
#     subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
#     return JsonResponse({'subcategories': list(subcategories)})


# def get_stocks_all(request):
#     category_id = request.GET.get('category_id')
#     subcategory_id = request.GET.get('subcategory_id')
#
#     stocks = Stock.objects.all()
#     if category_id:
#         stocks = stocks.filter(category_id=category_id)
#     if subcategory_id:
#         stocks = stocks.filter(subcategory_id=subcategory_id)
#
#     stocks_data = [
#         {
#             'id': stock.id,
#             'category': stock.category.name,
#             'subcategory': stock.subcategory.name,
#             'name': stock.name,
#             'quantity': stock.quantity,
#             'status': stock.status,
#         }
#         for stock in stocks
#     ]
#     return JsonResponse(stocks_data, safe=False)
#
# @require_GET
# def get_stocks_all(request):
#     category_id = request.GET.get('category_id')
#     subcategory_id = request.GET.get('subcategory_id')
#
#     stocks = Stock.objects.all()
#     if category_id and category_id != 'all':
#         stocks = stocks.filter(category_id=category_id)
#     if subcategory_id and subcategory_id != 'all':
#         stocks = stocks.filter(subcategory_id=subcategory_id)
#
#     stocks_data = [
#         {
#             'id': stock.id,
#             'category': stock.category.name,
#             'subcategory': stock.subcategory.name,
#             'name': stock.name,
#             'quantity': stock.quantity,
#             'status': stock.status,
#         }
#         for stock in stocks
#     ]
#     return JsonResponse(stocks_data, safe=False)


@require_GET
def get_stocks_all(request):
    category_id = request.GET.get('category_id')
    subcategory_id = request.GET.get('subcategory_id')

    # Filter stocks where is_deleted is False
    stocks = Stock.objects.filter(is_deleted=False, status=True).distinct()

    if category_id and category_id != 'all':
        stocks = stocks.filter(category_id=category_id)
    if subcategory_id and subcategory_id != 'all':
        stocks = stocks.filter(subcategory_id=subcategory_id)

    stocks_data = [
        {
            'id': stock.id,
            'category': stock.safe_category.name if stock.safe_category else '',
            'subcategory': stock.safe_subcategory.name if stock.safe_subcategory else '',
            'name': stock.name,
            'quantity': stock.quantity,
            'sales_unit': stock.safe_sales.short_name if stock.safe_sales else '',
            'status': stock.status,
        }
        for stock in stocks
    ]
    return JsonResponse(stocks_data, safe=False)





@require_GET
def get_subcategories1(request):
    category_id = request.GET.get("category_id")
    qs = SubCategory.objects.active_only().order_by("name", "id")
    if category_id and str(category_id) != "all":
        qs = qs.filter(category_id=category_id)
    subcategory_data = [{"id": subcat.id, "name": subcat.name} for subcat in qs]
    return JsonResponse(subcategory_data, safe=False)


# Add this to your StockListView or create a new view for these endpoints
def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

# @require_GET
# def get_subcategories(request):
#     category_id = request.GET.get('category_id')
#     subcategories = SubCategory.objects.filter(category_id=category_id)
#     subcategory_data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
#     return JsonResponse(subcategory_data, safe=False)



from django.shortcuts import render
from .models import FavoriteList, Stock, FavoriteListStock
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce


# View to display all favorite lists and their associated stock
class FavoriteListView(ListView):
    model = FavoriteList
    template_name = 'favorite_list.html'

    def get_queryset(self):
        # Subquery avoids PostgreSQL GROUP BY errors from Count() + join on this schema.
        stock_cnt = (
            FavoriteListStock.objects.filter(favorite_list_id=OuterRef('pk'))
            .values('favorite_list_id')
            .annotate(_n=Count('id'))
            .values('_n')[:1]
        )
        return (
            FavoriteList.objects.annotate(
                stock_count=Coalesce(Subquery(stock_cnt, output_field=IntegerField()), 0)
            )
            .order_by('-created_at', '-id')
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


from django.http import JsonResponse
from .models import FavoriteList
#
# @require_GET
# def favorite_list_details(request, favorite_list_id):
#     try:
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#         stocks = favorite_list.stocks.values('name', 'quantity', 'sales__short_name')  # Only return stock names
#         return JsonResponse({
#             'name': favorite_list.name,
#             'stocks': list(stocks)
#         })
#     except FavoriteList.DoesNotExist:
#         return JsonResponse({'message': 'Favorite list not found.'}, status=404)


@require_GET
def favorite_list_details(request, favorite_list_id):
    try:
        favorite_list = FavoriteList.objects.get(id=favorite_list_id)

        # ✅ Use through table to access quantity
        stocks = FavoriteListStock.objects.filter(favorite_list=favorite_list).values(
            'stock__name',
            'quantity',
            'stock__sales__short_name'
        )

        return JsonResponse({
            'name': favorite_list.name,
            'stocks': list(stocks)
        })
    except FavoriteList.DoesNotExist:
        return JsonResponse({'message': 'Favorite list not found.'}, status=404)

# def get_favorite_list(request):
#     favorite_list_id = request.GET.get('favorite_list_id')
#     try:
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#         data = {
#             'name': favorite_list.name,
#             'stocks': [
#                 {'id': stock.id, 'name': stock.name, 'category': stock.category.name, 'subcategory': stock.subcategory.name}
#                 for stock in favorite_list.stocks.all()
#             ]
#         }
#         return JsonResponse(data)
#     except FavoriteList.DoesNotExist:
#         return JsonResponse({'error': 'Favorite list not found'}, status=404)


# from django.http import JsonResponse
# from .models import FavoriteList, Stock
#
#
# @csrf_exempt
# def get_favorite_stock_list(request, favorite_list_id):
#     stocks = FavoriteList.objects.filter(favorite_list_id=favorite_list_id)
#     stock_data = [{
#         'id': stock.id,
#         'name': stock.name,
#         'category': stock.category.name,
#         'subcategory': stock.subcategory.name,
#     } for stock in stocks]
#     return JsonResponse(stock_data, safe=False)
#
#
# @csrf_exempt
# def update_favorite_stock_list(request, favorite_list_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         selected_stocks = data.get('stocks', [])
#         # Assuming FavoriteStockList is a model for storing favorite stocks
#         favorite_list = FavoriteStockList.objects.get(id=favorite_list_id)
#
#         # Clear the existing favorite list and add the selected stocks
#         favorite_list.stocks.clear()
#         for stock in selected_stocks:
#             stock_instance = Stock.objects.get(id=stock['id'])
#             favorite_list.stocks.add(stock_instance)
#
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import FavoriteList, Stock
import json


# # def edit_favorite_list(request, favorite_id):
# def edit_favorite_list(request, favorite_id):
#         favorite_list = get_object_or_404(FavoriteList, id=favorite_id)
#
#         # If POST, update favorite list
#         if request.method == 'POST':
#             # Retrieve stock IDs from form data
#             stock_ids = request.POST.getlist('stock_ids[]')
#
#             # Get Stock objects corresponding to these IDs
#             selected_stocks = Stock.objects.filter(id__in=stock_ids)
#
#             # Update the FavoriteList stocks with the selected stocks
#             favorite_list.stocks.set(selected_stocks)
#
#             # Save changes to the database
#             favorite_list.save()
#
#             # Redirect to some confirmation or success page
#             return redirect('favorite_list_view')  # Replace with the appropriate URL name
#
#         # If GET, render the page with existing stocks
#         existing_stocks = favorite_list.stocks.all()
#         all_stocks = Stock.objects.exclude(id__in=existing_stocks.values_list('id', flat=True))
#
#         context = {
#             'favorite_records': existing_stocks,
#             'stock_options': all_stocks,
#             'favorite_list': favorite_list,
#         }
#         return render(request, 'edit_favorite.html', context)



# from django.shortcuts import render, get_object_or_404, redirect
# from .models import FavoriteList, Stock, Category, SubCategory
#
# def edit_favorite_list(request, favorite_id):
#     favorite_list = get_object_or_404(FavoriteList, id=favorite_id)
#
#     if request.method == 'POST':
#         stock_ids = request.POST.getlist('stock_ids[]')
#         selected_stocks = Stock.objects.filter(id__in=stock_ids)
#         favorite_list.stocks.set(selected_stocks)
#         favorite_list.save()
#         return redirect('favorite_list_view')
#
#     existing_stocks = favorite_list.stocks.select_related('category', 'subcategory').all()
#     all_stocks = Stock.objects.exclude(id__in=existing_stocks.values_list('id', flat=True)).select_related('category', 'subcategory')
#
#     context = {
#         'favorite_records': existing_stocks,
#         'stock_options': all_stocks,
#         'favorite_list': favorite_list,
#     }
#     return render(request, 'edit_favorite.html', context)
#


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import FavoriteList, Stock, Category, SubCategory, FavoriteListStock

def edit_favorite_list(request, favorite_id):
    favorite_list = get_object_or_404(FavoriteList, id=favorite_id)

    # if request.method == 'POST':
    #     stock_ids = request.POST.getlist('stock_ids[]')
    #     selected_stocks = Stock.objects.filter(id__in=stock_ids)
    #     favorite_list.stocks.set(selected_stocks)
    #     favorite_list.save()
    #     # messages.success(request, "FavoriteList Records saved successfully!")
    #     return redirect('favorite_list_view')
    if request.method == 'POST':
        stock_ids = request.POST.getlist('stock_ids[]')
        quantities = request.POST.getlist('quantities[]')
        save_action = (request.POST.get('save_action') or 'update').strip()

        if save_action == 'save_as':
            new_name = (request.POST.get('new_list_name') or '').strip()
            if not new_name:
                messages.error(request, 'Please enter a name for the new favorite list.')
                return redirect('edit_favorite_list', favorite_id=favorite_id)
            if FavoriteList.objects.filter(name=new_name).exists():
                messages.error(
                    request,
                    'A favorite list with that name already exists. Choose a different name.',
                )
                return redirect('edit_favorite_list', favorite_id=favorite_id)
            new_list = FavoriteList.objects.create(name=new_name)
            for stock_id, qty in zip(stock_ids, quantities):
                stock = Stock.objects.get(id=stock_id)
                FavoriteListStock.objects.create(
                    favorite_list=new_list,
                    stock=stock,
                    quantity=int(qty),
                )
            messages.success(
                request,
                f'New list "{new_name}" was saved. The original list "{favorite_list.name}" was not changed.',
            )
            return redirect('favorite_list_view')

        # Default: update current list in place
        FavoriteListStock.objects.filter(favorite_list=favorite_list).delete()

        for stock_id, qty in zip(stock_ids, quantities):
            stock = Stock.objects.get(id=stock_id)
            FavoriteListStock.objects.create(
                favorite_list=favorite_list,
                stock=stock,
                quantity=int(qty)
            )

        messages.success(request, f'"{favorite_list.name}" was updated successfully.')
        return redirect('favorite_list_view')

    # existing_stocks = favorite_list.stocks.select_related('category', 'subcategory').all()
    existing_stocks = (
        FavoriteListStock.objects.filter(favorite_list=favorite_list)
        .select_related("stock")
        .order_by("stock__name", "id")
    )

    all_categories = Category.objects.all()
    all_subcategories = SubCategory.objects.all()
    all_stocks = Stock.objects.all()

    context = {
        'favorite_records': existing_stocks,
        'categories': all_categories,
        'subcategories': all_subcategories,
        'stocks': all_stocks,
        'favorite_list': favorite_list,
    }
    return render(request, 'edit_favorite.html', context)


def get_subcategories_edit(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})

def get_stocks_edit(request):
    subcategory_id = request.GET.get('subcategory_id')
    # stocks = Stock.objects.filter(subcategory_id=subcategory_id).values('id', 'name')
    # stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False).values('id', 'name')
    stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False, status=True).values(
        'id',
        'name',
        'gst',
        'sales__short_name',
    )
    return JsonResponse({'stocks': list(stocks)})

# def get_stocks_edit(request):
#     subcategory_id = request.GET.get('subcategory_id')
#     stocks = Stock.objects.filter(subcategory_id=subcategory_id, is_deleted=False, status=True)
#     stocks_data = []
#     for stock in stocks:
#         stocks_data.append({
#             'id': stock.id,
#             'name': stock.name,
#             'gst': stock.gst if stock.gst is not None else 0.0,  # Default to 0 if None
#             # Include other fields as needed
#         })
#     return JsonResponse({'stocks': stocks_data})
#
# def get_stock_quantity(request):
#     stock_id = request.GET.get('stock_id')
#     stock = Stock.objects.get(id=stock_id)
#     return JsonResponse({'quantity': stock.quantity})


def get_stock_quantity(request):
    stock_id = request.GET.get('stock_id')
    stock = Stock.objects.filter(id=stock_id).first()
    if stock:
        return JsonResponse({
            'quantity': stock.quantity,
            'stock_alert': stock.stock_alert,
            'purchase': stock.purchase.short_name,
        })
    return JsonResponse({'error': 'Stock not found'}, status=404)

def get_stock_detail(request):
    stock_id = request.GET.get('stock_id')
    try:
        stock = Stock.objects.get(pk=stock_id, is_deleted=False, status=True)
        data = {
            'stock': {
                'id': stock.id,
                'name': stock.name,
                'quantity': stock.quantity,
            }
        }
        return JsonResponse(data)
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)
#
# def edit_favorite_list(request, favorite_list_id):
#     # Fetch the favorite stock list for the given ID
#     favorite_list = get_object_or_404(FavoriteList, id=favorite_list_id)
#
#     # Fetch the stocks related to this favorite list
#     stocks = favorite_list.stocks.all()
#
#     # Prepare the data to pass to the template
#     stock_data = [{
#         'id': stock.id,
#         'name': stock.name,
#         'category': stock.category.name,
#         'subcategory': stock.subcategory.name,
#     } for stock in stocks]
#
#     return render(request, 'edit_favorite.html', {
#         'favorite_list': favorite_list,
#         'stock_data': stock_data
#     })

#
# def update_favorite_stock_list(request, favorite_list_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         selected_stocks = data.get('stocks', [])
#
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#         favorite_list.stocks.clear()
#
#         # Add the selected stocks to the favorite list
#         for stock in selected_stocks:
#             stock_instance = Stock.objects.get(id=stock['id'])
#             favorite_list.stocks.add(stock_instance)
#
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False})

# def update_favorite_stock_list(request, favorite_list_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         stocks_to_add = data.get('stocks_to_add', [])
#         stocks_to_remove = data.get('stocks_to_remove', [])
#
#         favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#
#         # Remove stocks
#         for stock_id in stocks_to_remove:
#             stock = Stock.objects.get(id=stock_id)
#             favorite_list.stocks.remove(stock)
#
#         # Add new stocks
#         for stock_data in stocks_to_add:
#             stock = Stock.objects.get(id=stock_data['id'])
#             favorite_list.stocks.add(stock)
#
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False})
#
# from django.http import JsonResponse
# from .models import FavoriteList, Stock
#
# from django.http import JsonResponse
# from .models import FavoriteList, Stock
#
# def remove_stock_from_favorite_list(request, favorite_list_id, stock_id):
#     if request.method == 'POST':
#         try:
#             # Retrieve the specific favorite list by ID
#             favorite_list = FavoriteList.objects.get(id=favorite_list_id)
#
#             # Find the stock and remove it from the list
#             stock = Stock.objects.get(id=stock_id)
#             favorite_list.stocks.remove(stock)
#
#             return JsonResponse({'success': True})
#         except FavoriteList.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Favorite list not found.'})
#         except Stock.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Stock not found.'})
#     return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def delete_favorite_list(request, favorite_list_id):
    try:
        favorite_list = FavoriteList.objects.get(id=favorite_list_id)
        favorite_list.delete()
        return JsonResponse({'message': 'Favorite list deleted successfully.'})
    except FavoriteList.DoesNotExist:
        return JsonResponse({'message': 'Favorite list not found.'}, status=404)
