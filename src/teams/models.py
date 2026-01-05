from django.db import models

class Member(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    name = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Week(models.Model):
    week_no = models.IntegerField()
    team_count = models.IntegerField()
    pr_name = models.CharField(max_length=100)


class Team(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    team_no = models.IntegerField()
    team_score = models.FloatField(default=0.0)


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='team_history'
    )
