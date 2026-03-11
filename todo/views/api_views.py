from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Todo  # 경로변경
from ..serializers import TodoSerializer  # 경로변경
from django.db.models import Q

# ViewSets 사용을 위한 DRF 모듈 import
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


from interaction.models import TodoLike, TodoBookmark, TodoComment

# ---------------------------------------------------------
# DRF action / permission import
# ---------------------------------------------------------
# action
# → ViewSet 안에서 "추가 API"를 만들 때 사용하는 데코레이터
# → 기본 CRUD 외에 커스텀 API를 만들 수 있음
from rest_framework.decorators import action

from ..pagination import CustomPageNumberPagination


# 전체보기
class TodoListAPI(APIView):
    pass


# 생성하기
class TodoCreateAPI(APIView):

    pass


# 상세보기 API
class TodoRetrieveAPI(APIView):

    pass


# 수정하기 API
class TodoUpdateAPI(APIView):

    pass


class TodoDeleteAPI(APIView):

    pass


# ---------------------------------------------------------
# 핵심 ViewSet
# ---------------------------------------------------------
# ModelViewSet
#
# 아래 CRUD가 자동 생성됩니다.
#
# GET    /todos/          → list
# POST   /todos/          → create
# GET    /todos/{id}/     → retrieve
# PUT    /todos/{id}/     → update
# DELETE /todos/{id}/     → destroy
#
# 즉 CRUD API를 자동으로 만들어주는 클래스입니다.
# ---------------------------------------------------------
class TodoViewSet(viewsets.ModelViewSet):

    # -----------------------------------------------------
    # 기본 queryset
    # -----------------------------------------------------
    # Todo 테이블 전체 데이터를 가져옵니다.
    # created_at 기준으로 최신순 정렬
    # queryset = Todo.objects.all().order_by("-created_at")

    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]  # ✅ 로그인한 사람만
    pagination_class = CustomPageNumberPagination  # ✅ 페이지네이션 연결

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(Q(is_public=True) | Q(user=user)).order_by(
            "-created_at"
        )

    # -----------------------------------------------------
    # list API 커스터마이징
    # -----------------------------------------------------
    # 기본 list 응답
    #
    # [
    #   {...},
    #   {...}
    # ]
    #
    # 하지만 JS에서 사용하기 편하도록
    # 아래처럼 응답 구조를 변경했습니다.
    #
    # {
    #   data: [...],
    #   current_page: 1,
    #   page_count: 5,
    #   next: true,
    #   previous: false
    # }
    # -----------------------------------------------------
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):

        # queryset 필터링
        qs = self.filter_queryset(self.get_queryset())

        # pagination 처리
        page = self.paginate_queryset(qs)

        # ---------------------------------------------
        # pagination이 적용된 경우
        # ---------------------------------------------
        if page is not None:

            # serializer 실행
            serializer = self.get_serializer(
                page,
                many=True,
                context={"request": request},
            )

            return Response(
                {
                    "data": serializer.data,
                    # 현재 페이지
                    "current_page": int(request.query_params.get("page", 1)),
                    # 전체 페이지 수
                    "page_count": self.paginator.page.paginator.num_pages,
                    # 다음 페이지 존재 여부
                    "next": self.paginator.get_next_link() is not None,
                    # 이전 페이지 존재 여부
                    "previous": self.paginator.get_previous_link() is not None,
                }
            )

        # ---------------------------------------------
        # pagination이 없는 경우
        # ---------------------------------------------
        serializer = self.get_serializer(
            qs,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "data": serializer.data,
                "current_page": 1,
                "page_count": 1,
                "next": False,
                "previous": False,
            }
        )

    # -----------------------------------------------------
    # 좋아요 토글 API
    # -----------------------------------------------------
    # URL
    #
    # POST /todo/viewsets/view/<id>/like/
    #
    # detail=True
    # → 특정 Todo 대상 API
    #
    # permission_classes=[IsAuthenticated]
    # → 로그인한 사용자만 가능
    #
    # get_or_create 패턴
    # → 없으면 생성
    # → 있으면 삭제
    #
    # 즉
    # 좋아요 ON / OFF 토글 기능
    # -----------------------------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):

        # 현재 Todo 가져오기
        todo = self.get_object()

        # 로그인한 사용자
        user = request.user

        # 좋아요 존재 확인
        obj, created = TodoLike.objects.get_or_create(todo=todo, user=user)

        # 새로 생성된 경우 → 좋아요 ON
        if created:
            liked = True

        # 이미 존재 → 삭제 → 좋아요 OFF
        else:
            obj.delete()
            liked = False

        # 전체 좋아요 개수 계산
        like_count = TodoLike.objects.filter(todo=todo).count()

        # 응답
        return Response({"liked": liked, "like_count": like_count})

    # -----------------------------------------------------
    # 북마크 토글 API
    # -----------------------------------------------------
    # URL
    #
    # POST /todo/viewsets/view/<id>/bookmark/
    #
    # 좋아요와 동일한 구조
    # -----------------------------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):

        # 현재 Todo
        todo = self.get_object()

        # 로그인 사용자
        user = request.user

        # 북마크 생성 또는 조회
        obj, created = TodoBookmark.objects.get_or_create(todo=todo, user=user)

        # 북마크 ON
        if created:
            bookmarked = True

        # 북마크 OFF
        else:
            obj.delete()
            bookmarked = False

        # 전체 북마크 수
        bookmark_count = TodoBookmark.objects.filter(todo=todo).count()

        return Response({"bookmarked": bookmarked, "bookmark_count": bookmark_count})

    # -----------------------------------------------------
    # 댓글 등록 API
    # -----------------------------------------------------
    # URL
    #
    # POST /todo/viewsets/view/<id>/comments/
    #
    # request.data
    # → 클라이언트에서 보낸 JSON 데이터
    #
    # {
    #   "content": "댓글 내용"
    # }
    # -----------------------------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):

        # Todo 가져오기
        todo = self.get_object()

        # 로그인 사용자
        user = request.user

        # 댓글 내용 가져오기
        content = (request.data.get("content") or "").strip()

        # 댓글 내용 검증
        if not content:
            return Response({"detail": "content is required"}, status=400)

        # 댓글 생성
        TodoComment.objects.create(todo=todo, user=user, content=content)

        # 댓글 개수 계산
        comment_count = TodoComment.objects.filter(todo=todo).count()

        return Response({"comment_count": comment_count})
