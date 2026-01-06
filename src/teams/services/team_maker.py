import random
from django.db.models import Count
from members.models import Member
from weeks.models import Week
from teams.models import Team, TeamMember

class TeamMaker:
    def __init__(self, week_id):
        self.week_id = week_id
        # 현재 주차와 이전 주차 정보 가져오기
        self.current_week = Week.objects.get(id=week_id)
        self.prev_week = Week.objects.filter(id__lt=week_id).order_by('-id').first()
        
        # 전체 부원 데이터 로드
        self.members = list(Member.objects.all())
        # 이전 주차 팀 구성 데이터 로드 (중복 체크용)
        self.prev_team_map = self._get_prev_team_map()

    def _get_prev_team_map(self):
        """멤버별로 이전 주에 몇 번 팀이었는지 매핑 {member_id: team_id}"""
        if not self.prev_week:
            return {}
        
        prev_members = TeamMember.objects.filter(team__week=self.prev_week)
        return {tm.member_id: tm.team_id for tm in prev_members}

    def run_assignment(self, n_teams=5):
        """배정 프로세스 실행"""
        # 1. 1차 배정: 전공/실력 기반 스네이크
        teams = self._distribute_initial(n_teams)
        
        # 2. 2차 배정: 성비 균형 조정
        teams = self._balance_gender(teams)
        
        # 3. 3차 배정: 이전 멤버 중복 방지
        teams = self._reduce_overlap(teams)
        
        return teams

    def _distribute_initial(self, n):
        """전공/비전공 및 점수 기준 스네이크 배정"""
        majors = sorted(
            [m for m in self.members if m.is_major], 
            key=lambda x: (x.score, random.random()), reverse=True
        )
        non_majors = sorted(
            [m for m in self.members if not m.is_major], 
            key=lambda x: (x.score, random.random()), reverse=True
        )

        teams = [{"team_no": i + 1, "members": []} for i in range(n)]

        # 전공자: 1 -> n -> n -> 1 스네이크
        for i, m in enumerate(majors):
            idx = i % (2 * n)
            if idx >= n:
                idx = 2 * n - 1 - idx
            teams[idx]["members"].append(m)

        # 비전공자: n -> 1 -> 1 -> n 스네이크
        for i, m in enumerate(non_majors):
            idx = i % (2 * n)
            if idx >= n:
                idx = 2 * n - 1 - idx
            # 반대 방향으로 뒤집기 (n번 조부터)
            teams[n - 1 - idx]["members"].append(m)
            
        return teams

    def _balance_gender(self, teams):
        """성비 5:0 조 조정"""
        for i, team in enumerate(teams):
            genders = [m.gender for m in team["members"]]
            # 성비가 5:0인 경우 (전체 성별이 하나뿐인 경우)
            if len(set(genders)) == 1:
                target_gender = genders[0]
                # 교체 대상 찾기 (반대 성별이 3명 이상 있는 조)
                for other_team in teams:
                    if other_team == team: continue
                    
                    opp_members = [m for m in other_team["members"] if m.gender != target_gender]
                    if len(opp_members) >= 3:
                        # 점수가 가장 비슷한 사람끼리 교체
                        m1 = team["members"][0] # 임의의 한 명
                        m2 = min(opp_members, key=lambda x: abs(x.score - m1.score))
                        
                        team["members"].remove(m1)
                        other_team["members"].remove(m2)
                        team["members"].append(m2)
                        other_team["members"].append(m1)
                        break
        return teams

    def _reduce_overlap(self, teams):
        """이전 주와 멤버 3명 이상 겹침 방지"""
        if not self.prev_team_map:
            return teams

        for i, team in enumerate(teams):
            while True:
                # 이전 팀 ID별로 현재 팀원들이 몇 명이나 겹치는지 계산
                overlap_counts = {}
                for m in team["members"]:
                    prev_tid = self.prev_team_map.get(m.id)
                    if prev_tid:
                        overlap_counts[prev_tid] = overlap_counts.get(prev_tid, 0) + 1
                
                # 3명 이상 겹치는 팀 ID 찾기
                problematic_prev_tid = next((tid for tid, count in overlap_counts.items() if count >= 3), None)
                
                if not problematic_prev_tid:
                    break # 문제 없으면 다음 조로
                
                # 교체 대상 선정 (위반한 사람 중 한 명)
                m1 = next(m for m in team["members"] if self.prev_team_map.get(m.id) == problematic_prev_tid)
                
                best_swap = self._find_best_swap(m1, team, teams)
                if best_swap:
                    target_team, m2 = best_swap
                    team["members"].remove(m1)
                    target_team["members"].remove(m2)
                    team["members"].append(m2)
                    target_team["members"].append(m1)
                else:
                    break # 교체 가능한 대상을 못 찾으면 무한루프 방지
                    
        return teams

    def _find_best_swap(self, m1, current_team, all_teams):
        """우선순위에 따른 최적의 교체 멤버 탐색"""
        candidates = []
        for other_team in all_teams:
            if other_team == current_team: continue
            for m2 in other_team["members"]:
                # 조건 검사
                score_diff = abs(m1.score - m2.score)
                
                # 가중치 계산 (낮을수록 좋음)
                penalty = 0
                
                # 1순위: 전공자 비율 (0:5 방지)
                if not self._check_major_balance(current_team, m1, m2) or \
                   not self._check_major_balance(other_team, m2, m1):
                    continue
                
                # 2순위: 성비 균형 (5:0 방지)
                if not self._check_gender_balance(current_team, m1, m2) or \
                   not self._check_gender_balance(other_team, m2, m1):
                    continue
                
                # 4순위: 새로운 중복 발생 여부 체크
                if self._will_cause_overlap(other_team, m1):
                    penalty += 100
                
                candidates.append((other_team, m2, score_diff + penalty))
        
        if not candidates:
            return None
            
        # 3순위: 점수 차이(score_diff)가 가장 적은 순으로 정렬
        candidates.sort(key=lambda x: x[2])
        return candidates[0][0], candidates[0][1]

    def _check_major_balance(self, team, out_m, in_m):
        temp_majors = [m.is_major for m in team["members"] if m != out_m] + [in_m.is_major]
        return not (all(temp_majors) == False and len(temp_majors) > 0) # 전공자 0명 방지

    def _check_gender_balance(self, team, out_m, in_m):
        temp_genders = [m.gender for m in team["members"] if m != out_m] + [in_m.gender]
        return len(set(temp_genders)) > 1

    def _will_cause_overlap(self, team, new_m):
        prev_tid = self.prev_team_map.get(new_m.id)
        if not prev_tid: return False
        count = sum(1 for m in team["members"] if self.prev_team_map.get(m.id) == prev_tid)
        return count >= 2 # 내가 들어가서 3명이 되면 True