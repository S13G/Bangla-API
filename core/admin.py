from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.forms import CustomUserChangeForm, CustomUserCreationForm
from core.models import Profile, User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "email",
        "full_name",
        "phone_number",
        "is_staff",
        "is_active",
        "is_verified"
    )
    list_filter = (
        "email",
        "phone_number",
        "full_name",
        "is_staff",
        "is_active",
    )
    list_per_page = 30
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "full_name",
                    "phone_number",
                    "password",
                    "is_verified"
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "country",
        "email_address",
        "phone_number"
    )
    list_per_page = 30
    ordering = ("user__email",)
    search_fields = ("email_address",)

    @staticmethod
    def full_name(obj: Profile):
        return obj.user.full_name

    @staticmethod
    def email_address(obj: Profile):
        return obj.user.email

    @staticmethod
    def phone_number(obj: Profile):
        return obj.user.phone_number


admin.site.register(User, CustomUserAdmin)
