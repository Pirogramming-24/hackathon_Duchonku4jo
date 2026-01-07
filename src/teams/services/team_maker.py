import random
from collections import Counter
from ..models import Member, Week, TeamMember

class TeamMaker:
    def __init__(self, week_id):
        self.week = Week.objects.get(id=week_id)
        self.team_count = self.week.team_count

    def run_assignment(self):
        # 1, 2단계 배정을 실행하고 결과를 반환합니다.

        # 1단계: 1차 배정 (전공/비전공 비율 및 실력 균형)
        majors = list(Member.objects.filter(major='O').order_by('-score', '?'))
        non_majors = list(Member.objects.filter(major='X').order_by('-score', '?'))

        temp_teams = [[] for _ in range(self.team_count)]

        # 전공자 스네이크 배정
        for i, m in enumerate(majors):
            idx = i % self.team_count
            if (i // self.team_count) % 2 == 1:
                idx = self.team_count - 1 - idx
            temp_teams[idx].append(m)

        # 비전공자 스네이크 배정
        for i, f in enumerate(non_majors):
            idx = i % self.team_count
            if (i // self.team_count) % 2 == 0:
                idx = self.team_count - 1 - idx
            temp_teams[idx].append(f)

        # 2단계: 이전 팀 중복 최소화
        self._minimize_overlap(temp_teams)

        return self._format_result(temp_teams)

    def _minimize_overlap(self, temp_teams):
        # 이전 주차와 팀원이 3명 이상 겹칠 경우 교체합니다
        prev_week = Week.objects.filter(week_no=self.week.week_no - 1).first()
        if not prev_week:
            return

        changed = True
        while changed:
            changed = False
            for i in range(len(temp_teams)):
                # 이전 팀 구성 이력 조회
                prev_team_ids = TeamMember.objects.filter(
                    team__week=prev_week, 
                    member__in=temp_teams[i]
                ).values_list('team_id', flat=True)
                
                counts = Counter(prev_team_ids)
                overlap_team_id = next((tid for tid, count in counts.items() if count >= 3), None)

                if overlap_team_id:
                    # 중복 인원 중 한 명을 뽑아 다른 팀원과 교체 (Selection Swap)
                    target_member = next(m for m in temp_teams[i] if TeamMember.objects.filter(team_id=overlap_team_id, member=m).exists())
                    
                    for j in range(len(temp_teams)):
                        if i == j: continue
                        for idx, other in enumerate(temp_teams[j]):
                            if other.gender == target_member.gender:
                                temp_teams[i].remove(target_member)
                                temp_teams[j].remove(other)
                                temp_teams[i].append(other)
                                temp_teams[j].append(target_member)
                                changed = True
                                break
                        if changed: break
                if changed: break

    def _format_result(self, temp_teams):
        result = []
        for idx, members in enumerate(temp_teams):
            # score가 None일 수 있으니 0으로 처리
            scores = [(m.score or 0) for m in members]
            avg = (sum(scores) / len(scores)) if members else 0

            result.append({
                'team_no': idx + 1,
                'members': members,
                'team_score': round(avg, 2),   # ✅ 키 통일
            })
        return result