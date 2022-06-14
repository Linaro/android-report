## https://docs.djangoproject.com/en/1.11/topics/db/managers/
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands
## https://medium.com/@bencleary/django-scheduled-tasks-queues-part-1-62d6b6dc24f8
## https://medium.com/@bencleary/django-scheduled-tasks-queues-part-2-fc1fb810b81d
## https://medium.com/@kevin.michael.horan/scheduling-tasks-in-django-with-the-advanced-python-scheduler-663f17e868e6
## https://django-background-tasks.readthedocs.io/en/latest/
# VtsKernelLinuxKselftest#timers_set-timer-lat_32bit
import pdb
import datetime
import json
import logging
import os
import re
import yaml
import datetime
import subprocess

from django.core.management.base import BaseCommand, CommandError

from django.utils.timesince import timesince

from lkft.models import KernelChange, CiBuild, ReportBuild

from lcr import qa_report

from lcr.settings import QA_REPORT, QA_REPORT_DEFAULT, BUILD_WITH_JOBS_NUMBER

from lkft.views import get_test_result_number_for_build, get_lkft_build_status, get_classified_jobs
from lkft.views import extract
from lkft.views import get_result_file_path
from lkft.views import download_attachments_save_result
from lkft.views import get_build_metadata
from lkft.views import get_build_kernel_version, parse_kernel_version_string
from lkft.lkft_config import get_version_from_pname, get_kver_with_pname_env
from lkft.reportconfig import get_all_report_kernels, get_all_report_projects

logger = logging.getLogger(__name__)

qa_report_def = QA_REPORT[QA_REPORT_DEFAULT]
qa_report_api = qa_report.QAReportApi(qa_report_def.get('domain'), qa_report_def.get('token'))
jenkins_api = qa_report.JenkinsApi('ci.linaro.org', None)

rawkernels = get_all_report_kernels()
projectids = get_all_report_projects()

def do_boilerplate(output):
    output.write("\n\nFailure Key:\n")
    output.write("--------------------\n")
    output.write("I == Investigation\nB == Bug#, link to bugzilla\nF == Flakey\nU == Unexpected Pass\n\n")

# a flake entry
# name, state, bugzilla
def process_flakey_file(path_flakefile):
    Dict44 = {'version' : 4.4 , 'flakelist' : [] }
    Dict49 = {'version' : 4.9 , 'flakelist' : [] }
    Dict414 = {'version' : 4.14, 'flakelist' : [] }
    Dict419 = {'version' : 4.19, 'flakelist' : [] }
    Dict54 = {'version' : 5.4, 'flakelist' : [] }
    Dict510 = {'version' : 5.10, 'flakelist' : [] }
    flakeDicts = [Dict44, Dict49, Dict414, Dict419, Dict54, Dict510]

    kernelsmatch = re.compile('[0-9]+.[0-9]+')
    androidmatch = re.compile('ANDROID[0-9]+|AOSP')
    hardwarematch = re.compile('HiKey|db845|HiKey960')
    allmatch = re.compile('ALL')
    #pdb.set_trace()

    f_flakefile = open(path_flakefile, "r")
    Lines = f_flakefile.readlines()
    f_flakefile.close()
    for Line in Lines:
        newstate = ' '
        if Line[0] == '#':
            continue
        if Line[0] == 'I' or Line[0] == 'F' or Line[0] == 'B' or Line[0] == 'E':
            newstate = Line[0]
            Line = Line[2:]
        m = Line.find(' ')
        if m:
            testname = Line[0:m]
            Line = Line[m:]
            testentry = {'name' : testname, 'state': newstate, 'board': [], 'androidrel':[] }
            if Line[0:4] == ' ALL':
               Line = Line[5:]
               Dict44['flakelist'].append(testentry)
               Dict49['flakelist'].append(testentry)
               Dict414['flakelist'].append(testentry)
               Dict419['flakelist'].append(testentry)
               Dict54['flakelist'].append(testentry)
               Dict510['flakelist'].append(testentry)
            else:
               n = kernelsmatch.match(Line)
               if n:
                  Line = Line[n.end():]
                  for kernel in n:
                      for Dict in flakeDicts:
                          if kernel == Dict['version']:
                              Dict['flakelist'].append(testentry)
               else:
                   continue 
            if Line[0:3] == 'ALL':
               Line = Line[4:]
               testentry['board'].append("HiKey")
               testentry['board'].append("HiKey960")
               testentry['board'].append("db845")
            else:
               h = hardwarematch.findall(Line)
               if h:
                  for board in h:
                      testentry['board'].append(board)
               else:
                   continue
            a = allmatch.search(Line)
            if a:
               testentry['androidrel'].append('Android8') #O
               testentry['androidrel'].append('Android9') #P
               testentry['androidrel'].append('Android10') #Q
               testentry['androidrel'].append('Android11') #R
               testentry['androidrel'].append('Android12') #S
               testentry['androidrel'].append('AOSP')
            else:
               a = androidmatch.findall(Line)
               if a:
                  for android in a:
                      testentry['androidrel'].append(android)
               else:
                   continue
        else:
            continue 
       
    return flakeDicts

