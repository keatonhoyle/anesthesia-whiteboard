from django.db import models

class WhiteboardEntry(models.Model):
    room = models.CharField(max_length=50, unique=True)
    provider = models.CharField(max_length=100)
    surgeon = models.CharField(max_length=100)

    def __str__(self):
        return self.room

    class Meta:
        verbose_name = "Whiteboard Entry"
        verbose_name_plural = "Whiteboard Entries"