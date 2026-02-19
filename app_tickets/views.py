import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Ticket, Comment, TicketCategory
from .forms import TicketForm, CommentForm

class TicketCategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = TicketCategory
    template_name = 'app_tickets/category_list.html'
    context_object_name = 'categories'

    def test_func(self):
        return self.request.user.is_staff

class TicketCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TicketCategory
    fields = ['name', 'description']
    template_name = 'app_tickets/category_form.html'
    success_url = reverse_lazy('app_tickets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class TicketCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TicketCategory
    fields = ['name', 'description']
    template_name = 'app_tickets/category_form.html'
    success_url = reverse_lazy('app_tickets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class TicketCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TicketCategory
    template_name = 'app_tickets/category_confirm_delete.html'
    success_url = reverse_lazy('app_tickets:category_list')

    def test_func(self):
        return self.request.user.is_staff

class TicketExportCSVView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        # Replicate logic from TicketListView or similar filtering
        queryset = Ticket.objects.all().order_by('-created_at')

        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        filter_type = self.request.GET.get('filter')
        search_query = self.request.GET.get('q')

        if not status:
             queryset = queryset.exclude(status=Ticket.Status.CLOSED)
        else:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if filter_type == 'my_tickets':
            queryset = queryset.filter(
                Q(assigned_agent=self.request.user) | Q(creator=self.request.user)
            )

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tickets.csv"'

        writer = csv.writer(response)
        writer.writerow(['Ticket ID', 'Title', 'Status', 'Priority', 'Category', 'Creator', 'Assigned Agent', 'Created Date'])

        for ticket in queryset:
            writer.writerow([
                ticket.id,
                ticket.title,
                ticket.get_status_display(),
                ticket.get_priority_display(),
                ticket.category.name if ticket.category else 'N/A',
                ticket.creator.username,
                ticket.assigned_agent.username if ticket.assigned_agent else 'Unassigned',
                ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'app_tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        filter_type = self.request.GET.get('filter')
        search_query = self.request.GET.get('q')

        # Default: Exclude CLOSED tickets unless specifically requested via status filter
        if not status:
            queryset = queryset.exclude(status=Ticket.Status.CLOSED)
        else:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        if filter_type == 'my_tickets':
            queryset = queryset.filter(
                Q(assigned_agent=self.request.user) | Q(creator=self.request.user)
            )

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Ticket.Status.choices
        context['priority_choices'] = Ticket.Priority.choices
        return context

class TicketArchiveListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'app_tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        # Only show CLOSED tickets
        queryset = super().get_queryset().filter(status=Ticket.Status.CLOSED)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Ticket.Status.choices
        context['priority_choices'] = Ticket.Priority.choices
        context['is_archive'] = True
        return context

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'app_tickets/ticket_create.html'
    success_url = reverse_lazy('app_tickets:ticket_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'app_tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        # Filter comments based on user permissions
        if self.request.user.is_staff:
            context['comments'] = self.object.comments.all().order_by('created_at')
        else:
            context['comments'] = self.object.comments.filter(is_public=True).order_by('created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = self.object
            comment.author = request.user
            # Only staff can make non-public comments. For regular users, force is_public=True
            if not request.user.is_staff:
                comment.is_public = True
            comment.save()
            return redirect('app_tickets:ticket_detail', pk=self.object.pk)

        context = self.get_context_data(object=self.object)
        context['comment_form'] = form
        return self.render_to_response(context)

class TicketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'app_tickets/ticket_create.html'
    context_object_name = 'ticket'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        # Allow staff or creator to update
        ticket = self.get_object()
        return self.request.user.is_staff or ticket.creator == self.request.user

    def get_success_url(self):
        return reverse_lazy('app_tickets:ticket_detail', kwargs={'pk': self.object.pk})

class TicketDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ticket
    template_name = 'app_tickets/ticket_confirm_delete.html'
    success_url = reverse_lazy('app_tickets:ticket_list')

    def test_func(self):
        return self.request.user.is_staff
