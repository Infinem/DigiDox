from django.contrib import admin

from bot.models import PassportInfo


@admin.register(PassportInfo)
class PassportInfoAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "sex",
        "pass_number",
        "pass_serial",
        "date_of_birth",
        "date_of_issue",
        "date_of_expiry",
        "pinfl",
    )
