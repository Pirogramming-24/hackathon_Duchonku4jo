from django.db import models


class Week(models.Model):
    week_no = models.PositiveIntegerField(
        verbose_name="주차",
        help_text="몇 주차인지 (예: 1주차, 2주차)"
    )
    team_count = models.PositiveIntegerField(
        verbose_name="팀 개수",
        help_text="해당 주차의 팀 개수"
    )
    pr_name = models.CharField(
        max_length=100,
        verbose_name="과제명",
        help_text="해당 주차 프로젝트 / 과제 이름"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일"
    )

    class Meta:
        db_table = "week"
        ordering = ["week_no"]
        verbose_name = "주차"
        verbose_name_plural = "주차 목록"
        unique_together = ("week_no", "pr_name")

    def __str__(self):
        return f"{self.week_no}주차 - {self.pr_name}"