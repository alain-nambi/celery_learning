from django.db import models


class EmailMessage(models.Model):
    subject = models.CharField(max_length=255)
    from_email = models.EmailField()
    to_email = models.EmailField()
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
