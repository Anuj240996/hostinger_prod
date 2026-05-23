# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count, Sum, Avg, Q
# from django.utils import timezone
# from datetime import timedelta, datetime
# from calendar import monthrange
#
# from apps.leads.models import Lead, LeadActivity
# from apps.revenue.models import Revenue
# from django.contrib.auth.models import User
#
#
# @login_required
# def sales_team_dashboard(request):
#     """
#     Sales team leaderboard and performance metrics
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=monthrange(today.year, today.month)[1])
#
#     # Team performance by revenue
#     team_by_revenue = []
#     team_by_conversion = []
#     team_by_activity = []
#     individual_performance = []
#
#     for user in User.objects.filter(is_active=True).order_by('first_name'):
#         leads = Lead.objects.filter(assigned_to=user)
#         total_leads = leads.count()
#         won_leads = leads.filter(stage='won').count()
#         lost_leads = leads.filter(stage='lost').count()
#         qualified = leads.filter(stage__in=['qualified', 'survey', 'quote', 'negotiation']).count()
#
#         # Revenue
#         revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=first_day_month,
#             date__lte=last_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         # Activities
#         activities = LeadActivity.objects.filter(user=user)
#         calls = activities.filter(activity_type='call').count()
#         whatsapp = activities.filter(activity_type='whatsapp').count()
#         emails = activities.filter(activity_type='email').count()
#         followups = activities.filter(activity_type='followup').count()
#
#         # Follow-up compliance (last 30 days)
#         last_30_days = today - timedelta(days=30)
#         scheduled_followups = activities.filter(
#             activity_type='followup',
#             created__date__gte=last_30_days
#         ).count()
#
#         # Performance metrics
#         conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
#         avg_deal_size = revenue / won_leads if won_leads > 0 else 0
#
#         # Trend (compare with last month)
#         last_month = first_day_month - timedelta(days=1)
#         last_month_first = last_month.replace(day=1)
#         last_month_revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=last_month_first,
#             date__lt=first_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         trend = ((revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
#
#         # Target achievement
#         target = 1000000  # ₹10 lakhs target
#         achievement = (revenue / target * 100) if target > 0 else 0
#
#         user_data = {
#             'id': user.id,
#             'name': user.get_full_name() or user.username,
#             'email': user.email,
#             'initials': ''.join([n[0] for n in (user.get_full_name() or user.username).split()[:2]]).upper(),
#             'leads_assigned': total_leads,
#             'leads': total_leads,
#             'qualified': qualified,
#             'won': won_leads,
#             'lost': lost_leads,
#             'conversion_rate': round(conversion_rate, 1),
#             'revenue': revenue,
#             'avg_deal_size': round(avg_deal_size, 2),
#             'trend': round(trend, 1),
#             'calls': calls,
#             'whatsapp': whatsapp,
#             'emails': emails,
#             'followups': followups,
#             'total_activities': activities.count(),
#             'avg_per_day': round(activities.count() / 30, 1),
#             'followup_compliance': 85,  # Calculate from actual data
#             'achievement': round(achievement, 1),
#         }
#
#         team_by_revenue.append(user_data)
#         individual_performance.append(user_data)
#
#     # Sort by revenue for leaderboard
#     team_by_revenue.sort(key=lambda x: x['revenue'], reverse=True)
#     team_by_conversion.sort(key=lambda x: x['conversion_rate'], reverse=True)
#     team_by_activity.sort(key=lambda x: x['total_activities'], reverse=True)
#
#     # Top performers
#     top_closer = team_by_revenue[0] if team_by_revenue else {'name': 'N/A', 'revenue': 0}
#     fastest_closer = {'name': 'N/A', 'days': 0}  # Calculate from actual data
#     followup_king = team_by_activity[0] if team_by_activity else {'name': 'N/A', 'total_activities': 0}
#
#     context = {
#         'team_by_revenue': team_by_revenue[:10],
#         'team_by_conversion': team_by_conversion[:10],
#         'team_by_activity': team_by_activity[:10],
#         'individual_performance': individual_performance[:6],
#         'top_closer': top_closer,
#         'fastest_closer': fastest_closer,
#         'followup_king': followup_king,
#     }
#
#     return render(request, 'team/sales_team.html', context)
#
#
# @login_required
# def sales_rep_detail(request, pk):
#     """
#     Detailed view for individual sales rep
#     """
#     user = get_object_or_404(User, pk=pk)
#
#     # Get performance data
#     leads = Lead.objects.filter(assigned_to=user)
#     won_leads = leads.filter(stage='won')
#
#     # Recent activities
#     recent_activities = LeadActivity.objects.filter(user=user).select_related('lead')[:20]
#
#     # Monthly performance
#     today = timezone.now().date()
#     months = []
#     revenue_data = []
#     for i in range(6):
#         month = today.replace(day=1) - timedelta(days=30 * i)
#         month_start = month.replace(day=1)
#         month_end = month.replace(day=monthrange(month.year, month.month)[1])
#
#         months.append(month.strftime('%b %Y'))
#         month_revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=month_start,
#             date__lte=month_end,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#         revenue_data.append(float(month_revenue))
#
#     context = {
#         'rep': user,
#         'total_leads': leads.count(),
#         'won_leads': won_leads.count(),
#         'total_revenue': revenue_data[0] if revenue_data else 0,
#         'recent_activities': recent_activities,
#         'months': months[::-1],
#         'revenue_data': revenue_data[::-1],
#     }
#
#     return render(request, 'team/sales_rep_detail.html', context)
#
# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count, Sum, Avg, Q
# from django.utils import timezone
# from datetime import timedelta
#
# from django.contrib.auth.models import User
#
#
# @login_required
# def sales_team_dashboard(request):
#     """
#     Sales team leaderboard and performance metrics
#     """
#     # Sample data for demonstration
#     team_by_revenue = []
#     team_by_conversion = []
#     team_by_activity = []
#     individual_performance = []
#
#     # Get all active users (in a real app, you'd filter by sales team group)
#     users = User.objects.filter(is_active=True)[:5]  # Limit to 5 for demo
#
#     for i, user in enumerate(users):
#         # Sample data
#         rep_data = {
#             'id': user.id,
#             'name': user.get_full_name() or user.username,
#             'email': user.email,
#             'initials': ''.join([n[0] for n in (user.get_full_name() or user.username).split()[:2]]).upper(),
#             'leads_assigned': 10 + i,
#             'leads': 10 + i,
#             'qualified': 5 + i,
#             'won': 3 + i,
#             'lost': 2,
#             'conversion_rate': 30 + i * 5,
#             'revenue': 100000 + i * 50000,
#             'avg_deal_size': 33000 + i * 5000,
#             'trend': 5 + i,
#             'calls': 20 + i * 5,
#             'whatsapp': 15 + i * 3,
#             'emails': 10 + i * 2,
#             'followups': 8 + i,
#             'total_activities': 53 + i * 11,
#             'avg_per_day': 2 + i,
#             'followup_compliance': 80 + i,
#             'achievement': 70 + i * 5,
#             'followup_percentage': 75 + i,
#         }
#
#         team_by_revenue.append(rep_data)
#         individual_performance.append(rep_data)
#
#     # Sort for different views
#     team_by_conversion = sorted(team_by_revenue, key=lambda x: x['conversion_rate'], reverse=True)
#     team_by_activity = sorted(team_by_revenue, key=lambda x: x['total_activities'], reverse=True)
#     team_by_revenue = sorted(team_by_revenue, key=lambda x: x['revenue'], reverse=True)
#
#     # Top performers
#     top_closer = team_by_revenue[0] if team_by_revenue else {'name': 'N/A', 'revenue': 0}
#     fastest_closer = {'name': 'John Doe', 'days': 15}
#     followup_king = team_by_activity[0] if team_by_activity else {'name': 'N/A', 'count': 0}
#
#     context = {
#         'team_by_revenue': team_by_revenue,
#         'team_by_conversion': team_by_conversion,
#         'team_by_activity': team_by_activity,
#         'individual_performance': individual_performance,
#         'top_closer': top_closer,
#         'fastest_closer': fastest_closer,
#         'followup_king': followup_king,
#     }
#
#     return render(request, 'team/sales_team.html', context)
#
#
# @login_required
# def sales_rep_detail(request, pk):
#     """
#     Detailed view for individual sales rep
#     """
#     user = get_object_or_404(User, pk=pk)
#
#     context = {
#         'rep': user,
#         'total_leads': 15,
#         'won_leads': 8,
#         'total_revenue': 450000,
#         'recent_activities': [],
#         'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
#         'revenue_data': [50000, 75000, 100000, 85000, 120000, 95000],
#     }
#
#     return render(request, 'team/sales_rep_detail.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from calendar import monthrange
from apps.leads.models import Lead, LeadActivity, FollowUp
from django.contrib.auth.models import User
from apps.leads.models import Lead, LeadActivity, FollowUp
from apps.revenue.models import Revenue


