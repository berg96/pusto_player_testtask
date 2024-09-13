import csv
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

INCORRECT_LEVEL = 'Переданный аргумент должен быть экземпляром модели Level.'
NOT_COMPLETED = 'Игрок {} не завершил уровень {}.'
PRIZE_NOT_FOUND = 'Приз для уровня {} не найден.'
RECEIVED = 'Приз на уровне {} уже получен'


class Player(models.Model):
    player_id = models.CharField(max_length=100)

    def awarding_for_level(self, level):
        if not isinstance(level, Level):
            raise ValidationError(INCORRECT_LEVEL)
        try:
            player_level = PlayerLevel.objects.get(player=self, level=level)
        except PlayerLevel.DoesNotExist:
            raise ValidationError(
                NOT_COMPLETED.format(self.player_id, level.title)
            )
        if not player_level.is_completed:
            raise ValidationError(
                NOT_COMPLETED.format(self.player_id, level.title)
            )
        try:
            level_prize = LevelPrize.objects.get(level=level)
        except LevelPrize.DoesNotExist:
            raise ValidationError(PRIZE_NOT_FOUND.format(level.title))
        if level_prize.received:
            raise ValidationError(RECEIVED.format(level.title))
        level_prize.received = datetime.now()
        level_prize.save()


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField(max_length=100)


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()


def export_to_csv():
    with open(
            'player_data.csv', 'w', newline='', encoding='utf-8'
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            ['player_id', 'level_title', 'is_completed', 'prize_title']
        )
        player_levels = PlayerLevel.objects.select_related(
            'player', 'level'
        ).prefetch_related('level__levelprize_set')
        for player_level in player_levels:
            level = player_level.level
            level_prizes = level.levelprize_set.all()
            prize_title = ', '.join(
                [
                    level_prize.prize.title for level_prize in level_prizes
                    if level_prize.received
                ]
            ) or 'None'
            writer.writerow([
                player_level.player.player_id,
                level.title,
                player_level.is_completed,
                prize_title
            ])
