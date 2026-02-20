from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomForm, FormQuestion, FormSubmission, FormAnswer
from .forms import CustomFormCreateForm, FormQuestionCreateForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class FormListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = CustomForm
    template_name = 'app_forms/form_list.html'
    context_object_name = 'forms'
    ordering = ['-created_at']

class FormCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = CustomForm
    form_class = CustomFormCreateForm
    template_name = 'app_forms/form_create.html' # We can reuse or create new

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Form created. Now add some questions!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app_forms:form_builder', kwargs={'pk': self.object.pk})

class FormBuilderView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = CustomForm
    template_name = 'app_forms/form_builder.html'
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_form'] = FormQuestionCreateForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = FormQuestionCreateForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.form = self.object
            question.save()
            messages.success(request, "Question added.")
            return redirect('app_forms:form_builder', pk=self.object.pk)

        # If invalid, re-render context
        context = self.get_context_data()
        context['question_form'] = form
        return self.render_to_response(context)

class FormServeView(View):
    """
    Public facing view to render and handle form submissions.
    """
    def get(self, request, pk):
        custom_form = get_object_or_404(CustomForm, pk=pk, is_active=True)
        return render(request, 'app_forms/form_serve.html', {'form': custom_form})

    def post(self, request, pk):
        custom_form = get_object_or_404(CustomForm, pk=pk, is_active=True)

        # Basic validation could go here, but for now we iterate questions
        email_contact = request.POST.get('email_contact')

        submission = FormSubmission(
            form=custom_form,
            submitted_by=email_contact
        )
        # We need to save submission to add answers, but we might rollback if validation fails
        # A transaction would be better but keeping it simple as per guidelines
        submission.save()

        answers_to_create = []

        for question in custom_form.questions.all():
            answer_key = f"question_{question.id}"
            answer_text = request.POST.get(answer_key)

            # Simple required check
            if question.is_required and not answer_text:
                messages.error(request, f"Question '{question.question_text}' is required.")
                submission.delete() # Rollback
                return render(request, 'app_forms/form_serve.html', {
                    'form': custom_form,
                    'values': request.POST # Preserve input
                })

            if answer_text:
                answers_to_create.append(FormAnswer(
                    submission=submission,
                    question=question,
                    answer_text=answer_text
                ))

        FormAnswer.objects.bulk_create(answers_to_create)

        return render(request, 'app_forms/form_serve.html', {'form': custom_form, 'submitted': True})

class FormResponsesView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = CustomForm
    template_name = 'app_forms/form_responses.html'
    context_object_name = 'form'

class FormShareEmailView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        custom_form = get_object_or_404(CustomForm, pk=pk)
        recipient = request.POST.get('recipient_email')

        if recipient:
            link = request.build_absolute_uri(reverse('app_forms:form_serve', args=[pk]))
            subject = f"Please fill out: {custom_form.title}"
            message = f"You have been invited to fill out the following form:\n\n{custom_form.title}\n{custom_form.description}\n\nClick here: {link}"

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
                messages.success(request, f"Link sent to {recipient}")
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")

        return redirect('app_forms:form_builder', pk=pk)
