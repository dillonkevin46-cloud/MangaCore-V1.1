from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Ticket, Comment
from .forms import TicketForm, CommentForm

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'app_tickets/ticket_list.html'
    context_object_name = 'tickets'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        filter_param = self.request.GET.get('filter')

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if filter_param == 'my_tickets':
            queryset = queryset.filter(creator=self.request.user)
        return queryset

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
        messages.success(self.request, "Ticket created successfully!")
        return super().form_valid(form)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'app_tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        if self.request.user.is_staff:
             context['comments'] = self.object.comments.all().order_by('created_at')
        else:
             context['comments'] = self.object.comments.filter(is_public=True).order_by('created_at')
        return context

class TicketAddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'app_tickets/ticket_detail.html' # Fallback, though we usually redirect

    def form_valid(self, form):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        form.instance.ticket = ticket
        form.instance.author = self.request.user
        form.save()
        messages.success(self.request, "Comment added.")
        return redirect('app_tickets:ticket_detail', pk=ticket.pk)

    def form_invalid(self, form):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        messages.error(self.request, "Error adding comment.")
        return redirect('app_tickets:ticket_detail', pk=ticket.pk)

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class TicketUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'app_tickets/ticket_create.html' # Reuse create template
    context_object_name = 'ticket'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Ticket updated.")
        return reverse('app_tickets:ticket_detail', kwargs={'pk': self.object.pk})

class TicketDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'app_tickets/ticket_confirm_delete.html'
    success_url = reverse_lazy('app_tickets:ticket_list')