from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from apps.team.permissions import OrganizationAdminRequiredMixin
from apps.team.forms import UserCreationForm
from apps.team.services import user_service

# class UserCreateView(OrganizationAdminRequiredMixin, FormView):
#     template_name = 'team/user_form.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('team:user_list')  # you'll need a user list view
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['organization'] = self.request.organization
#         return kwargs
#
#     def form_valid(self, form):
#         # Gather data
#         user_data = {
#             'first_name': form.cleaned_data['first_name'],
#             'last_name': form.cleaned_data['last_name'],
#             'email': form.cleaned_data['email'],
#             'phone': form.cleaned_data.get('phone', ''),
#             'title': form.cleaned_data.get('title', ''),
#             'department': form.cleaned_data.get('department', ''),
#             'is_active': form.cleaned_data.get('is_active', True),
#         }
#         role = form.cleaned_data['role']
#         send_email = form.cleaned_data.get('send_welcome_email', False)
#         manual_password = None
#         if form.cleaned_data['password_option'] == 'manual':
#             manual_password = form.cleaned_data['password']
#
#         try:
#             user_service.create_organization_user(
#                 organization=self.request.organization,
#                 created_by=self.request.user,
#                 user_data=user_data,
#                 role=role,
#                 send_email=send_email,
#                 manual_password=manual_password
#             )
#             messages.success(self.request, 'User created successfully.')
#         except Exception as e:
#             messages.error(self.request, f'Error creating user: {str(e)}')
#             return self.form_invalid(form)
#
#         return super().form_valid(form)
#
# from django.views.generic import ListView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from apps.core.models import UserProfile
# from .permissions import OrganizationAdminRequiredMixin
#
# class UserListView(LoginRequiredMixin, OrganizationAdminRequiredMixin, ListView):
#     model = UserProfile
#     template_name = 'team/user_list.html'
#     context_object_name = 'users'
#
#     def get_queryset(self):
#         return UserProfile.objects.filter(
#             organization=self.request.organization
#         ).select_related('user')  # ✅ correct relation

