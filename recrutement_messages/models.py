from django.db import models
from recrutement_accounts.models import Account

class Message(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} to {self.recipient.email}: {self.subject}"
