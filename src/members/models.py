from django.db import models


class Member(models.Model):
    GENDER_CHOICES = [
        ('M', '남자'),  # 남자
        ('F', '여자'),  # 여자
    ]

    MAJOR_CHOICES = [
        ('O', '전공자'),  # 전공자
        ('X', '비전공자'),  # 비전공자
    ]

    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    major = models.CharField(max_length=1, choices=MAJOR_CHOICES)

    def __str__(self):
        return self.name