from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from apps.core.models import UserProfile
from .permissions import OrganizationAdminRequiredMixin
from .forms import UserCreationForm
from .services import user_service
from ..control_panel.models import Role


# class UserListView(OrganizationAdminRequiredMixin, ListView):
#     model = UserProfile
#     template_name = 'team/user_list.html'
#     context_object_name = 'users'
#
#     def get_queryset(self):
#         return UserProfile.objects.filter(
#             organization=self.request.organization
#         ).select_related('user')
#

#
# class UserCreateView(OrganizationAdminRequiredMixin, FormView):
#     template_name = 'team/user_form.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('user_list')
#
#     def dispatch(self, request, *args, **kwargs):
#         # Check if there are any roles for this organization
#         if not Role.objects.filter(organization=request.organization).exists():
#             messages.warning(request, "You need to create at least one role before adding users.")
#             return redirect('team:user_list')  # or redirect to role creation page
#         return super().dispatch(request, *args, **kwargs)

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['organization'] = self.request.organization
#         return kwargs
#
#     def form_valid(self, form):
#         user_data = {
#             'first_name': form.cleaned_data['first_name'],
#             'last_name': form.cleaned_data['last_name'],
#             'email': form.cleaned_data['email'],
#             'phone': form.cleaned_data.get('phone', ''),
#             'title': form.cleaned_data.get('title', ''),
#             'department': form.cleaned_data.get('department', ''),
#             'is_active': form.cleaned_data.get('is_active', True),
#         }
#         role = form.cleaned_data['role']
#         send_email = form.cleaned_data.get('send_welcome_email', False)
#         manual_password = None
#         if form.cleaned_data['password_option'] == 'manual':
#             manual_password = form.cleaned_data['password']
#
#         try:
#             user_service.create_organization_user(
#                 organization=self.request.organization,
#                 created_by=self.request.user,
#                 user_data=user_data,
#                 role=role,
#                 send_email=send_email,
#                 manual_password=manual_password
#             )
#             messages.success(self.request, 'User created successfully.')
#         except Exception as e:
#             messages.error(self.request, f'Error creating user: {str(e)}')
#             return self.form_invalid(form)
#
#         return super().form_valid(form)

