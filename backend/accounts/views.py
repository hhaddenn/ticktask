from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# The React app has no Django templates, so nothing else would send the
# csrftoken cookie. Calling this endpoint on load gives the frontend a token
# before its first POST (the login), even when the answer is 403.
@ensure_csrf_cookie
@api_view(["GET"])
def me(request):
    return Response({"id": request.user.id, "username": request.user.username})


@api_view(["POST"])
# The project default is IsAuthenticated, but whoever is logging in has no session yet.
@permission_classes([AllowAny])
# DRF only checks CSRF for users who are already authenticated, so the login
# would be unprotected (login CSRF). It must stay BELOW @api_view: @api_view
# marks the view as csrf_exempt, and a @csrf_protect above it skips the check.
@csrf_protect
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        # Generic on purpose: saying which field is wrong would reveal
        # which usernames exist.
        return Response(
            {"detail": "The username or password is wrong."}, status=status.HTTP_400_BAD_REQUEST
        )
    login(request, user)
    return Response({"id": user.id, "username": user.username})


# POST, not GET: logging out changes state, and a GET could be triggered by
# any other site (e.g. an <img> tag). Unlike login_view, no AllowAny and no
# @csrf_protect: only a logged-in user can log out (project default
# IsAuthenticated), and DRF already checks CSRF for authenticated users.
@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)