# take the data dictionaries, the testcase name and ideally the list of failures
# and determine how to classify a test case. This might be a little slow espeically
# once linked into bugzilla
def classifyTest(flakeDicts, testcasename, hardware, kernel, android):
    for dict in flakeDicts:
        if dict['version'] == kernel:
            break
    #pdb.set_trace()
    foundboard = 0
    foundandroid = 0
    #if testcasename == 'VtsKernelLinuxKselftest.timers_set-timer-lat_64bit':
    #    pdb.set_trace()
    #if testcasename == 'android.webkit.cts.WebChromeClientTest#testOnJsBeforeUnloadIsCalled#arm64-v8a':
    #    pdb.set_trace()
    for flake in dict['flakelist']:
        if flake['name'] == testcasename:
            for board in flake['board'] :
                if board == hardware:
                    foundboard = 1
                    break
            for rel in flake['androidrel']:
                if rel == android:
                    foundandroid = 1
                    break
            if foundboard == 1 and foundandroid == 1:
                return flake['state']
            else:
                return 'I'
    return 'I'


def find_best_two_runs(builds, project_name, project, exact_ver1="", exact_ver2="", reverse_build_order=False, no_check_kernel_version=False):
    goodruns = []
    bailaftertwo = 0
    number_of_build_with_jobs = 0
    baseExactVersionDict=None
    nextVersionDict=None

    if len(exact_ver1) > 0 and exact_ver1 !='No':
        baseExactVersionDict = parse_kernel_version_string(exact_ver1)

    sorted_builds = sorted(builds, key=get_build_kernel_version, reverse=True)
    for build in sorted_builds:
        if bailaftertwo == 2:
            break
        elif bailaftertwo == 0 :
            baseVersionDict = parse_kernel_version_string(build['version'])
            if baseExactVersionDict is not None \
                    and not baseVersionDict['versionString'].startswith(exact_ver1):
                logger.info('Skip the check as it is not the specified version for %s %s', project_name, build['version'])
                continue
            # print "baseset"
        elif bailaftertwo == 1 :
            nextVersionDict = parse_kernel_version_string(build['version'])
            if exact_ver2 is not None \
                    and not nextVersionDict['versionString'].startswith(exact_ver2):
                # for case that second build version specified, but not this build
                logger.info('Skip the check as it is not the specified version for %s %s', project_name, build['version'])
                continue
            elif not no_check_kernel_version and nextVersionDict['Extra'] == baseVersionDict['Extra']:
                # for case that need to check kernel version, and all major, minro, extra version are the same
                # then needs to check if the rc version is the same too
                nextRc = nextVersionDict.get('rc')
                baseRc = baseVersionDict.get('rc')
                if (nextRc is None and baseRc is None) \
                    or (nextRc is not None and baseRc is not None and nextRc == baseRc):
                    # for case that neither build is rc version or both have the same rc version
                    logger.info('Skip the check as it has the same version for %s %s', project_name, build['version'])
                    continue
                else:
                    # for case that the rc version are different, like
                    # 1. one build is rc version, but another is not rc version
                    # 2. both are rc versions, but are different rc versions
                    pass
            else:
                # for cases that
                # 1. the second build version not specified, or this build has the same version like the specified second build version
                # 2. no need to check the kernel version, or the kernel version is different, either extra version or the rc version
                pass

        logger.info("Checking for %s, %s", project_name, build.get('version'))
        build['created_at'] = qa_report_api.get_aware_datetime_from_str(build.get('created_at'))
        jobs = qa_report_api.get_jobs_for_build(build.get("id"))
        jobs_to_be_checked = get_classified_jobs(jobs=jobs).get('final_jobs')
        build_status = get_lkft_build_status(build, jobs_to_be_checked)
        #build_status = get_lkft_build_status(build, jobs)
        jobs=jobs_to_be_checked
        if build_status['has_unsubmitted']:
            logger.info('Skip the check as the build has unsubmitted jobs: %s %s', project_name, build['version'])
            continue
        elif build_status['is_inprogress']:
            logger.info('Skip the check as the build is still inprogress: %s %s', project_name, build['version'])
            continue
           
        build['jobs'] = jobs
        if not jobs:
            continue

        download_attachments_save_result(jobs=jobs)
            
        failures = {}
       
        #pdb.set_trace()
        total_jobs_finished_number = 0
        build['numbers'] = qa_report.TestNumbers()
        for job in jobs:
            jobstatus = job['job_status']
            jobfailure = job['failure']
            # for some failed cases, numbers are not set for the job
            job_numbers = job.get('numbers', None)
            if jobstatus == 'Complete' and jobfailure is None and \
                    job_numbers is not None and job_numbers.get('finished_successfully'):
                total_jobs_finished_number = total_jobs_finished_number + 1

            result_file_path = get_result_file_path(job=job)
            if not result_file_path or not os.path.exists(result_file_path):
                continue
            # now tally then move onto the next job
            kernel_version = get_kver_with_pname_env(prj_name=project_name, env=job.get('environment'))

            platform = job.get('environment').split('_')[0]
            metadata = {
                          'job_id': job.get('job_id'),
                          'qa_job_id': qa_report_api.get_qa_job_id_with_url(job_url=job.get('url')),
                          'result_url': job.get('attachment_url'),
                          'lava_nick': job.get('lava_config').get('nick'),
                          'kernel_version': kernel_version,
                          'platform': platform,
                        }
            extract(result_file_path, failed_testcases_all=failures, metadata=metadata)
            # this line overrides the numbers set within the function of download_attachments_save_result
            test_numbers = qa_report.TestNumbers()
            test_numbers.addWithHash(job['numbers'])
            job['numbers'] = test_numbers
            build['numbers'].addWithTestNumbers(test_numbers)

        # now let's see what we have. Do we have a complete yet?
        print("Total Finished Jobs Number / Total Jobs Number: %d / %d" % (total_jobs_finished_number, len(jobs)))

        # when the finished successfully jobs number is the same as the number of all jobs
        # it means all the jobs are finished successfully, the build is OK to be used for comparisonfin
        if len(jobs) == total_jobs_finished_number and build['numbers'].modules_total > 0:
            #pdb.set_trace()

            if nextVersionDict is not None:
                # add for the second build
                if exact_ver2 is not None:
                    if reverse_build_order:
                        # find regression in exact_ver2 compare to exact_ver1
                        goodruns.append(build)
                    else:
                        # find regression in exact_ver1 compare to exact_ver2
                        goodruns.insert(0, build)

                elif int(nextVersionDict['Extra']) > int(baseVersionDict['Extra']):
                    # for the case the second build is newer than the first build
                    # first build is goodruns[0], second build is goodruns[1]
                    # normally, the builds are sorted with the newest kernel version as the first build.
                    goodruns.append(build)
                else:
                    # for the case the second build is older than or equal to the first build
                    goodruns.insert(0, build)
            else:
                # add for the first build
                goodruns.append(build)

            bailaftertwo += 1
            logger.info("found one valid build bailaftertwo=%s %s, %s", bailaftertwo, project_name, build.get('version'))
        elif bailaftertwo == 0 and exact_ver1 is not None and baseVersionDict is not None and baseVersionDict.get('versionString') == exact_ver1:
            # found the first build with exact_ver1, but that build does not have all jobs finished successfully
            # stop the loop for builds to find anymore
            bailaftertwo += 1

            goodruns.append(build)
            logger.info("The build specified with --exact-version-1 is not a valid build: %s, %s", project_name, build.get('version'))
            return goodruns
        elif bailaftertwo == 1 and exact_ver2 is not None and nextVersionDict is not None and nextVersionDict.get('versionString') == exact_ver2:
            # found the second build with exact_ver2, but that build does not have all jobs finished successfully
            # stop the loop for builds to find anymore
            bailaftertwo += 1
            logger.info("The build specified with --exact-version-2 is not a valid build: %s, %s", project_name, build.get('version'))
            return goodruns
        else:
            # for case that no completed build found, continute to check the next build
            logger.info("Not one valid will continue: %s, %s", project_name, build.get('version'))
            continue

        #pdb.set_trace()
        failures_list = []
        for module_name in sorted(failures.keys()):
            failures_in_module = failures.get(module_name)
            for test_name in sorted(failures_in_module.keys()):
                failure = failures_in_module.get(test_name)
                abi_stacktrace = failure.get('abi_stacktrace')
                abis = sorted(abi_stacktrace.keys())

                stacktrace_msg = ''
                if (len(abis) == 2) and (abi_stacktrace.get(abis[0]) != abi_stacktrace.get(abis[1])):
                    for abi in abis:
                        stacktrace_msg = '%s\n\n%s:\n%s' % (stacktrace_msg, abi, abi_stacktrace.get(abi))
                else:
                    stacktrace_msg = abi_stacktrace.get(abis[0])

                failure['abis'] = abis
                failure['stacktrace'] = stacktrace_msg.strip()
                failure['module_name'] = module_name
                failures_list.append(failure)

        #pdb.set_trace()
        android_version = get_version_from_pname(pname=project.get('name'))
        build['failures_list'] = failures_list

    return goodruns

