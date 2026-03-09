# Django 인증 관련 함수
# authenticate → 사용자 인증
# login → 세션 로그인 처리
# logout → 세션 로그아웃 처리
from django.contrib.auth import logout

# DRF APIView 사용
from rest_framework.views import APIView

# API 응답 객체
from rest_framework.response import Response

# HTTP 상태 코드
from rest_framework import status

# 모든 사용자 접근 허용
from rest_framework.permissions import AllowAny, IsAuthenticated

# 회원가입 데이터 검증 Serializer
from .serializers import SignupSerializer


# -----------------------------
# 회원가입 API
# -----------------------------
class SignupAPIView(APIView):

    # 로그인하지 않은 사용자도 접근 가능
    permission_classes = [AllowAny]

    # POST 요청 처리
    def post(self, request):

        # 요청 데이터(request.data)를 Serializer에 전달
        serializer = SignupSerializer(data=request.data)

        # 데이터 검증
        # raise_exception=True → 검증 실패 시 자동으로 에러 응답 반환
        serializer.is_valid(raise_exception=True)

        # 검증 완료 후 사용자 생성
        serializer.save()

        # 회원가입 성공 응답
        return Response({"detail": "회원가입 완료"}, status=status.HTTP_201_CREATED)


# -----------------------------
# 세션 로그아웃 API
# -----------------------------
class SessionLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # POST 요청 처리
    def post(self, request):

        # 현재 로그인된 사용자 세션 종료
        logout(request)

        # 로그아웃 성공 응답
        return Response({"detail": "로그아웃(세션 정리)"}, status=status.HTTP_200_OK)