from django.core.exceptions import ValidationError

# class UserCreateView(OrganizationAdminRequiredMixin, FormView):
#     template_name = 'team/user_form.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('team:user_list')
#
    # def dispatch(self, request, *args, **kwargs):
    #     # Check if there are any roles for this organization
    #     if not Role.objects.filter(organization=request.organization).exists():
    #         messages.warning(request, "You need to create at least one role before adding users.")
    #         return redirect('team:user_list')  # or redirect to role creation page
    #     return super().dispatch(request, *args, **kwargs)
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['organization'] = self.request.organization
#         return kwargs

from django.views.generic import ListView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.models import UserProfile
from apps.control_panel.models import UserRole
from .permissions import OrganizationAdminRequiredMixin
from .forms import UserCreationForm, UserUpdateForm
from .services import user_service

class UserListView(OrganizationAdminRequiredMixin, ListView):
    model = UserProfile
    template_name = 'team/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return UserProfile.objects.filter(
            organization=self.request.organization
        ).select_related('user').prefetch_related('user__userrole_set__role')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add role information for each user
        for profile in context['users']:
            user_role = profile.user.userrole_set.first()
            profile.user_role_name = user_role.role.name if user_role else 'No role'
        return context

class UserCreateView(OrganizationAdminRequiredMixin, FormView):
    template_name = 'team/user_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('team:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_users = UserProfile.objects.filter(organization=self.request.organization).count()
        remaining = self.request.organization.max_users - current_users
        context['remaining_slots'] = remaining
        return context

    def form_valid(self, form):
        user_data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'email': form.cleaned_data['email'],
            'phone': form.cleaned_data.get('phone', ''),
            'title': form.cleaned_data.get('title', ''),
            'department': form.cleaned_data.get('department', ''),
            'is_active': form.cleaned_data.get('is_active', True),
        }
        role = form.cleaned_data['role']
        send_email = form.cleaned_data.get('send_welcome_email', False)
        manual_password = None
        if form.cleaned_data['password_option'] == 'manual':
            manual_password = form.cleaned_data['password']

        try:
            user_service.create_organization_user(
                organization=self.request.organization,
                created_by=self.request.user,
                user_data=user_data,
                role=role,
                send_email=send_email,
                manual_password=manual_password
            )
            messages.success(self.request, 'User created successfully.')
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating user: {str(e)}')
            return self.form_invalid(form)

        return super().form_valid(form)

