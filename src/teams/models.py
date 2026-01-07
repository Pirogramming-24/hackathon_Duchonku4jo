from django.db import models
from weeks.models import Week
from members.models import Member


class Team(models.Model):
    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name="teams"
    )
    team_no = models.PositiveIntegerField()
    team_score = models.FloatField(default=0)

    class Meta:
        db_table = "team"
        unique_together = ("week", "team_no")

    def __str__(self):
        return f"{self.week.week_no}주차 {self.team_no}팀"


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members"
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="teams"
    )

    class Meta:
        db_table = "team_member"
        unique_together = ("team", "member")

    def __str__(self):
        return f"{self.team} - {self.member}"