# Try to find the regressions in goodruns[1]
# compared to the result in goodruns[0]
def find_regressions(goodruns):
    runA = goodruns[1]
    failuresA = runA['failures_list']
    runB = goodruns[0]
    failuresB = runB['failures_list']
    regressions = []
    for failureA in failuresA:
        match = 0
        testAname = failureA['test_name']
        for failureB in failuresB:
            testBname = failureB['test_name']
            if testAname == testBname:
                match = 1
                break
        if match != 1 :
            # for failures in goodruns[1],
            # if they are not reported in goodruns[0],
            # then they are regressions
            regressions.append(failureA)
    
    return regressions

def find_antiregressions(goodruns):
    runA = goodruns[1]
    failuresA = runA['failures_list']
    runB = goodruns[0]
    failuresB = runB['failures_list']
    antiregressions = []
    for failureB in failuresB:
        match = 0
        for failureA in failuresA:
            testAname = failureA['test_name']
            testBname = failureB['test_name']
            if testAname == testBname:
                match = 1
                break
        if match != 1 :
            antiregressions.append(failureB)
    
    return antiregressions


"""  Example project_info dict
                    {'project_id': 210, 
                     'hardware': 'hikey',
                     'OS' : 'Android10',
                     'branch' : 'Android-4.19-q',},
"""

