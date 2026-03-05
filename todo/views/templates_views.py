from ..models import Todo
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy


# 목록 조회
class TodoListView(ListView):
    model = Todo  # 이 뷰가 사용할 모델 지정 (Todo 테이블 데이터를 조회)

    template_name = "todo/list.html"
    # 데이터를 보여줄 HTML 템플릿 파일 지정

    context_object_name = "todos"
    # 템플릿에서 사용할 변수 이름 (기본값 object_list 대신 todos 사용)

    ordering = ["-created_at"]
    # 데이터 정렬 방식 (created_at 기준 내림차순 → 최신 글이 먼저)

    success_url = reverse_lazy("todo:list")
    # 작업 성공 후 이동할 URL (ListView에서는 보통 사용하지 않지만 설정 가능)


# 생성
class TodoCreateView(CreateView):
    model = Todo
    # 이 뷰에서 사용할 모델 (Todo 테이블에 데이터 생성)

    fields = ["name", "description", "complete", "exp"]
    # HTML form에서 입력받을 모델 필드 정의

    template_name = "todo/create.html"
    # Todo 생성 화면에 사용할 템플릿 파일

    success_url = reverse_lazy("todo:list")
    # 생성이 성공하면 이동할 URL (todo 목록 페이지)


# 상세보기
class TodoDetailView(DetailView):
    model = Todo
    # 이 뷰에서 사용할 모델 지정 (Todo 테이블의 특정 데이터 조회)

    template_name = "todo/detail.html"
    # 조회한 데이터를 보여줄 HTML 템플릿 파일

    context_object_name = "todo"
    # 템플릿에서 사용할 변수 이름
    # 기본값 object 대신 todo라는 이름으로 전달됨


# 업데이트
class TodoUpdateView(UpdateView):
    model = Todo
    # 이 뷰에서 사용할 모델 (Todo 테이블에 데이터 수정)

    fields = ["name", "description", "complete", "exp"]
    # HTML form에서 입력받을 모델 필드 정의

    template_name = "todo/update.html"
    # Todo 수정 화면에 사용할 템플릿 파일

    context_object_name = "todo"
    # 템플릿에서 사용할 변수 이름
    # 기본값 object 대신 todo로 전달됨

    success_url = reverse_lazy("todo:list")
    # 수정이 성공하면 이동할 URL (todo 목록 페이지)
