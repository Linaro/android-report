from django.urls import re_path as url

from . import views

basic_pat = '[a-zA-Z0-9][a-zA-Z0-9_.-]+'
numerical_pat = '[1-9][0-9]+'
gitlab_project_id_pat = '[a-zA-Z0-9][a-zA-Z0-9_\.\-\%\/]+'
urlpatterns = [
    url(r'^$', views.list_projects_simple, name='home'),
    url(r'^boottime-projects/.*$', views.list_boottime_projects, name='list_boottime_projects'),
    url(r'^rc-projects/.*$', views.list_rc_projects, name='list_rc_projects'),
    url(r'^projects/.*$', views.list_projects, name='list_projects'),
    url(r'^projects-simple/.*$', views.list_projects_simple, name='list_projects_simple'),
    url(r'^kernel-changes/$', views.list_kernel_changes, name='list_kernel_changes'),
    # newchanges/$branch/
    url(r'^kernel-changes/(%s)/$' % (basic_pat), views.list_branch_kernel_changes, name='list_branch_kernel_changes'),
    # newchanges/$branch/$describe/
    url(r'^kernel-changes/(%s)/(%s)/$' % (basic_pat, basic_pat), views.list_describe_kernel_changes, name='list_describe_kernel_changes'),
    url(r'^changereportstatus/(%s)/(%s)/$' % (basic_pat, basic_pat), views.mark_kernel_changes_reported, name='mark_kernel_changes_reported'),
    url(r'^builds/.*$', views.list_builds, name='list_builds'),
    url(r'^jobs/.*$', views.list_jobs, name='list_jobs'),
    url(r'^lavalog/(%s)/$' % (numerical_pat), views.get_job_lavalog, name='get_job_lavalog'),
    url(r'^lavalog-lavaurl/.*$', views.get_job_lavalog_lavaurl, name='get_job_lavalog_lavaurl'),
    url(r'^alljobs/.*$', views.list_all_jobs, name='list_all_jobs'),
    url(r'^allmanualjobs/.*$', views.list_all_jobs_resubmitted_manually, name='list_all_manual_jobs'),
    url(r'^file-bug/.*$', views.file_bug, name='file_bug'),
    url(r'^resubmit-job/.*$', views.resubmit_job, name='resubmit_job'),
    url(r'^resubmit-job-manual/(%s)' % (numerical_pat), views.resubmit_job_manual, name='resubmit_job_manual'),
    url(r'^cancel-job/(%s)/$' % (numerical_pat), views.cancel_job, name='cancel_job'),
    url(r'^fetch-job/(%s)/$' % (numerical_pat), views.fetch_job, name='fetch_job'),
    url(r'^cancel-build/(%s)/$' % (numerical_pat), views.cancel_build, name='cancel_build'),
    url(r'^cancel-kernelchange/(%s)/(%s)$' % (basic_pat, basic_pat), views.cancel_kernelchange, name='cancel_kernelchange'),
    # newchanges/$branch/$describe/$build_name/$build_number
    url(r'^newchanges/(%s)/(%s)/(%s)/([0-9]+)' % (basic_pat, basic_pat, basic_pat), views.new_kernel_changes),
    # newchanges/$branch/$describe/$build_name/$build_number
    url(r'^newbuild/(%s)/(%s)/(%s)/([0-9]+)' % (basic_pat, basic_pat, basic_pat), views.new_build, name='new_build'),

    url(r'^gitlab/$', views.gitlab_projects, name='gitlab_projects'),
    url(r'^gitlab/(%s)/$' % gitlab_project_id_pat, views.gitlab_project_pipelines, name='gitlab_progect_pipelines'),
    url(r'^matrix/$', views.matrix, name='matrix'),

    url(r'^aosp/(%s)/$' % (basic_pat), views.list_aosp_versions, name='list_aosp_versions'),
]