def print_androidresultheader(output, project_info, run, priorrun):
    output.write("    " + project_info['OS'] + "/" + project_info['hardware'] + " - " )
    output.write("Current:" + run['version'] + "  Prior:" + priorrun['version']+"\n")

    build_metadata = get_build_metadata(build_metadata_url=run.get('metadata'))
    prior_build_metadata = get_build_metadata(build_metadata_url=priorrun.get('metadata'))


    def get_last_of_metadata(metadata):
        if metadata is None:
            return None
        if type(metadata) is str:
            return metadata
        if type(metadata) is list:
            return metadata[-1]

    if build_metadata.get('gsi_fingerprint', None):
        output.write("    " + "GSI Fingerprint:" + " - " )
        if get_last_of_metadata(build_metadata.get('gsi_fingerprint')) == get_last_of_metadata(prior_build_metadata.get('gsi_fingerprint', 'UNKNOWN')):
            output.write("Current:" + get_last_of_metadata(build_metadata.get('gsi_fingerprint')) + " == Prior:" + get_last_of_metadata(prior_build_metadata.get('gsi_fingerprint', 'UNKNOWN')) + "\n")
        else:
            output.write("Current:" + get_last_of_metadata(build_metadata.get('gsi_fingerprint')) + " != Prior:" + get_last_of_metadata(prior_build_metadata.get('gsi_fingerprint', 'UNKNOWN')) + "\n")

    if build_metadata.get('vendor_fingerprint', None):
        output.write("    " + "Vendor Fingerprint:" + " - " )
        if get_last_of_metadata(build_metadata.get('vendor_fingerprint')) == get_last_of_metadata(prior_build_metadata.get('vendor_fingerprint', 'UNKNOWN')):
            output.write("Current:" + get_last_of_metadata(build_metadata.get('vendor_fingerprint')) + " == Prior:" + get_last_of_metadata(prior_build_metadata.get('vendor_fingerprint', 'UNKNOWN')) + "\n")
        else:
            output.write("Current:" + get_last_of_metadata(build_metadata.get('vendor_fingerprint')) + " != Prior:" + get_last_of_metadata(prior_build_metadata.get('vendor_fingerprint', 'UNKNOWN')) + "\n")

    if build_metadata.get('cts_version', None):
        output.write("    " + "CTS Version:" + " - " )
        if get_last_of_metadata(build_metadata.get('cts_version', 'UNKNOWN')) == get_last_of_metadata(prior_build_metadata.get('cts_version', 'UNKNOWN')):
            output.write("Current:" + get_last_of_metadata(build_metadata.get('cts_version', 'UNKNOWN')) + " == Prior:" + get_last_of_metadata(prior_build_metadata.get('cts_version', 'UNKNOWN')) + "\n")
        else:
            output.write("Current:" + get_last_of_metadata(build_metadata.get('cts_version', 'UNKNOWN')) + " != Prior:" + get_last_of_metadata(prior_build_metadata.get('cts_version', 'UNKNOWN')) + "\n")

    # there is the case like presubmit jobs that there are not vts is run
    if build_metadata.get('vts_version', None):
        output.write("    " + "VTS Version:" + " - " )
        if get_last_of_metadata(build_metadata.get('vts_version', 'UNKNOWN')) == get_last_of_metadata(prior_build_metadata.get('vts_version', 'UNKNOWN')):
            output.write("Current:" + get_last_of_metadata(build_metadata.get('vts_version', 'UNKNOWN')) + " == Prior:" + get_last_of_metadata(prior_build_metadata.get('vts_version', 'UNKNOWN')) + "\n")
        else:
            output.write("Current:" + get_last_of_metadata(build_metadata.get('vts_version', 'UNKNOWN')) + " != Prior:" + get_last_of_metadata(prior_build_metadata.get('vts_version', 'UNKNOWN')) + "\n")


