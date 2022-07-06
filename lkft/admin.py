# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import KernelChange, CiBuild, ReportBuild, ReportProject, ReportJob, TestCase, JobMeta

# Register your models here.
class KernelChangeAdmin(admin.ModelAdmin):
    list_display = ['branch', 'describe', 'trigger_name', 'trigger_number', 'result', 'reported']
    search_fields = ('branch', 'describe', 'result')


class CiBuildAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'kernel_change', 'result']
    search_fields = ('name', 'number', 'kernel_change__branch', 'kernel_change__describe')


class ReportBuildAdmin(admin.ModelAdmin):
    list_display = ['qa_project', 'version', 'number_passed', 'number_failed', 'number_total', 'modules_done', 'modules_total', 'qa_build_id']
    search_fields = ('qa_project__group', 'qa_project__name', 'qa_project__slug', 'version')


class ReportProjectAdmin(admin.ModelAdmin):
    list_display = ['group', 'name', 'slug', 'project_id']
    search_fields = ['group', 'name', 'slug', 'project_id']


class ReportJobAdmin(admin.ModelAdmin):
    list_display = ['job_name', 'job_url', 'report_build', 'status','resubmitted', 'failure_msg']
    search_fields = ['job_name', 'report_build__version', 'status', 'failure_msg']


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['suite', 'name', 'result', 'measurement', 'unit', 'lava_nick', 'job_id']
    search_fields = ['suite', 'name', 'result', 'measurement', 'unit', 'lava_nick', 'job_id']

class JobMetaAdmin(admin.ModelAdmin):
    list_display = ['qa_job_id', 'kind', 'resubmission_reason']
    search_fields = ['qa_job_id', 'kind', 'resubmission_reason']

admin.site.register(KernelChange, KernelChangeAdmin)
admin.site.register(CiBuild, CiBuildAdmin)
admin.site.register(ReportBuild, ReportBuildAdmin)
admin.site.register(ReportProject, ReportProjectAdmin)
admin.site.register(ReportJob, ReportJobAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(JobMeta, JobMetaAdmin)
