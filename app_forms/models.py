from django.db import models
from django.conf import settings

class CustomForm(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class FormQuestion(models.Model):
    QUESTION_TYPES = [
        ('TEXT', 'Short Text'),
        ('PARAGRAPH', 'Long Text'),
        ('CHOICE', 'Multiple Choice'),
    ]

    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='TEXT')
    choices = models.TextField(null=True, blank=True, help_text="Comma separated for CHOICE type")
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def get_choices_list(self):
        if not self.choices:
            return []
        return [c.strip() for c in self.choices.split(',') if c.strip()]

    def __str__(self):
        return self.question_text

class FormSubmission(models.Model):
    form = models.ForeignKey(CustomForm, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"Submission for {self.form.title} at {self.submitted_at}"

class FormAnswer(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.question.question_text}: {self.answer_text}"