def add_unique_kernel(unique_kernels, kernel_version, combo, unique_kernel_info):
    #pdb.set_trace()
    if kernel_version not in unique_kernels:
        unique_kernels.append(kernel_version)
        newlist = []
        newlist.append(combo)
        unique_kernel_info[kernel_version] = newlist
    else:
        kernellist= unique_kernel_info[kernel_version]
        kernellist.append(combo)


def report_results(output, run, regressions, combo, priorrun, flakes, antiregressions, trim_number=0):
    #pdb.set_trace()
    numbers = run['numbers']
    project_info = projectids[combo]
    output.write(project_info['branch'] + "\n")
    print_androidresultheader(output, project_info, run, priorrun)
    #pdb.set_trace()
    if numbers.modules_total == 0:
        logger.info("Skip printing the regressions information as this build might not have any cts vts jobs run")
        return
    output.write("    " + str(len(antiregressions)) + " Prior Failures now pass\n")
    output.write("    " + str(len(regressions)) + " Regressions of ")
    output.write(str(numbers.number_failed) + " Failures, ")
    output.write(str(numbers.number_passed) + " Passed, ")
    if numbers.number_ignored > 0 :
        output.write(str(numbers.number_ignored) + " Ignored, ")
    if numbers.number_assumption_failure > 0 :
        output.write(str(numbers.number_assumption_failure) + " Assumption Failures, ")
    output.write(str(numbers.number_total) + " Total\n" )
    output.write("    " + "Modules Run: " + str(numbers.modules_done) + " Module Total: " + str(numbers.modules_total) + "\n")

    regressions_failure = [ failure for failure in regressions if failure.get('result') == 'fail' ]
    regressions_assumption = [ failure for failure in regressions if failure.get('result') == 'ASSUMPTION_FAILURE' ]

    def print_regressions(output, target_regressions, flakes, project_info, trim_number=0):
        if 'baseOS' in project_info: 
            OS = project_info['baseOS']
        else:
            OS = project_info['OS']
        if trim_number > 0 and len(target_regressions) > trim_number:
            print_number=int(trim_number/2)
            for regression in target_regressions[:print_number]:
                # pdb.set_trace()
                testtype = classifyTest(flakes, regression['test_name'], project_info['hardware'], project_info['kern'], OS)
                output.write("        " + testtype + " " + regression['module_name'] +"." + regression['test_name'] + "\n")
            output.write("    [...%d lines removed...]\n" % (len(target_regressions) - print_number * 2))
            for regression in target_regressions[-print_number:]:
                # pdb.set_trace()
                testtype = classifyTest(flakes, regression['test_name'], project_info['hardware'], project_info['kern'], OS)
                output.write("        " + testtype + " " + regression['module_name'] +"." + regression['test_name'] + "\n")
        else:
            for regression in target_regressions:
                # pdb.set_trace()
                testtype = classifyTest(flakes, regression['test_name'], project_info['hardware'], project_info['kern'], OS)
                output.write("        " + testtype + " " + regression['module_name'] +"." + regression['test_name'] + "\n")

    if len(regressions_failure) > 0:
        output.write("    " + str(len(regressions_failure)) + " Test Regressions:\n")
        print_regressions(output, regressions_failure, flakes, project_info, trim_number=trim_number)
    if len(regressions_assumption) > 0:
        output.write("    " + str(len(regressions_assumption)) + " New Assumption Failures:\n")
        print_regressions(output, regressions_assumption, flakes, project_info, trim_number=trim_number)

    if len(regressions) > 0:
        output.write("    " + "Current jobs\n")
        for job in run['jobs']:
            output.write("        " + "%s %s\n" % (job.get('external_url'), job.get('name')))
        output.write("    " + "Prior jobs\n")
        for job in priorrun['jobs']:
            output.write("        " + "%s %s\n" % (job.get('external_url'), job.get('name')))

    output.write("\n")


