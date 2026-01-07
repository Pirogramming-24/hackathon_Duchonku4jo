from django.shortcuts import render, get_object_or_404, redirect
from weeks.models import Week
from members.models import Member
from .models import Team, TeamMember
from .services.team_maker import TeamMaker

def team_home(request, week_id):
    """
    팀 편성 초기/저장 화면
    - 저장된 팀이 있으면 그대로 보여줌
    - 없으면 빈 보드
    """
    week = get_object_or_404(Week, id=week_id)

    saved_teams_qs = (
        Team.objects.filter(week=week)
        .order_by("team_no")
        .prefetch_related("members__member")  # TeamMember -> member
    )

    teams = []
    if saved_teams_qs.exists():
        for t in saved_teams_qs:
            members = [tm.member for tm in t.members.all()]  # TeamMember related_name="members"
            teams.append({
                "team_no": t.team_no,
                "members": members,
                "team_score": t.team_score,
            })

    return render(request, "teams/team_home.html", {
        "week": week,
        "teams": teams,   # ✅ 추가
    })


def team_preview(request, week_id):
    """
    팀 편성 미리보기
    - TeamMaker로 팀 생성
    - DB 저장 ❌
    - session에 결과 저장 (id + 평균점수)
    """
    week = get_object_or_404(Week, id=week_id)

    maker = TeamMaker(week_id)
    result = maker.run_assignment()  # 팀 리스트

    # ✅ session 저장: member_ids + team_score까지 저장
    request.session["team_preview"] = [
        {
            "team_no": team["team_no"],
            "member_ids": [m.id for m in team["members"]],
            "team_score": float(team.get("team_score", 0)),  # 없으면 0
        }
        for team in result
    ]

    return render(request, "teams/team_preview.html", {
        "week": week,
        "teams": result,
    })


def team_save(request, week_id):
    """
    미리보기 결과를 DB에 확정 저장
    - team_score도 같이 저장
    - 저장 후 홈에서 저장된 팀이 보이게 됨
    """
    week = get_object_or_404(Week, id=week_id)
    preview = request.session.get("team_preview")

    if not preview:
        # ✅ 저장할 preview 없으면 다시 뽑게 preview로 보냄
        return redirect("teams:team_home", week_id=week.id)

    # 기존 팀 삭제 (재생성 대비)
    Team.objects.filter(week=week).delete()

    for team_data in preview:
        team = Team.objects.create(
            week=week,
            team_no=team_data["team_no"],
            team_score=team_data.get("team_score", 0),  # ✅ 평균점수 저장
        )

        for member_id in team_data["member_ids"]:
            TeamMember.objects.create(
                team=team,
                member_id=member_id
            )

    # session 정리
    del request.session["team_preview"]

    # ✅ 저장 후 홈으로 가면 DB에서 팀을 읽어서 보여줌
    return redirect("teams:team_home", week_id=week.id)

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