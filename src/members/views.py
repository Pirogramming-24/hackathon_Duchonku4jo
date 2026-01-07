# members/views.py
from django.views.decorators.http import require_POST
#delete에서 사용자가 링크 입력해서 삭제하는걸 방지하기 위함
from django.shortcuts import render, redirect, get_object_or_404
from .models import Member
from .forms import MemberForm

#멤버 목록 페이지
#멤버 카드 목록만 보여줌
def member_list(request):
    members = Member.objects.all()

    return render(request, 'members/member_list.html', {
        'members': members,
    })

#멤버 생성 페이지
#GET: 멤버 생성 폼 페이지
#POST: 멤버 생성 처리
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('members:member_list')
    else:
        form = MemberForm()

    return render(request, 'members/member_create.html', {
        'form': form,
    })

#멤버 삭제
@require_POST
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    return redirect('members:member_list')