def report_kernels_in_report(path_outputfile, unique_kernels, unique_kernel_info, work_total_numbers):
    with open(path_outputfile, "w") as f_outputfile:
        f_outputfile.write("\n")
        f_outputfile.write("\n")
        f_outputfile.write("Kernel/OS Combo(s) in this report:\n")
        for kernel in unique_kernels:
            f_outputfile.write("    " + kernel+ " - ")
            combolist = unique_kernel_info[kernel]
            intercombo = iter(combolist)
            combo=combolist[0]
            f_outputfile.write(combo)
            next(intercombo)
            for combo in intercombo:
                f_outputfile.write(", "+ combo)
            f_outputfile.write("\n")

        f_outputfile.write("\n")
        f_outputfile.write("%d Prior Failures now pass\n" % work_total_numbers.number_antiregressions)
        f_outputfile.write("%d Regressions of %d Failures, %d Passed, %d Ignored, %d Assumption Failures, %d Total\n" % (
                                work_total_numbers.number_regressions,
                                work_total_numbers.number_failed,
                                work_total_numbers.number_passed,
                                work_total_numbers.number_ignored,
                                work_total_numbers.number_assumption_failure,
                                work_total_numbers.number_total))


class Command(BaseCommand):
    help = 'returns Android Common Kernel Regression Report for specific kernels'

    def add_arguments(self, parser):
        parser.add_argument('kernel', type=str, help='Kernel version')
        parser.add_argument('outputfile', type=str, help='Output File')
        parser.add_argument('flake', type=str, help='flakey file')
        parser.add_argument("--no-check-kernel-version",
                help="Specify if the kernel version for the build should be checked.",
                dest="no_check_kernel_version",
                action='store_true',
                required=False)

        parser.add_argument("--exact-version-1",
                help="Specify the exact kernel version for the first build",
                dest="exact_version_1",
                default="",
                required=False)
        parser.add_argument("--exact-version-2",
                help="Specify the exact kernel version for the second build",
                dest="exact_version_2",
                default="",
                required=False)

        parser.add_argument("--trim-number",
                help="Specify how many test cases to be printed",
                dest="trim_number",
                type=int,
                default=0,
                required=False)

        parser.add_argument("--reverse-build-order",
                help="When both --exact-version-1 and --exact-version-2 specified,\
                 normally will try to find the regressions in --exact-version-1 against --exact-version-2,\
                 but with this option, it will try to find the regressions in --exact-version-2\
                 agains the build of --exact-version-1",
                dest="reverse_build_order",
                action='store_true',
                required=False)

        parser.add_argument("--qareport-project",
                help="Specify the QA Report project to check",
                dest="qareport_project",
                default=None,
                required=False)


    def handle(self, *args, **options):
        kernel = options['kernel']
        path_outputfile = options['outputfile']
        scribblefile = path_outputfile + str(".scribble")
        f_errorprojects = path_outputfile + str(".errorprojects")
        path_flakefile = options['flake']

        no_check_kernel_version = options.get('no_check_kernel_version')
        opt_exact_ver1 = options.get('exact_version_1')
        opt_exact_ver2 = options.get('exact_version_2')
        trim_number = options.get('trim_number')
        reverse_build_order = options.get('reverse_build_order')
        qareport_project = options.get('qareport_project')

        # map kernel to all available kernel, board, OS combos that match
        work = []
        unique_kernel_info = { }
        unique_kernels=[]

        if qareport_project:
            work = [ qareport_project ]
        else:
            work = rawkernels.get(kernel)
            if work is None:
                print("The specified kernel is not supported yet:", kernel)
                print("The supported kernels are:", ' '.join(rawkernels.keys()))
                return

        flakes = process_flakey_file(path_flakefile)

        output = open(scribblefile, "w")
        output_errorprojects = open(f_errorprojects, "w")
        do_boilerplate(output)

        work_total_numbers = qa_report.TestNumbers()
        trimmed_lines = 0
        for combo in work:
            project_info = projectids[combo]
            project_id = project_info.get('project_id', None)
            if project_id is not None:
                logger.info("Try to get project %s with project_id %s", combo, project_id)
                project =  qa_report_api.get_project(project_id)
            else:
                project_group = project_info.get('group', None)
                project_slug = project_info.get('slug', None)
                project_fullname = qa_report_api.get_project_full_name_with_group_and_slug(project_group, project_slug)

                logger.info("Try to get project %s with project_fullname %s", combo, project_fullname)
                project =  qa_report_api.get_project_with_name(project_fullname)

            if project is None:
                print("\nNOTE: project for " + combo + " was not found, please check and try again\n")
                output_errorprojects.write("\nNOTE: project " + combo+ " was not found, please check and try again\n\n")
                continue

            project_id = project.get('id')
            builds = qa_report_api.get_all_builds(project_id)
            
            project_name = project.get('name')
            goodruns = find_best_two_runs(builds, project_name, project,
                                          exact_ver1=opt_exact_ver1, exact_ver2=opt_exact_ver2, reverse_build_order=reverse_build_order,
                                          no_check_kernel_version=no_check_kernel_version)
            if len(goodruns) < 2 :
                print("\nNOTE: project " + project_name+ " did not have 2 good runs\n")
                if opt_exact_ver1 is not None:
                    output_errorprojects.write("NOTE: project " + project_name + " did not have results for %s\n" % (opt_exact_ver1))
                else:
                    output_errorprojects.write("NOTE: project " + project_name + " did not have results for %s\n" % (kernel))
                if len(goodruns) == 1:
                    # assuming that it's the latest build a invalid build
                    # and that caused only one goodruns returned.
                    # if the first latest build is a valid build,
                    # then the second build should be alwasy there
                    run = goodruns[0]
                    output_errorprojects.write(project_info['branch'] + "\n")
                    output_errorprojects.write("    " + project_info['OS'] + "/" + project_info['hardware'] + " - " + "Current:" + run['version'] + "\n")
                    output_errorprojects.write("    Current jobs\n")

                    for job in run['jobs']:
                        output_errorprojects.write("        " + "%s %s %s\n" % (job.get('external_url'), job.get('name'), job.get("job_status")))
                        if job.get('failure') and job.get('failure').get('error_msg'):
                            output_errorprojects.write("            " + "%s\n" % (job.get('failure').get('error_msg')))
                    output_errorprojects.write("    Want to resubmit the failed jobs for a try? https://android.linaro.org/lkft/jobs/?build_id=%s&fetch_latest=true\n" %  run.get('id'))
                elif len(goodruns) == 0 and opt_exact_ver1 is not None:
                    output_errorprojects.write(project_info['branch'] + "\n")
                    output_errorprojects.write("    " + project_info['OS'] + "/" + project_info['hardware'] + " - build for kernel version " + opt_exact_ver1 + " is not found or still in progress!"+ "\n")
                    output_errorprojects.write("    Builds list: https://android.linaro.org/lkft/builds/?project_id=%s&fetch_latest=true\n" %  project_id)
                elif len(goodruns) == 0:
                    output_errorprojects.write(project_info['branch'] + "\n")
                    output_errorprojects.write("    " + project_info['OS'] + "/" + project_info['hardware'] + " - no build available for " + kernel + "!\n")
                output_errorprojects.write("\n")
            else:
                add_unique_kernel(unique_kernels, goodruns[1]['version'], combo, unique_kernel_info)
                regressions = find_regressions(goodruns)
                antiregressions = find_antiregressions(goodruns)
                goodruns[1].get('numbers').number_regressions = len(regressions)
                goodruns[1].get('numbers').number_antiregressions = len(antiregressions)
                work_total_numbers.addWithTestNumbers(goodruns[1].get('numbers'))
                report_results(output, goodruns[1], regressions, combo, goodruns[0], flakes, antiregressions, trim_number=trim_number)

                if trim_number > 0 and len(regressions) > trim_number:
                    print_number = int(trim_number/2)
                    trimmed_lines = trimmed_lines + (len(regressions) - print_number * 2)

        if trimmed_lines > 0:
            output_errorprojects.write("\nNOTE: %d lines were removed from this report.\n" % trimmed_lines)

        report_kernels_in_report(path_outputfile, unique_kernels, unique_kernel_info, work_total_numbers)
        output.close()
        output_errorprojects.close()
        
        bashCommand = "cat "+ str(scribblefile) +str(" >> ") + path_outputfile
        print(bashCommand)
        #process = subprocess.run(['cat', scribblefile, str('>>'+options['outputfile']) ], stdout=subprocess.PIPE)
        
"""
        except:
            raise CommandError('Kernel "%s" does not exist' % kernel)
"""
