#!/usr/bin/env python3

import datetime
import logging

from collections import Counter

from django.core.management.base import BaseCommand, CommandError

from lcr import qa_report
from lcr.settings import QA_REPORT, QA_REPORT_DEFAULT
from lcr.settings import JENKINS, JENKINS_DEFAULT

from lkft.views import thread_pool

logger = logging.getLogger(__name__)

jenkins_def = JENKINS[JENKINS_DEFAULT]
jenkins_api = qa_report.JenkinsApi(jenkins_def.get('domain'), jenkins_def.get('token'), user=jenkins_def.get('user'))

qa_report_def = QA_REPORT[QA_REPORT_DEFAULT]
qa_report_api = qa_report.QAReportApi(qa_report_def.get('domain'), qa_report_def.get('token'))

class Command(BaseCommand):
    help = 'List all the builds with the duration and started time'

    def add_arguments(self, parser):
        parser.add_argument('jenkins_jobname', type=str, nargs='?',
                            default=None)

    def get_build_info(self, build_info):
        build_number = build_info.get('build_number')
        jenkins_jobname = build_info.get('jenkins_jobname')
        build_url = jenkins_api.get_job_url(name=jenkins_jobname, number=build_number)
        build_details = jenkins_api.get_build_details_with_full_url(build_url)
        display_name = build_details.get('displayName')
        started_date = qa_report_api.get_aware_datetime_from_timestamp(int(build_details['timestamp'])/1000).date()
        duration_minutes = datetime.timedelta(milliseconds=build_details['duration']).total_seconds() / 60

        build_name_fields = display_name.strip().split('-')
        #build_number = build_name_fields[0]
        if build_name_fields[2].find('rc') < 0:
            build_describe = '-'.join(build_name_fields[1:3])
            index_branch_start = 3
        else:
            build_describe = '-'.join(build_name_fields[1:4])
            index_branch_start = 4

        pos_config_lkft = 0
        index = 0
        for field in build_name_fields:
            if field != "lkft":
                index = index + 1
                continue

            if build_name_fields[index + 1] == "lkft":
                pos_config_lkft = index + 1
            else:
                pos_config_lkft = index
            break

        build_branch = '-'.join(build_name_fields[index_branch_start:pos_config_lkft])
        build_config = '-'.join(build_name_fields[pos_config_lkft:])
        # build_year, build_mon, build_day = started_date.strip().split('-')
        build_week = started_date.isocalendar()[1]

        build_info.update({'duration': duration_minutes,
             'build_date': started_date,
             'build_week': build_week,
             # 'build_number': build_number,
             'build_describe': build_describe,
             'build_branch': build_branch,
             'build_config': build_config,
            })
        return build_info


    def handle(self, *args, **options):
        jenkins_jobname = options.get('jenkins_jobname')
        jenkins_job_details = jenkins_api.get_build_details_with_cibuild_name(jenkins_jobname)
        first_build = jenkins_job_details.get('firstBuild')
        last_build = jenkins_job_details.get('lastBuild')
        first_build_number = first_build.get('number')
        last_build_number = last_build.get('number')

        builds = []
        for build_number in range(last_build_number, first_build_number - 1,  -1):
            builds.append({
                            'build_number': build_number,
                            'jenkins_jobname': jenkins_jobname})

        thread_pool(func=self.get_build_info, elements=builds)
            # print(f"{display_name}, {start_timestamp}, {duration_minutes}")

        #items = ['build_date', 'build_week', 'build_branch', 'build_describe', 'build_config']
        items = ['build_week', 'build_branch']
        for item in items:
            counter = Counter(build.get(item) for build in builds)
            for key in sorted(counter.keys()):
                print("%s: %d" % (key, counter.get(key)))
            print("===========")