class UserUpdateView(OrganizationAdminRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'team/user_form.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('team:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs

    def get_object(self, queryset=None):
        return UserProfile.objects.get(
            user_id=self.kwargs['pk'],
            organization=self.request.organization
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def form_valid(self, form):
        try:
            form.save()
            messages.success(self.request, 'User updated successfully.')
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return redirect(self.success_url)

class UserDeleteView(OrganizationAdminRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'team/user_confirm_delete.html'
    success_url = reverse_lazy('team:user_list')

    def get_object(self, queryset=None):
        return UserProfile.objects.get(
            user_id=self.kwargs['pk'],
            organization=self.request.organization
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)


# class UserCreateView(OrganizationAdminRequiredMixin, FormView):
#     template_name = 'team/user_form.html'
#     form_class = UserCreationForm
#     success_url = reverse_lazy('team:user_list')
#
#     def dispatch(self, request, *args, **kwargs):
#         # Check if there are any roles for this organization
#         if not Role.objects.filter(organization=request.organization).exists():
#             messages.warning(request, "You need to create at least one role before adding users.")
#             return redirect('team:user_list')  # or redirect to role creation page
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['organization'] = self.request.organization
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         current_users = UserProfile.objects.filter(organization=self.request.organization).count()
#         remaining = self.request.organization.max_users - current_users
#         context['remaining_slots'] = remaining
#         return context
#
#     def form_valid(self, form):
#         user_data = {
#             'first_name': form.cleaned_data['first_name'],
#             'last_name': form.cleaned_data['last_name'],
#             'email': form.cleaned_data['email'],
#             'phone': form.cleaned_data.get('phone', ''),
#             'title': form.cleaned_data.get('title', ''),
#             'department': form.cleaned_data.get('department', ''),
#             'is_active': form.cleaned_data.get('is_active', True),
#         }
#         role = form.cleaned_data['role']
#         send_email = form.cleaned_data.get('send_welcome_email', False)
#         manual_password = None
#         if form.cleaned_data['password_option'] == 'manual':
#             manual_password = form.cleaned_data['password']
#
#         try:
#             user_service.create_organization_user(
#                 organization=self.request.organization,
#                 created_by=self.request.user,
#                 user_data=user_data,
#                 role=role,
#                 send_email=send_email,
#                 manual_password=manual_password
#             )
#             messages.success(self.request, 'User created successfully.')
#         except ValidationError as e:
#             messages.error(self.request, str(e))
#             return self.form_invalid(form)
#         except Exception as e:
#             messages.error(self.request, f'Error creating user: {str(e)}')
#             return self.form_invalid(form)
#
#         return super().form_valid(form)



def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    current_users = UserProfile.objects.filter(organization=self.request.organization).count()
    remaining = self.request.organization.max_users - current_users
    context['remaining_slots'] = remaining
    return context

#
# @login_required
# def sales_team_dashboard(request):
#     """
#     Sales team leaderboard and performance metrics with real data
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#
#     team_by_revenue = []
#     team_by_conversion = []
#     team_by_activity = []
#     individual_performance = []
#
#     # Get all sales users (you can filter by group if needed)
#     sales_users = User.objects.filter(is_active=True)
#
#     for user in sales_users:
#         # Get leads assigned to this user
#         leads = Lead.objects.filter(assigned_to=user)
#         total_leads = leads.count()
#
#         # Get won leads
#         won_leads = leads.filter(stage='won').count()
#
#         # Get lost leads
#         lost_leads = leads.filter(stage='lost').count()
#
#         # Get qualified leads (in pipeline)
#         qualified = leads.filter(stage__in=['qualified', 'survey', 'quote', 'negotiation']).count()
#
#         # Calculate conversion rate
#         conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
#
#         # Get revenue for this month
#         current_month_revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=first_day_month,
#             date__lte=today,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         # Get total revenue all time
#         total_revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         # Calculate average deal size
#         avg_deal_size = total_revenue / won_leads if won_leads > 0 else 0
#
#         # Get activity counts
#         activities = LeadActivity.objects.filter(user=user)
#         calls = activities.filter(activity_type='call').count()
#         whatsapp = activities.filter(activity_type='whatsapp').count()
#         emails = activities.filter(activity_type='email').count()
#         followups = activities.filter(activity_type='followup').count()
#         total_activities = activities.count()
#
#         # Calculate average activities per day (last 30 days)
#         last_30_days = today - timedelta(days=30)
#         recent_activities = activities.filter(created__date__gte=last_30_days).count()
#         avg_per_day = round(recent_activities / 30, 1) if recent_activities > 0 else 0
#
#         # Calculate follow-up compliance (simplified version without JSON lookup)
#         # Count follow-ups that were completed (we can use a different approach)
#         # For now, we'll use a placeholder value or calculate based on FollowUp model
#         # followup_compliance = 75  # Placeholder value
#         # Calculate follow-up compliance using FollowUp model
#         followup_compliance = calculate_followup_compliance(user, first_day_month, today)
#
#         # Calculate trend (compare with last month)
#         last_month = first_day_month - timedelta(days=1)
#         last_month_first = last_month.replace(day=1)
#         last_month_revenue = Revenue.objects.filter(
#             lead__assigned_to=user,
#             date__gte=last_month_first,
#             date__lt=first_day_month,
#             payment_status='paid'
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         trend = ((
#                              current_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
#
#         # Target achievement (example target: ₹10,00,000 per month)
#         monthly_target = 1000000
#         achievement = (current_month_revenue / monthly_target * 100) if monthly_target > 0 else 0
#
#         user_data = {
#             'id': user.id,
#             'name': user.get_full_name() or user.username,
#             'email': user.email,
#             'initials': ''.join([n[0] for n in (user.get_full_name() or user.username).split()[:2]]).upper(),
#             'leads_assigned': total_leads,
#             'leads': total_leads,
#             'qualified': qualified,
#             'won': won_leads,
#             'lost': lost_leads,
#             'conversion_rate': round(conversion_rate, 1),
#             'revenue': current_month_revenue,
#             'total_revenue': total_revenue,
#             'avg_deal_size': round(avg_deal_size, 2),
#             'trend': round(trend, 1),
#             'calls': calls,
#             'whatsapp': whatsapp,
#             'emails': emails,
#             'followups': followups,
#             'total_activities': total_activities,
#             'avg_per_day': avg_per_day,
#             'followup_compliance': round(followup_compliance, 1),
#             'achievement': round(achievement, 1),
#             'followup_percentage': round(followup_compliance, 1),
#         }
#
#         team_by_revenue.append(user_data)
#         individual_performance.append(user_data)
#
#     # Sort by different metrics
#     team_by_revenue = sorted(team_by_revenue, key=lambda x: x['revenue'], reverse=True)
#     team_by_conversion = sorted(team_by_revenue, key=lambda x: x['conversion_rate'], reverse=True)
#     team_by_activity = sorted(team_by_revenue, key=lambda x: x['total_activities'], reverse=True)
#
#     # Top performers
#     top_closer = team_by_revenue[0] if team_by_revenue else {'name': 'N/A', 'revenue': 0}
#
#     # Fastest closer (lowest average days to close)
#     fastest_closer_data = {'name': 'N/A', 'days': 0}
#     if sales_users.exists():
#         # This is a complex query - simplified for now
#         fastest_closer_data = {'name': 'John Doe', 'days': 15}
#
#     # Follow-up king (most follow-ups)
#     followup_king = team_by_activity[0] if team_by_activity else {'name': 'N/A', 'count': 0}
#
#     context = {
#         'team_by_revenue': team_by_revenue,
#         'team_by_conversion': team_by_conversion,
#         'team_by_activity': team_by_activity,
#         'individual_performance': individual_performance[:6],  # Show top 6
#         'top_closer': top_closer,
#         'fastest_closer': fastest_closer_data,
#         'followup_king': followup_king,
#     }
#
#     return render(request, 'team/sales_team.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from calendar import monthrange

from apps.leads.models import Lead, LeadActivity
from apps.revenue.models import Revenue
from apps.core.utils import get_current_organization

User = get_user_model()


def _sales_team_rep_queryset(request):
    """
    Same people set as analytics Sales Performance: org members, Sales group,
    anyone with assigned leads, then staff fallback — not request.organization alone
    (that is often None and yielded an empty team list).
    """
    rep_ids = set()
    rep_ids.update(
        User.objects.filter(groups__name__iexact='Sales').values_list('id', flat=True).distinct()
    )
    rep_ids.update(
        Lead.objects.exclude(assigned_to_id__isnull=True).values_list('assigned_to_id', flat=True).distinct()
    )
    org = getattr(request, 'organization', None) or get_current_organization()
    if org:
        rep_ids.update(
            User.objects.filter(core_profile__organization=org).values_list('id', flat=True).distinct()
        )
    if not rep_ids and Lead.objects.exists():
        rep_ids.update(
            User.objects.filter(is_staff=True, is_active=True).values_list('id', flat=True).distinct()[:100]
        )
    return User.objects.filter(id__in=rep_ids).order_by('first_name', 'last_name', 'username')


def _append_unassigned_sales_row(team_rows, today, first_day_month, revenue_status_filter):
    """Pool of leads with no assigned_to — same idea as analytics."""
    unassigned_leads = Lead.objects.filter(assigned_to__isnull=True)
    unassigned_count = unassigned_leads.count()
    if not unassigned_count:
        return
    won_leads = unassigned_leads.filter(stage='won').count()
    lost_leads = unassigned_leads.filter(stage='lost').count()
    qualified = unassigned_leads.filter(stage__in=['qualified', 'survey', 'quote', 'negotiation']).count()
    conversion_rate = (won_leads / unassigned_count * 100) if unassigned_count > 0 else 0

    current_month_revenue = Revenue.objects.filter(
        lead__assigned_to__isnull=True,
        date__gte=first_day_month,
        date__lte=today,
    ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

    total_revenue = Revenue.objects.filter(
        lead__assigned_to__isnull=True,
    ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

    avg_deal_size = total_revenue / won_leads if won_leads > 0 else 0

    last_month = first_day_month - timedelta(days=1)
    last_month_first = last_month.replace(day=1)
    last_month_revenue = Revenue.objects.filter(
        lead__assigned_to__isnull=True,
        date__gte=last_month_first,
        date__lt=first_day_month,
    ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

    trend = (
        ((current_month_revenue - last_month_revenue) / last_month_revenue * 100)
        if last_month_revenue > 0
        else 0
    )
    monthly_target = 1000000
    achievement = (current_month_revenue / monthly_target * 100) if monthly_target > 0 else 0
    followup_compliance = 0.0

    team_rows.append(
        {
            'id': None,
            'name': 'Unassigned',
            'email': '—',
            'initials': 'NA',
            'leads_assigned': unassigned_count,
            'leads': unassigned_count,
            'total_leads': unassigned_count,
            'qualified': qualified,
            'won': won_leads,
            'lost': lost_leads,
            'conversion_rate': round(conversion_rate, 1),
            'revenue': current_month_revenue,
            'total_revenue': total_revenue,
            'avg_deal_size': round(avg_deal_size, 2),
            'trend': round(trend, 1),
            'calls': 0,
            'whatsapp': 0,
            'emails': 0,
            'followups': 0,
            'total_activities': 0,
            'avg_per_day': 0.0,
            'followup_compliance': followup_compliance,
            'achievement': round(achievement, 1),
            'followup_percentage': followup_compliance,
        }
    )


@login_required
def sales_team_dashboard(request):
    """
    Sales team leaderboard and performance metrics – filtered by current organization.
    """
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    revenue_status_filter = Q(payment_status__in=['paid', 'pending', 'partial'])

    team_by_revenue = []
    for user in _sales_team_rep_queryset(request):
        leads = Lead.objects.filter(assigned_to=user)
        total_leads = leads.count()

        won_leads = leads.filter(stage='won').count()
        lost_leads = leads.filter(stage='lost').count()
        qualified = leads.filter(stage__in=['qualified', 'survey', 'quote', 'negotiation']).count()
        conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0

        current_month_revenue = Revenue.objects.filter(
            lead__assigned_to=user,
            date__gte=first_day_month,
            date__lte=today,
        ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

        total_revenue = Revenue.objects.filter(
            lead__assigned_to=user,
        ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

        avg_deal_size = total_revenue / won_leads if won_leads > 0 else 0

        activities = LeadActivity.objects.filter(user=user)
        calls = activities.filter(activity_type='call').count()
        whatsapp = activities.filter(activity_type='whatsapp').count()
        emails = activities.filter(activity_type='email').count()
        followups = activities.filter(activity_type='followup').count()
        total_activities = activities.count()

        last_30_days = today - timedelta(days=30)
        recent_activities = activities.filter(created__date__gte=last_30_days).count()
        avg_per_day = round(recent_activities / 30, 1) if recent_activities > 0 else 0

        followup_compliance = 75

        last_month = first_day_month - timedelta(days=1)
        last_month_first = last_month.replace(day=1)
        last_month_revenue = Revenue.objects.filter(
            lead__assigned_to=user,
            date__gte=last_month_first,
            date__lt=first_day_month,
        ).filter(revenue_status_filter).aggregate(total=Sum('amount'))['total'] or 0

        trend = (
            ((current_month_revenue - last_month_revenue) / last_month_revenue * 100)
            if last_month_revenue > 0
            else 0
        )

        monthly_target = 1000000
        achievement = (current_month_revenue / monthly_target * 100) if monthly_target > 0 else 0

        name = user.get_full_name() or user.username
        initials_src = name.split()[:2] if name.split() else [user.username[:1]]
        initials = ''.join(n[0] for n in initials_src if n).upper() or user.username[:2].upper()

        user_data = {
            'id': user.id,
            'name': name,
            'email': user.email or '',
            'initials': initials,
            'leads_assigned': total_leads,
            'leads': total_leads,
            'total_leads': total_leads,
            'qualified': qualified,
            'won': won_leads,
            'lost': lost_leads,
            'conversion_rate': round(conversion_rate, 1),
            'revenue': current_month_revenue,
            'total_revenue': total_revenue,
            'avg_deal_size': round(avg_deal_size, 2),
            'trend': round(trend, 1),
            'calls': calls,
            'whatsapp': whatsapp,
            'emails': emails,
            'followups': followups,
            'total_activities': total_activities,
            'avg_per_day': avg_per_day,
            'followup_compliance': round(followup_compliance, 1),
            'achievement': round(achievement, 1),
            'followup_percentage': round(followup_compliance, 1),
        }

        team_by_revenue.append(user_data)

    _append_unassigned_sales_row(team_by_revenue, today, first_day_month, revenue_status_filter)

    team_by_revenue = sorted(team_by_revenue, key=lambda x: x['revenue'], reverse=True)
    team_by_conversion = sorted(team_by_revenue, key=lambda x: x['conversion_rate'], reverse=True)
    team_by_activity = sorted(team_by_revenue, key=lambda x: x['total_activities'], reverse=True)

    # Same rows as revenue leaderboard (all reps + Unassigned), not capped at 6
    individual_performance = list(team_by_revenue)

    top_closer = team_by_revenue[0] if team_by_revenue else {'name': 'N/A', 'revenue': 0}
    fastest_closer = {'name': 'N/A', 'days': 15}

    if team_by_activity:
        followup_king = dict(team_by_activity[0])
        followup_king['count'] = followup_king.get('followups', 0)
    else:
        followup_king = {'name': 'N/A', 'count': 0}

    context = {
        'team_by_revenue': team_by_revenue,
        'team_by_conversion': team_by_conversion,
        'team_by_activity': team_by_activity,
        'individual_performance': individual_performance,
        'top_closer': top_closer,
        'fastest_closer': fastest_closer,
        'followup_king': followup_king,
    }

    return render(request, 'team/sales_team.html', context)

@login_required
def sales_rep_detail(request, pk):
    """
    Detailed view for individual sales rep with real data
    """
    user = get_object_or_404(User, pk=pk)
    today = timezone.now().date()

    # Get leads for this rep
    leads = Lead.objects.filter(assigned_to=user)
    total_leads = leads.count()
    won_leads = leads.filter(stage='won').count()

    # Get revenue data
    total_revenue = Revenue.objects.filter(
        lead__assigned_to=user,
        payment_status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Get monthly revenue for chart (last 6 months)
    months = []
    revenue_data = []

    for i in range(5, -1, -1):  # Last 6 months
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        month_end = month_date.replace(day=monthrange(month_date.year, month_date.month)[1])

        months.append(month_date.strftime('%b %Y'))

        month_revenue = Revenue.objects.filter(
            lead__assigned_to=user,
            date__gte=month_start,
            date__lte=month_end,
            payment_status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        revenue_data.append(float(month_revenue))

    # Get recent activities
    recent_activities = LeadActivity.objects.filter(
        user=user
    ).select_related('lead').order_by('-created')[:10]

    # Format activities for display
    activity_list = []
    for activity in recent_activities:
        activity_list.append({
            'id': activity.id,
            'type': activity.get_activity_type_display(),
            'description': activity.description,
            'lead_name': activity.lead.name if activity.lead else 'Unknown',
            'created': activity.created.strftime('%d %b %Y, %I:%M %p'),
            'icon': get_activity_icon(activity.activity_type)
        })

    context = {
        'rep': user,
        'total_leads': total_leads,
        'won_leads': won_leads,
        'total_revenue': total_revenue,
        'recent_activities': activity_list,
        'months': months,
        'revenue_data': revenue_data,
    }

    return render(request, 'team/sales_rep_detail.html', context)


def get_activity_icon(activity_type):
    """Helper function to get icon for activity type"""
    icons = {
        'call': 'fa-phone',
        'whatsapp': 'fa-whatsapp',
        'email': 'fa-envelope',
        'note': 'fa-sticky-note',
        'followup': 'fa-calendar',
        'stage_change': 'fa-exchange-alt',
        'quotation': 'fa-file-invoice',
        'survey': 'fa-hard-hat',
    }
    return icons.get(activity_type, 'fa-clock')


def calculate_followup_compliance(user, start_date, end_date):
    """
    Calculate follow-up compliance without using JSON lookups
    """
    # Get all scheduled follow-ups for this user in the date range
    scheduled_followups = FollowUp.objects.filter(
        user=user,
        scheduled_date__date__gte=start_date,
        scheduled_date__date__lte=end_date
    )

    total_scheduled = scheduled_followups.count()
    if total_scheduled == 0:
        return 0

    # Count completed follow-ups
    completed = scheduled_followups.filter(status='completed').count()

    return (completed / total_scheduled * 100)
