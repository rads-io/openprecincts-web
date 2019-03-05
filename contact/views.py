from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Max
from django.contrib import messages
from django.utils.html import mark_safe
from contact.models import Official, EmailMessage


class EmailForm(forms.Form):
    subject_template = forms.CharField(max_length=100)
    body_template = forms.CharField(widget=forms.Textarea)


def bulk_email(request, state):
    # TODO: add permission checking

    if request.method == "POST":
        form = EmailForm(request.POST)
        recipients = request.POST.getlist('recipients')
        if form.is_valid() and recipients:
            email = EmailMessage.objects.create(
                subject_template=form.cleaned_data['subject_template'],
                body_template=form.cleaned_data['body_template'],
                created_by=request.user,
            )
            email.officials.set(recipients)
            return redirect('preview_email', email.id)
        elif not recipients:
            messages.error(request, "Must specify at least one recipient.")
    else:
        form = EmailForm()

    officials = Official.objects.filter(
        locality__state__abbreviation=state.upper(),
        active=True,
    ).exclude(
        email="",
    ).annotate(
        times_contacted=Count('messages'),
        last_contacted=Max('messages__sent_at'),
    )
    return render(request, 'contact/bulk_email.html', {
        'form': form,
        'officials': officials,
    })


def render_email(email, official, preview=False):
    email_context = {
        "LOCALITY": official.locality.name,
        "FIRST": official.first_name,
        "LAST": official.last_name,
        "NAME": ' '.join((official.first_name, official.last_name)),
        "TITLE": official.title,
    }

    if preview:
        for k in email_context:
            email_context[k] = f'<span class="templatevar">{email_context[k]}</span>'
    subject = email.subject_template.format(**email_context)
    body = email.body_template.format(**email_context)
    return official.email, subject, body


def preview(request, id):
    email = get_object_or_404(EmailMessage, pk=id)

    try:
        _, preview_subject, preview_body = render_email(email, email.officials.first(), preview=True)
    except KeyError as e:
        preview_subject = email.subject_template
        preview_body = email.body_template
        messages.error(request, f"Error in template: {e}")

    return render(request, 'contact/preview_email.html', {
        'email': email,
        'preview_subject': mark_safe(preview_subject),
        'preview_body': mark_safe(preview_body),
    })