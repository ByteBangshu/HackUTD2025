from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    try:
        data = json.loads(request.body.decode())
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")

        if not username or not password:
            return JsonResponse({"error": "Missing fields"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Auto-login after registration
        return JsonResponse({
            "message": "User registered successfully",
            "username": user.username,
            "email": user.email
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body.decode())
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Missing credentials"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                "message": "Login successful",
                "username": user.username,
                "email": user.email
            })
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"})


def check_auth(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse({
            "authenticated": True,
            "username": request.user.username,
            "email": request.user.email
        })
    else:
        return JsonResponse({"authenticated": False})