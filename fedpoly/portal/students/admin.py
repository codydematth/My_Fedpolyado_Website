import calendar
from datetime import date
from django.contrib.auth.admin import UserAdmin
from material.admin.options import MaterialModelAdmin
from material.admin.decorators import register
from material.admin.sites import site
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.utils.html import mark_safe

from .forms import StudentFeeAdd
from .models import Student, StudentFee, FeeGroup, FeeType#, FeeSummary

# Register your models here.
site.register(FeeGroup)
icon_name = 'attach_money'

site.register(FeeType)


#admin.site.site_header = "My School Admin"
#admin.site.site_title = "My School Admin Portal"
#admin.site.index_title = "Welcome to My School Portal"


@register(Student)
class StudentAdmin(MaterialModelAdmin):
    """ Display Class of Student Model in Admin Panel"""

# remove delete actions
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # Custom Actions
    def expel_from_school(self, request, queryset):
        rows_updated = queryset.update(is_studying=False)
        if rows_updated == 1:
            message_bit = "1 student was"
        else:
            message_bit = "%s students were" % rows_updated
        self.message_user(request, "%s successfully marked as expelled" % message_bit)

    expel_from_school.short_description = 'Expel From School'
    expel_from_school.allowed_permissions = ('change',)


    def last_fee_submitted(self):
        paid_color = 'green'
        unpaid_color = 'red'

        if self.is_studying:
            obj = self.studentfee_set.last()
            if obj is not None:  # if a record exists
                if obj.valid_until >= date.today():  # if paid this month
                    return format_html(
                        '<span style="color: {};">{}</span>',
                        paid_color,
                        calendar.month_name[int(obj.valid_until.month)] + ', ' + str(obj.valid_until.year)
                    )
                else:  # if not paid this month
                    return format_html(
                        '<span style="color: {};">{}</span>',
                        unpaid_color,
                        calendar.month_name[int(obj.date.month)] + ', ' + str(obj.date.year)
                    )
            else:  # if record does not exists
                return format_html(
                    '<span style="color: {};">{}</span>',
                    unpaid_color,
                    "No Fee Paid"
                )
        else:
            return "Left School"

    last_fee_submitted.short_description = 'Last Fee Submitted'


    def profile_image_display(self, obj):
        return mark_safe(
            '<a href={url} target="_blank"><img src="{url}" width="{width}" \
            height={height} style={style} /></a>'.format(
                url=obj.profile_image.url,
                width=200,
                height=200,
                style='',
            )
        )

    profile_image_display.short_description = "Student Image"

    empty_value_display = '--Empty--'

    list_display = (
        'full_name',
        'father_name',
        'is_studying',
        'gender',
        #'last_fee_submitted'
    )

    list_filter = (
        'is_studying',
        'current_class',
        'gender'
    )

    search_fields = (
        'first_name', 'last_name', 'admission_no'
    )

    ordering = ('first_name',)

    fieldsets = (
        ("School Record", {
            'fields': (
                'admission_no',
                'date_of_admission',
                'is_studying',
                'current_class',
                'profile_image',
                'profile_image_display',  # callable function,
            )
        }),
        ("Personal Information", {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'address')
        }),
        ("Guardian Information", {
            'fields': ('father_name', 'father_cnic', 'fathers_phone_no', 'fathers_proffesion')
        })
    )

    icon_name = 'school'

    actions = ['expel_from_school', ]

    def get_readonly_fields(self, request, obj=None):
        """ Make admission_no and date_of_admission uneditable if
        opened the admin change form but editable if opened
        the create form
        """

        if obj:  # if the object exists then make them readonly
            return ['admission_no', 'date_of_admission', 'profile_image_display']
        else:
            return ['profile_image_display', ]


@register(StudentFee)
class StudentFeeAdmin(MaterialModelAdmin):
    """ Admin display class for the model StudentFee """

    # Delete Delete Action from admin
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    form = StudentFeeAdd

    raw_id_fields = (
        'student',
        'fee_group',
        )
    # Filtering
    list_filter = (
        'valid_until',
    )

    # searching
    search_fields = [
        'student__admission_no',
        'student__first_name',
        'student__last_name',
    ]

    list_display = (
        'student',
        'valid_until',
        'total_amount',
        'date_submitted',
    )

    icon_name = 'money'

# @admin.register(FeeSummary)
# class FeeSummary(admin.ModelAdmin):
#     change_list_template = 'students/admin/fee_summary_change_list.html'
#     date_hierarchy = 'date'

#     def changelist_view(self, request, extra_context=None):
#         response = super().changelist_view(
#             request,
#             extra_context=extra_context,
#         )

#         try:
#             qs = response.context_data['cl'].queryset
#         except (AttributeError, KeyError):
#             return response

#         metrics = {
#             'total': Count('id'),
#             'total_sales': Sum('amount'),
#         }

#         response.context_data['summary'] = list(
#             qs
#                 .values('date')
#                 .annotate(**metrics)
#                 .order_by('date')
#         )

#         response.context_data['summary_total'] = dict(
#             qs.aggregate(**metrics)
#         )

#         return response
