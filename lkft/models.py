# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from django.db import models

class KernelChangeManager(models.Manager):
    def get_queryset(self):
        return super(KernelChangeManager, self).get_queryset().filter(reported=False).order_by('branch', 'trigger_name', '-trigger_number')

class KernelChange(models.Model):
    branch = models.CharField(max_length=255)
    describe = models.CharField(max_length=255)
    reported = models.BooleanField(default=False)
    trigger_name = models.CharField(max_length=255)
    trigger_number = models.IntegerField(default=0)

    # TRIGGER_BUILD_COMPLETED
    # CI_BUILDS_IN_QUEUE / CI_BUILDS_NOT_REPORTED / CI_BUILDS_IN_PROGRESS / CI_BUILDS_COMPLETED
    # HAS_QA_PROJECT_NOT_FOUND / HAS_QA_BUILD_NOT_FOUND / HAS_JOBS_NOT_SUBMITTED / HAS_JOBS_IN_PROGRESS
    # ALL_COMPLETED
    result = models.CharField(max_length=100, null=True, default="NOINFO")
    timestamp = models.DateTimeField(null=True, default=timezone.now)
    duration = models.IntegerField(default=0) # total_seconds

    number_passed = models.IntegerField(default=0)
    number_failed = models.IntegerField(default=0)
    number_assumption_failure = models.IntegerField(default=0)
    number_ignored = models.IntegerField(default=0)
    number_total = models.IntegerField(default=0)
    modules_done = models.IntegerField(default=0)
    modules_total = models.IntegerField(default=0)
    jobs_finished = models.IntegerField(default=0)
    jobs_total = models.IntegerField(default=0)


    def __str__(self):
        return "%s-%s" % (self.branch, self.describe)

    def __unicode__(self):
        return "%s-%s" % (self.branch, self.describe)

    objects = models.Manager() # The default manager
    objects_needs_report = KernelChangeManager() # custom managerKernelChangeManager()


class CiBuildKernelChangeManager(models.Manager):
    def get_builds_per_kernel_change(self, kernel_change=None):
        return super(CiBuildKernelChangeManager, self).get_queryset().filter(kernel_change=kernel_change)


class CiBuild(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    kernel_change = models.ForeignKey(KernelChange, null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True, default=timezone.now)
    duration = models.IntegerField(default=0) # total_seconds
    # CI_BUILD_DELETED / INPROGRESS / SUCCESS / FAILURE / ABORTED
    result = models.CharField(max_length=100, null=True, default="NOINFO")

    display_name = models.CharField(max_length=255, null=True)
    changes_num = models.IntegerField(default=0)

    def __str__(self):
        return "%s#%s" % (self.name, self.number)

    def __unicode__(self):
        return "%s#%s" % (self.name, self.number)

    objects = models.Manager()
    objects_kernel_change = CiBuildKernelChangeManager()


class ReportProject(models.Model):
    # the group that this build belongs to
    group = models.CharField(max_length=100)
    # the name of the qareport project
    name = models.CharField(max_length=100)
    # the slug of the qareport project
    slug = models.CharField(max_length=100)

    project_id = models.IntegerField(default=0)

    is_public = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ("view_eap_projects", "Can see available eap projects"),
            ("view_benchmark_projects", "Can see available benchmark projects"),
            ("admin_projects", "Can do operations on the project, like job resubmission, job cancellation, build cancellation"),
        )

    def __str__(self):
        return "%s#%s" % (self.group, self.name)

    def __unicode__(self):
        return "%s#%s" % (self.group, self.name)

    objects = models.Manager()


