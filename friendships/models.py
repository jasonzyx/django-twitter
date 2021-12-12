from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_user_set"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_user_set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('from_user_id', 'created_at'),
            ('to_user_id', 'created_at')
        )
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return f'{self.created_at}: {self.from_user_id} followed {self.to_user_id}'
