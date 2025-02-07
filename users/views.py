import requests
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import FormView, DetailView, UpdateView
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.messages.views import SuccessMessageMixin
from . import models, forms, mixins


class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request=self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        # user.verify_email()
        return super().form_valid(form)


class LoginView(mixins.LoggedOutOnlyView,
                FormView):
    template_name = "users/login.html"
    form_class = forms.LogInForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request=self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    if request.user:
        messages.info(request, f"See you later {request.user.first_name}")
        logout(request)
        return redirect(reverse("core:home"))


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do : add success message
    except models.User.DoesNotExist:
        # to do : add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = settings.GITHUB_ID
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"

    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user")


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = settings.GITHUB_ID
        client_secret = settings.GITHUB_SECRET
        code = request.GET.get("code", None)
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get access token.")
            else:
                access_token = token_json.get("access_token", None)
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"token {access_token}",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    if email is None:
                        raise GithubException("Please provide an email.")
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(f"Please log in with: {user.login_method}")
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            username=email,
                            email=email,
                            first_name=name,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, "Welcome back!")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile.")
        else:
            raise GithubException("Can't get code.")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    client_id = settings.KAKAO_ID
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&response_type=code")


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code", None)
        client_id = settings.KAKAO_ID
        client_secret = settings.KAKAO_SECRET
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        if code is not None:
            token_request = requests.post(
                f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}&client_secret={client_secret}"
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise KakaoException("Can't get authorization code.")
            else:
                access_token = token_json.get("access_token", None)
                profile_request = requests.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                    },
                )
                profile_json = profile_request.json()
                kakao_account = profile_json.get("kakao_account")
                email = kakao_account.get("email")
                if email is None:
                    raise KakaoException("Please provide an email.")
                properties = profile_json.get("properties")
                nickname = properties.get("nickname")
                profile_img = properties.get("profile_image")

                try:
                    user = models.User.objects.get(email=email)
                    if user.login_method != models.User.LOGIN_KAKAO:
                        raise KakaoException(f"Please log in with: {user.login_method}")
                except models.User.DoesNotExist:
                    user = models.User.objects.create(
                        username=email,
                        email=email,
                        first_name=nickname,
                        login_method=models.User.LOGIN_KAKAO,
                        email_verified=True
                    )
                    user.set_unusable_password()
                    user.save()
                    if profile_img is not None:
                        photo_request = requests.get(profile_img)
                        user.avatar.save(
                            f"{nickname}-avatar", ContentFile(photo_request.content)
                        )
                    else:
                        pass
                login(request, user)
                messages.success(request, f"Welcome back {user.first_name}!")
                return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"        # Important 21.3


class UpdateProfileView(mixins.LoggedInOnlyView,
                        SuccessMessageMixin,
                        UpdateView):

    model = models.User
    template_name = "users/update_profile.html"
    fields = (
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency"
    )
    success_message = "Profile Updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last name"}
        form.fields["avatar"].widget.attrs = {"placeholder": "Avatar"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birthdate"}
        return form


class UpdatePasswordView(mixins.LoggedInOnlyView,
                         mixins.EmailLoginOnlyView,
                         SuccessMessageMixin,
                         PasswordChangeView):

    template_name = "users/update_password.html"
    success_message = "Password changed"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "Confirm new password"}
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()