class ReportBuild(models.Model):
    # the version of the qareport build
    version = models.CharField(max_length=100)

    qa_project = models.ForeignKey(ReportProject, on_delete=models.CASCADE, null=True)
    kernel_change = models.ForeignKey(KernelChange, on_delete=models.CASCADE, null=True)
    ci_build = models.ForeignKey(CiBuild, on_delete=models.CASCADE, related_name="ci_build", null=True)
    ci_trigger_build = models.ForeignKey(CiBuild, on_delete=models.CASCADE, related_name='trigger_build', null=True)
    finished = models.BooleanField(default=False)

    # JOBSNOTSUBMITTED / JOBSINPROGRESS / JOBSCOMPLETED
    status = models.CharField(max_length=100, null=True, default="NOINFO")

    number_passed = models.IntegerField(default=0)
    number_failed = models.IntegerField(default=0)
    number_assumption_failure = models.IntegerField(default=0)
    number_ignored = models.IntegerField(default=0)
    number_total = models.IntegerField(default=0)
    modules_done = models.IntegerField(default=0)
    modules_total = models.IntegerField(default=0)
    jobs_finished = models.IntegerField(default=0)
    jobs_total = models.IntegerField(default=0)

    # the time the trigger build was started
    started_at = models.DateTimeField(null=True)
    # the time the last job was fetched
    fetched_at = models.DateTimeField(null=True)

    # The id of the qa-report build id
    qa_build_id = models.IntegerField(default=0)

    # the metadata url for the qa-report api, like
    # https://qa-reports.linaro.org/api/builds/63239/metadata/
    metadata_url = models.URLField(null=True)

    def __str__(self):
        return "%s#%s" % (self.qa_project, self.version)

    def __unicode__(self):
        return "%s#%s" % (self.qa_project, self.version)

    objects = models.Manager()


class ReportJob(models.Model):
    job_name = models.CharField(max_length=100)
    job_url = models.URLField(null=True)
    attachment_url = models.URLField(null=True, blank=True)
    results_cached = models.BooleanField(default=False)

    qa_job_id = models.IntegerField(default=0)

    report_build = models.ForeignKey(ReportBuild, on_delete=models.CASCADE, null=True)
    parent_job = models.CharField(max_length=100, null=True, blank=True)
    resubmitted = models.BooleanField(default=False)

    # JOBSNOTSUBMITTED / JOBSINPROGRESS / JOBSCOMPLETED
    status = models.CharField(max_length=100, null=True, default="NOINFO")
    failure_msg = models.TextField(null=True, blank=True)
    # null=True vs blank=True: https://stackoverflow.com/questions/8609192/what-is-the-difference-between-null-true-and-blank-true-in-django
    environment = models.CharField(max_length=100, blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    number_passed = models.IntegerField(default=0)
    number_failed = models.IntegerField(default=0)
    number_assumption_failure = models.IntegerField(default=0)
    number_ignored = models.IntegerField(default=0)
    number_total = models.IntegerField(default=0)
    modules_done = models.IntegerField(default=0)
    modules_total = models.IntegerField(default=0)
    finished_successfully = models.BooleanField(default=False)

    def __str__(self):
        if self.report_build:
            return "%s#%s" % (self.job_name, self.report_build.version)
        else:
            return "%s#%s" % (self.job_name, self.job_url)

    def __unicode__(self):
        if self.report_build:
            return "%s#%s" % (self.job_name, self.report_build.version)
        else:
            return "%s#%s" % (self.job_name, self.job_url)

    objects = models.Manager()


class JobMeta(models.Model):
    qa_job_id = models.IntegerField(default=0)
    kind = models.CharField(
        max_length=32,
        choices=(
            ('ManualResubmit', 'ManualResubmit'),
        ),
        db_index=True,
    )
    resubmission_reason = models.TextField(null=True, blank=True, max_length=256,)


class TestSuite(models.Model):
    report_job = models.ForeignKey(ReportJob)

    name = models.CharField(max_length=256, db_index=True)
    abi = models.CharField(max_length=16, null=True)
    done = models.BooleanField(default=False)
    number_pass = models.IntegerField(default=0)
    number_total = models.IntegerField(default=0)


class TestCase(models.Model):
    # multiple index might be enabled later
    # when the problem is not improved too much
    # or get worse again when the data gets huge
    # https://docs.djangoproject.com/en/3.2/ref/models/options/#indexes
    name = models.CharField(max_length=320, db_index=True)
    result = models.CharField(max_length=64, db_index=True)
    measurement = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    unit = models.CharField(max_length=128, null=True)
    suite = models.CharField(max_length=256, db_index=True)
    job_id = models.CharField(max_length=16, db_index=True)
    lava_nick = models.CharField(max_length=64, db_index=True)

    # failure should be deleted when this testcase deleted
    testsuite = models.ForeignKey(TestSuite, null=True)

    message = models.TextField(null=True, blank=True)
    stacktrace = models.TextField(null=True, blank=True)

    def __unicode__(self):
        if self.measurement:
            return "%s %s %s %s" % (self.name, self.result, self.measurement, self.unit)
        else:
            return "%s %s" % (self.name, self.result)
