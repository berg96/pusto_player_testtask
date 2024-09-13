from django.core.exceptions import ValidationError
from django.db import models

ALREADY_ADD = 'Этот буст "{}" уже добавлен игроку {}.'
INCORRECT_BOOST = 'Переданный аргумент должен быть экземпляром модели Boost.'


class Player(models.Model):
    username = models.CharField(max_length=255, verbose_name='Никнейм')
    score = models.IntegerField(verbose_name='Количество баллов', default=0)
    first_entry = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата первого входа'
    )
    boosts = models.ManyToManyField('Boost', related_name='players', blank=True)

    def give_boost(self, boost):
        if not isinstance(boost, Boost):
            raise ValidationError(INCORRECT_BOOST)
        if self.boosts.filter(id=boost.id).exists():
            raise ValidationError(
                ALREADY_ADD.format(boost.name, self.username)
            )
        self.boosts.add(boost)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return f'{self.username} ({self.score}) - {self.first_entry}'


class Boost(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название усиления')

    class Meta:
        verbose_name = 'Усиление'
        verbose_name_plural = 'Усиления'

    def __str__(self):
        return f'{self.name}'
