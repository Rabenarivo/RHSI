from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import ComposeMessageForm
from recrutement_accounts.models import Account

def get_current_account(request):
    try:
        return Account.objects.get(email=request.user.username)
    except Account.DoesNotExist:
        return None

@login_required
def inbox(request):
    account = get_current_account(request)
    if not account:
        return redirect('recrutement_accounts:home')
        
    messages_list = Message.objects.filter(recipient=account).order_by('-sent_at')
    return render(request, 'recrutement_messages/inbox.html', {'messages_list': messages_list})

@login_required
def sent_messages(request):
    account = get_current_account(request)
    if not account:
        return redirect('recrutement_accounts:home')
        
    messages_list = Message.objects.filter(sender=account).order_by('-sent_at')
    return render(request, 'recrutement_messages/sent.html', {'messages_list': messages_list})

@login_required
def compose(request):
    account = get_current_account(request)
    if not account:
        return redirect('recrutement_accounts:home')
        
    if request.method == 'POST':
        form = ComposeMessageForm(request.POST, user=account)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = account
            msg.save()
            messages.success(request, "Votre message a été envoyé avec succès.")
            return redirect('recrutement_messages:sent_messages')
    else:
        # Pre-fill for replies if provided in URL
        initial = {}
        reply_to_id = request.GET.get('reply_to')
        if reply_to_id:
            original_msg = get_object_or_404(Message, id=reply_to_id, recipient=account)
            initial['recipient'] = original_msg.sender
            initial['subject'] = f"Re: {original_msg.subject}"
            
        form = ComposeMessageForm(user=account, initial=initial)
        
    return render(request, 'recrutement_messages/compose.html', {'form': form})

@login_required
def read_message(request, message_id):
    account = get_current_account(request)
    msg = get_object_or_404(Message, id=message_id)
    
    # Vérifier l'accès
    if msg.recipient != account and msg.sender != account:
        messages.error(request, "Accès refusé.")
        return redirect('recrutement_messages:inbox')
        
    # Marquer comme lu si c'est le destinataire
    if msg.recipient == account and not msg.is_read:
        msg.is_read = True
        msg.save()
        
    return render(request, 'recrutement_messages/read.html', {'msg': msg})
