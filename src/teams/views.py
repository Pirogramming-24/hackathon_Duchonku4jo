from django.shortcuts import render, redirect
from django.db import transaction
from .models import Member, Week, Team, TeamMember
import random
from .services.team_maker import TeamMaker

def generate_teams(request):
    # 팀 생성 버튼 클릭 시 호출 (알고리즘 실행 레이어 호출)
    week_id = request.GET.get('week_id')
    week = Week.objects.get(id=week_id)

    # 1. 서비스 클래스 인스턴스 생성 및 실행
    maker = TeamMaker(week_id)
    display_teams = maker.run_assignment()

    # 2. '저장' 버튼 클릭 시를 대비해 세션에 임시 저장
    request.session['temp_team_result'] = {
        'week_id': week_id,
        'teams': [[m.id for m in t['members']] for t in display_teams]
    }

    # 3. 결과 페이지 렌더링 (새로고침 시 다시 배정됨)
    return render(request, 'teams/team_generate.html', {
        'teams': display_teams,
        'week': week
    })


@transaction.atomic
def save_teams(request):
    # 세션에 저장된 데이터를 실제 DB에 저장
    if request.method == "POST":
        data = request.session.get('temp_team_result')
        if not data:
            return redirect('teams:team_list')

        week = Week.objects.get(id=data['week_id'])
        Team.objects.filter(week=week).delete()

        for idx, member_ids in enumerate(data['teams']):
            members = Member.objects.filter(id__in=member_ids)
            avg_score = sum(m.score for m in members) / len(members)

            team = Team.objects.create(
                week=week,
                team_no=idx + 1,
                team_score=avg_score
            )
            for m_id in member_ids:
                TeamMember.objects.create(team=team, member_id=m_id)

        del request.session['temp_team_result']
        return redirect('teams:team_list')
