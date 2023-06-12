from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.forms import CustomUserChangeForm, CustomUserCreationForm
from core.models import MatrimonialProfile, Profile, User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "email",
        "full_name",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "full_name",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "full_name",
                    "password",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
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
    )
    ordering = ("user__email",)
    search_fields = ("email_address",)

    @staticmethod
    def full_name(obj: Profile):
        return obj.user.full_name

    @staticmethod
    def email_address(obj: Profile):
        return obj.user.email


admin.site.register(User, CustomUserAdmin)
admin.site.register(MatrimonialProfile)
