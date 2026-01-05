from django.shortcuts import render, get_object_or_404, redirect
from weeks.models import Week
from members.models import Member
from .models import Team, TeamMember
from .services.team_maker import TeamMaker

def team_home(request, week_id):
    """
    팀 편성 초기 화면
    - 아직 팀 없음
    - 점수 입력 페이지로 이동 버튼
    """
    week = get_object_or_404(Week, id=week_id)

    return render(request, "teams/team_home.html", {
        "week": week,
    })


def score_input(request, week_id):
    """
    과제 점수 입력 화면
    - 멤버별 점수 입력
    - 저장 시 DB 반영
    """
    week = get_object_or_404(Week, id=week_id)
    members = Member.objects.all().order_by("name")

    if request.method == "POST":
        for member in members:
            score = request.POST.get(f"score_{member.id}")
            if score is not None and score != "":
                member.score = float(score)
                member.save()

        return redirect("teams:team_preview", week_id=week.id)

    return render(request, "teams/score_input.html", {
        "week": week,
        "members": members,
    })



def team_preview(request, week_id):
    """
    팀 편성 미리보기
    - TeamMaker로 팀 생성
    - DB 저장 ❌
    - session에만 결과 저장
    """
    week = get_object_or_404(Week, id=week_id)

    maker = TeamMaker(week_id)
    result = maker.run_assignment()

    # session 저장용 (id만 저장)
    request.session["team_preview"] = [
        {
            "team_no": team["team_no"],
            "member_ids": [m.id for m in team["members"]]
        }
        for team in result
    ]

    return render(request, "teams/team_preview.html", {
        "week": week,
        "teams": result,
    })



def team_save(request, week_id):
    #미리보기 결과를 DB에 확정 저장
    week = get_object_or_404(Week, id=week_id)
    preview = request.session.get("team_preview")

    if not preview:
        return redirect("teams:team_preview", week_id=week.id)

    # 기존 팀 삭제 (재생성 대비)
    Team.objects.filter(week=week).delete()

    for team_data in preview:
        team = Team.objects.create(
            week=week,
            team_no=team_data["team_no"]
        )

        for member_id in team_data["member_ids"]:
            TeamMember.objects.create(
                team=team,
                member_id=member_id
            )

    # session 정리
    del request.session["team_preview"]

    return redirect("teams:team_home", week_id=week.id)
