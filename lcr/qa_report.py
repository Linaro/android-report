# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import json
import logging
import re
import requests
import yaml

from abc import abstractmethod
from io import BytesIO, TextIOWrapper, StringIO
from ruamel.yaml import YAML
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

class DotDict(dict):
    '''dict.item notation for dict()'s'''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class UrlNotFoundException(Exception):
    '''
        Specific Expection for UrlNotFound Error
    '''
    response = None
    url = None

    def __init__(self, response, url=None):
        self.response = response
        self.url = url


class ParameterInvalidException(Exception):
    """
    Exception when wrong Parameters passed
    """
    pass


class RESTFullApi():
    def __init__(self, domain, api_token, auth=None):
        self.domain = domain
        self.api_token = api_token
        self.auth = auth

    def call_with_full_url(self, request_url='', method='GET', returnResponse=False, post_data=None):
        headers = {
                'Content-Type': 'application/json',
                }
        if self.api_token and len(self.api_token) > 0:
            headers['Authorization'] = 'Token %s' % self.api_token
            headers['Auth-Token'] = self.api_token
            headers['PRIVATE-TOKEN'] = self.api_token

        if method == 'GET':
            r = requests.get(request_url, headers=headers, auth=self.auth)
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            r = requests.post(request_url, headers=headers, data=post_data)

        if returnResponse:
            return r

        if not r.ok and r.status_code == 404:
            logger.info("url({}) not found".format(request_url))
            raise UrlNotFoundException(r, url=request_url)
        elif not r.ok or r.status_code != 200:
            raise Exception(r.url, r.reason, r.status_code)

        if r.content:
            ret = DotDict(r.json())
            return ret
        else:
            return r

    def call_with_api_url(self, api_url='', method='GET', returnResponse=False, post_data=None):
        full_url = '%s/%s' % (self.get_api_url_prefix().strip('/'), api_url.strip('/'))
        return self.call_with_full_url(request_url=full_url, method=method, returnResponse=returnResponse, post_data=post_data)

    def get_list_results(self, api_url='', only_first=False):
        result = self.call_with_api_url(api_url=api_url)
        list_results = result.get('results')
        if not only_first:
            next_url = result.get('next')
            while next_url:
                result = self.call_with_full_url(request_url=next_url)
                next_url = result.get('next')
                list_results.extend(result.get('results'))
        return list_results

    @abstractmethod
    def get_api_url_prefix(sefl):
        """Return the url prefix, which we could use with the api url directly"""
        """Should never be called."""
        raise NotImplementedError('%s.get_api_url_prefix should never be called directly' % self.__class__.__name__)


class GitlabApi(RESTFullApi):
    def get_api_url_prefix(self, detail_url):
        return 'https://%s/api/v4/projects/%s' % (self.domain, detail_url)

    def get_json_with_url(self, full_url):
        r = self.call_with_full_url(request_url=full_url, returnResponse=True)
        if not r.ok and r.status_code == 404:
            raise UrlNotFoundException(r, url=full_url)
        elif not r.ok or r.status_code != 200:
            raise Exception(r.url, r.reason, r.status_code)

        return r.json()

    def get_project(self, project_id):
        project_id = project_id.replace('/', '%2F')
        full_url = self.get_api_url_prefix(detail_url=project_id)
        return self.get_json_with_url(full_url)

    def get_project_pipelines(self, project_id, per_page=50):
        project_id = project_id.replace('/', '%2F')
        full_url = self.get_api_url_prefix(detail_url="%s/pipelines?per_page=%d" % (project_id, per_page))
        return self.get_json_with_url(full_url)

    def get_pipeline_variables(self, project_id, pipeline_id):
        project_id = project_id.replace('/', '%2F')
        full_url = self.get_api_url_prefix(detail_url="%s/pipelines/%s/variables" % (project_id, pipeline_id))
        return self.get_json_with_url(full_url)

    def get_pipeline_jobs(self, project_id, pipeline_id):
        project_id = project_id.replace('/', '%2F')
        full_url = self.get_api_url_prefix(detail_url="%s/pipelines/%s/jobs" % (project_id, pipeline_id))
        return self.get_json_with_url(full_url)

    def get_job_artifacts_url(self, project_id, job_id):
        return self.get_api_url_prefix(detail_url="%s/jobs/%s/artifacts" % (project_id, job_id))

    def get_project_url(self, project_id):
        return self.get_api_url_prefix(detail_url="%s" % (project_id))


class JenkinsApi(RESTFullApi):
    def __init__(self, domain, api_token, user=None):
        from requests.auth import HTTPBasicAuth
        if user is not None:
            auth = HTTPBasicAuth(user, api_token)
        else:
            auth = None
        super().__init__(domain, api_token, auth=auth)

    def get_api_url_prefix(self, detail_url):
        # https://ci.linaro.org/job/trigger-lkft-aosp-mainline/api/json
        return 'https://%s/job/%s/api/json/' % (self.domain, detail_url)

    def get_last_build(self, cijob_name=''):
        if not cijob_name:
            return None
        full_url = self.get_api_url_prefix(detail_url=cijob_name)
        result = self.call_with_full_url(request_url=full_url)
        if result:
            return result.get('lastBuild')
        else:
            return None

    def is_build_disabled(self, cibuild_name):
        try:
            build_details = self.get_build_details_with_cibuild_name(cibuild_name)
        except UrlNotFoundException:
            # Treat deleted builds as disabled
            return True
        return not build_details.get('buildable')

    def get_build_details_with_cibuild_name(self, cibuild_name):
        full_api_url = self.get_api_url_prefix(detail_url=cibuild_name)
        return self.call_with_full_url(request_url=full_api_url)

    def get_build_details_with_job_url(self, job_url):
        full_api_url = self.get_api_url_prefix(detail_url=job_url)
        return self.call_with_full_url(request_url=full_api_url)

    def get_build_details_with_full_url(self, build_url):
        if build_url.find(self.domain) < 0:
            raise UrlNotFoundException(None, url=build_url)
        full_api_url = '%s/api/json/' % build_url
        return self.call_with_full_url(request_url=full_api_url)

    def get_trigger_from_ci_build(self, jenkins_build):
        logger.info("Try to find the trigger build for build: %s" % jenkins_build.get('url'))
        last_build_ci_build_actions = jenkins_build.get("actions")
        is_user_triggered_build = False
        for action in last_build_ci_build_actions:
            action_class = action.get("_class")
            if not action_class or action_class != "hudson.model.CauseAction":
                continue

            causes = action.get("causes")
            for cause in causes:
                cause_class = cause.get("_class")
                if not cause_class:
                    continue

                if cause_class == "hudson.triggers.SCMTrigger$SCMTriggerCause":
                    return jenkins_build
                elif  cause_class == "hudson.model.Cause$UserIdCause":
                    is_user_triggered_build = True
                    continue
                elif cause_class != "hudson.model.Cause$UpstreamCause":
                    continue

                upstreamBuild = cause.get("upstreamBuild") # 297
                upstreamProject = cause.get("upstreamProject") # trigger-lkft-linaro-hikey
                trigger_ci_build_url = self.get_job_url(name=upstreamProject, number=upstreamBuild)
                trigger_build = self.get_build_details_with_full_url(trigger_ci_build_url)

                logger.info("Found the trigger build for build: %s which is %s" % (jenkins_build.get('url'), trigger_ci_build_url))
                return trigger_build

        if is_user_triggered_build:
            return jenkins_build
        else:
            return None

    def get_final_trigger_from_ci_build(self, jenkins_build):
        build_url = jenkins_build.get('url')
        trigger_build = self.get_trigger_from_ci_build(jenkins_build)
        if trigger_build is None:
            logger.info("Failed to get the trigger for build: %s" % build_url)
            return None

        trigger_url = trigger_build.get('url')
        if build_url != trigger_url:
            try:
                new_trigger_build = self.get_build_details_with_full_url(trigger_url)
                return self.get_final_trigger_from_ci_build(new_trigger_build)
            except UrlNotFoundException:
                logger.info("build job url is not found: {}".format(trigger_url))
                return None
        else:
            return jenkins_build

    def get_job_url(self, name=None, number=None):
        if name is None:
            return "https://%s" % (self.domain)
        elif number is None:
            return "https://%s/job/%s/" % (self.domain, name)
        else:
            return "https://%s/job/%s/%s/" % (self.domain, name, number)

    def get_queued_items(self):
        # https://ci.linaro.org/queue/api/json?pretty=true
        queue_api = 'https://%s/queue/api/json/' % (self.domain)
        result = self.call_with_full_url(request_url=queue_api)
        if result:
            queued_items = result.get('items')
            items_tobe_returned = []
            for item in queued_items:
                cibuild_name = item.get('task').get('name')
                if not cibuild_name.startswith('lkft-'):
                    continue
                params_list = item.get('params').strip().split('\n')
                params_dict = {}
                for key_val_str in params_list:
                    (key, value) = key_val_str.split('=')
                    if key is not None:
                        params_dict[key] = value
                if not params_dict.get('KERNEL_DESCRIBE'):
                    continue
                item['KERNEL_DESCRIBE'] = params_dict.get('KERNEL_DESCRIBE')
                item['build_name'] = cibuild_name
                items_tobe_returned.append(item)

            return items_tobe_returned
        else:
            return []

    def get_parameter_value_with_build_json(self, jenkins_build_json, para_name):
        ci_build_actions = jenkins_build_json.get('actions')
        for action in ci_build_actions:
            class_name = action.get('_class')
            if class_name != 'hudson.model.ParametersAction':
                continue
            parameters = action.get('parameters')
            for parameter in parameters:
                if parameter.get('_class') == 'hudson.model.StringParameterValue' \
                        and parameter.get('name') == para_name :
                    return parameter.get('value').strip()
        return ""

    def get_build_configs(self, jenkins_build_json):
        return self.get_parameter_value_with_build_json(jenkins_build_json, 'ANDROID_BUILD_CONFIG')

    def get_override_plans(self, jenkins_build_json):
        return self.get_parameter_value_with_build_json(jenkins_build_json, 'TEST_OTHER_PLANS_OVERRIDE')


class LAVAApi(RESTFullApi):
    username = None

    def __init__(self, lava_config=None):
        self.username = lava_config.get('username')
        super().__init__(lava_config.get('hostname'), lava_config.get('token'))

    def get_api_url_prefix(self):
        return 'https://%s/api/v0.2/' % self.domain

    def get_job(self, job_id=None):
        api_url = "/jobs/%s" % job_id
        return self.call_with_api_url(api_url=api_url)

    def get_job_results(self, job_id=None, lava_config=None):
        url_result_yaml = "https://%s/results/%s/yaml?user=%s&token=%s" % (self.domain, job_id, self.username, self.api_token)
        r = self.call_with_full_url(request_url=url_result_yaml, returnResponse=True)
        if not r.ok and r.status_code == 404:
            raise UrlNotFoundException(r, url=url_result_yaml)
        elif not r.ok or r.status_code != 200:
            raise Exception(r.url, r.reason, r.status_code)

        results = yaml.safe_load(r.content)
        return results

    def cancel_job(self, lava_job_id=None):
        ## e.g. http://validation.linaro.org/api/v0.2/jobs/2345786/cancel/
        api_url = '/jobs/%s/cancel/' % lava_job_id
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True)

    def __parse_log__(self, log_data):
        returned_log = StringIO()
        start_dict = False
        tmp_dict = None
        tmp_key = None
        is_value = False
        logger.debug("Length of log buffer: %s" % log_data.getbuffer().nbytes)
        if log_data.getbuffer().nbytes > 0:
            try:
                for event in yaml.parse(log_data, Loader=yaml.CLoader):
                    if isinstance(event, yaml.MappingStartEvent):
                        start_dict = True
                        tmp_dict = {}
                    if isinstance(event, yaml.MappingEndEvent):
                        start_dict = False
                        if tmp_dict:
                            if 'lvl' in tmp_dict.keys():
                                    # let's output all logs, there are seveal types for lvl:
                                    #   target, feedback, debug, info, results, input, ...
                                    # and (tmp_dict['lvl'] == 'target' or tmp_dict['lvl'] == 'feedback'):
                                if 'msg' in tmp_dict.keys():
                                    if isinstance(tmp_dict['msg'], bytes):
                                        try:
                                            # seems like latin-1 is the encoding used by serial
                                            # this might not be true in all cases
                                            returned_log.write(tmp_dict["msg"].decode('latin-1', 'ignore') + "\n")
                                        except ValueError:
                                            # despite ignoring errors, they are still raised sometimes
                                            pass
                                    else:
                                        returned_log.write(tmp_dict['msg'] + "\n")
                        del tmp_dict
                        tmp_dict = None
                        is_value = False
                    if start_dict is True and isinstance(event, yaml.ScalarEvent):
                        if is_value is False:
                            # the event.value is a dict key
                            tmp_key = event.value
                            is_value = True
                        else:
                            # the event.value is a dict value
                            tmp_dict.update({tmp_key: event.value})
                            is_value = False
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                log_data.seek(0)
                wrapper = TextIOWrapper(log_data, encoding='utf-8')
                logger.error("Problem parsing LAVA log\n" + wrapper.read() + "\n" + traceback.format_exc())

        return returned_log.getvalue().replace("\x00", "")

    def get_lava_log(self, lava_job_id=None):
        # https://validation.linaro.org/scheduler/job/3365241/log_file/plain
        url_log_plain = "https://%s/scheduler/job/%s/log_file/plain?user=%s&token=%s" % (self.domain, lava_job_id, self.username, self.api_token)
        r = self.call_with_full_url(request_url=url_log_plain, returnResponse=True)
        if not r.ok and r.status_code == 404:
            #raise UrlNotFoundException(r, url=url_log_plain)
            logger.warn("LAVA Log not found: " + "https://%s/scheduler/job/%s/log_file/plain" % (self.domain, lava_job_id) )
            raw_logs = BytesIO()
        elif not r.ok or r.status_code != 200:
            #raise Exception(r.url, r.reason, r.status_code)
            logger.warn("Failed to get LAVA Log for %s because of error: " + "https://%s/scheduler/job/%s/log_file/plain" % (self.domain, lava_job_id) + "\n" +  Exception(r.url, r.reason, r.status_code))
            raw_logs = BytesIO()

        raw_logs = BytesIO(r.content)
        return self.__parse_log__(raw_logs)


class QAReportApi(RESTFullApi):
    def get_api_url_prefix(self):
        if self.domain.startswith('http'):
            return '%s/' % self.domain.strip('/')
        else:
            return 'https://%s/' % self.domain.strip('/')


    def get_projects(self, filter_url=None):
        if filter_url is not None:
            api_url = filter_url
        else:
            api_url = "/api/projects/"
        return self.get_list_results(api_url=api_url)

    def get_projects_with_group_id(self, group_id):
        # https://qa-reports.linaro.org/api/projects/?group=17
        api_url = "/api/projects/?group={}".format(group_id)
        return self.get_list_results(api_url=api_url)


    def get_project(self, project_id):
        api_url = "/api/projects/%s" % project_id
        return self.call_with_api_url(api_url=api_url)


    def get_project_group(self, project_json):
        return project_json.get('full_name').replace('/{}'.format(project_json.get('slug')), "")


    def get_project_url_with_group_slug(self, group, slug):
        return "https://%s/%s/%s" % (self.domain, group, slug)


    def get_project_with_url(self, project_url):
        return self.call_with_full_url(request_url=project_url)


    def get_project_api_url_with_project_id(self, project_id):
        return "https://%s/api/projects/%s/" % (self.domain, project_id)

    def get_project_full_name_with_group_and_slug(self, group_name, slug):
        return "%s/%s" % (group_name, slug)


    def get_all_builds(self, project_id, only_first=False, limit=-1):
        builds_api_url = "api/projects/%s/builds" % project_id
        if only_first:
            limit = 1
        if limit != -1:
            builds_api_url = "{}?limit={}".format(builds_api_url, limit)
            only_first = True

        return self.get_list_results(api_url=builds_api_url, only_first=only_first)


    def get_build(self, build_id):
        builds_api_url = "api/builds/%s" % build_id
        return self.call_with_api_url(api_url=builds_api_url)


    def get_build_api_url_with_build_id(self, build_id):
        return "https://%s/api/builds/%s/" % (self.domain, build_id)


    def get_build_url_with_group_slug_buildVersion(self, group, slug, build_version):
        return "https://%s/%s/%s/%s" % (self.domain, group, slug, build_version)


    def get_build_with_url(self, build_url):
        return self.call_with_full_url(request_url=build_url)


    def get_build_with_version(self, build_version, project_id):
        for build in self.get_all_builds(project_id):
            if build.get('version') == build_version:
                return build
        return None


    def get_build_meta_with_url(self, build_meta_url):
        return self.call_with_full_url(request_url=build_meta_url)


    def get_jobs_for_build(self, build_id):
        api_url = "api/builds/%s/testjobs" % build_id
        jobs = self.get_list_results(api_url=api_url)
        for job in jobs:
            job_name = job.get('name')
            if job_name is None:
                job_definition = self.get_job_definition(job.get('definition'))
                if job_definition.get('job_name') is None:
                    # the project had been deleted or not specified(like the gki build)
                    logger.info("Failed to get job name from job definition: {}".format(job.get('definition')))
                    job['name'] = 'qareport-id-{}'.format(job.get('id'))
                else:
                    job['name'] = job_definition.get('job_name')
                    logger.info("Job name set to {} with information from job definition".format(job.get('name')))
            self.set_job_status(job)
            self.reset_qajob_failure_msg(job)

        return jobs


    def get_project_with_name(self, project_full_name):
        # https://qa-reports.linaro.org/api/projects/?full_name=android-lkft%2Fmainline-gki-aosp-master-db845c
        api_url = "/api/projects/?full_name={}".format(project_full_name)
        for project in self.get_projects(filter_url=api_url):
            if project.get('full_name') == project_full_name:
                return project
        return None


    def get_builds_with_project_name(self, project_full_name):
        qa_report_project = self.get_project_with_name(project_full_name)
        if not qa_report_project:
            logger.info("qa report project for build %s not found" % project_full_name)
            return []
        return self.get_all_builds(qa_report_project.get('id'))


    def get_jobs_with_project_name_build_version(self, project_full_name, build_version):
        qa_report_project = self.get_project_with_name(project_full_name)
        if not qa_report_project:
            logger.info("qa report project for build %s not found" % project_full_name)
            return []
        build = self.get_build_with_version(build_version, qa_report_project.get('id'))
        if not build:
            logger.info("qa report build for project(%s) with build no(%s) not found" % (project_full_name, build_version))
            return []
        return self.get_jobs_for_build(build.get('id'))


    def create_build(self, team, project, build_version):
        api_url = "api/createbuild/%s/%s/%s" % (team, project, build_version)
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True)


    def submit_test_result(self, team, project, build_version, environment,
            tests_data_dict={}, metadata_dict={}, metrics_dict={}):
        '''
        tests_data_dict': {
            "test_suite1/test_case1": "fail",
            "test_suite1/test_case2": "pass",
            "test_suite2/test_case1": "fail",
            "test_suite2/test_case2": "pass",
        }
        metadata_dict = {
            'job_id': '12345',  # job_id is mandatory here, and need to be string
            'test_metadata': 'xxxx',
        }
        metrics_dict = {
            'metrics_suite1/test_metric1': [1, 2, 3, 4, 5],
            'metrics_suite1/test_metric21': 10,
        }
        '''

        if type(tests_data_dict) != dict or not tests_data_dict:
            raise ParameterInvalidException("tests_data_dict must be a dictionary for test cases, and should not be empty")

        if type(metadata_dict) != dict:
            raise ParameterInvalidException("metadata_dict must be a dictionary for test cases")

        if type(metrics_dict) != dict:
            raise ParameterInvalidException("metrics_dict must be a dictionary for test cases")

        post_data={
            'tests': json.dumps(tests_data_dict)
        }
        if metadata_dict:
            post_data[metadata] = json.dumps(metadata_dict),

        if metrics_dict:
            post_data['metrics'] = json.dumps(metrics_dict),

        api_url = "api/submit/%s/%s/%s/%s" % (team, project, build_version, environment)
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True, post_data=post_data)


    def forceresubmit(self, qa_job_id):
        api_url = 'api/forceresubmit/%s' % qa_job_id
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True)


    '''
        lava_url_base: https://validation.linaro.org/
    '''
    def submitjob_with_definition(self, qa_team, qa_project, qa_build, qa_env, lava_url_base, job_definition):
        api_url = 'api/submitjob/%s/%s/%s/%s' % (qa_team, qa_project, qa_build, qa_env)

        def simple_yaml_check(yaml_string):
            logger.debug(yaml_string)
            yaml = YAML()
            # ruamel does not provide a mechanism to dump to string, so use StringIO
            # to catch it
            output = StringIO()
            yaml.dump(yaml.load(yaml_string), output)
            # strip empty lines from output
            return re.sub(r"^\s*$\n", "", output.getvalue(), flags=re.MULTILINE)

        post_data = {
            "definition": simple_yaml_check(job_definition),
            "backend": urlsplit(
                lava_url_base
            ).netloc,  # qa-reports backends are named as lava instances, something like "validation.linaro.org"
        }

        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True, post_data=post_data)


    def canceljob(self, qa_job_id):
        api_url = 'api/testjobs/%s/cancel' % qa_job_id
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True)


    def get_environment_with_url(self, environment_url):
        return self.call_with_full_url(request_url=environment_url)

    def get_backend_with_url(self, backend_url):
        return self.call_with_full_url(request_url=backend_url)

    def get_group_with_url(self, group_url):
        return self.call_with_full_url(request_url=group_url)

    def fetchjob(self, qa_job_id):
        qa_job = self.get_job_with_id(qa_job_id)
        qa_build = self.get_build_with_url(qa_job.get("target_build"))
        qa_project = self.get_project_with_url(qa_job.get("target"))
        qa_group = self.get_group_with_url(qa_project.get("group"))
        qa_backend = self.get_backend_with_url(qa_job.get("backend"))

        # group_slug, project_slug, version, environment_slug, backend_name
        api_url = 'api/fetchjob/%s/%s/%s/%s/%s' % (qa_group.get('slug'), qa_project.get("slug"), qa_build.get("version"), qa_job.get("environment"), qa_backend.get("name"))
        logger.info(f"fetchjob api url={api_url}")
        return self.call_with_api_url(api_url=api_url, method='POST', returnResponse=True)

    '''
        Possible job status: Submitted, Running, Complete, Incomplete, Canceled
    '''
    def set_job_status(self, job):
        if job.get('job_status') is None and \
                job.get('submitted') and \
                not job.get('fetched'):
            job['job_status'] = 'Submitted'
        elif job.get('job_status') is None and \
                not job.get('submitted'):
            # like when lava instance id down
            job['job_status'] = 'NotSubmitted'

    def reset_qajob_failure_msg(self, job):
        if type(job.get('failure')) == str:
            failure_str = job.get('failure')
            new_str = failure_str.replace('"', '\\"').replace('\'', '"')
            try:
                failure_dict = json.loads(new_str)
            except ValueError:
                failure_dict = {'error_msg': new_str}
            job['failure'] = failure_dict
        else:
            # already reset
            pass

    def get_job_with_id(self, qa_job_id):
        api_url = 'api/testjobs/%s' % qa_job_id
        job = self.call_with_api_url(api_url=api_url)
        self.set_job_status(job)
        return job

    def get_job_api_url(self, qa_job_id):
        api_url = '%s/api/testjobs/%s' % (self.get_api_url_prefix().strip('/'), qa_job_id)
        return api_url

    def get_qa_job_id_with_url(self, job_url):
        if job_url:
            return job_url.strip('/').split('/')[-1]
        else:
            return job_url

    def get_job_definition(self, url_definition=None):
        response = self.call_with_full_url(request_url=url_definition, returnResponse=True)
        job_definition = yaml.safe_load(response.content)
        return job_definition

    def get_lkft_qa_report_projects(self, include_archived=False):
        projects = []
        for project in self.get_projects():
            if (not include_archived) and (project.get('is_archived')):
                continue

            project_full_name = project.get('full_name')
            if not project_full_name.startswith('android-lkft/') \
                and not project_full_name.startswith('android-lkft-benchmarks/') \
                and not project_full_name.startswith('android-lkft-rc/'):
                continue

            projects.append(project)

        return projects

    def get_aware_datetime_from_str(self, datetime_str):
        import datetime
        import pytz
        # from python3.7, pytz is not necessary, we could use %z to get the timezone info
        #https://stackoverflow.com/questions/53291250/python-3-6-datetime-strptime-returns-error-while-python-3-7-works-well
        if type(datetime_str) is datetime.datetime:
            return datetime_str
        if type(datetime_str) is not str:
            datetime_str = str(datetime_str)

        if datetime_str.split(":")[-1].find('.') > -1:
            str_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        else:
            str_format = '%Y-%m-%dT%H:%M:%SZ'

        navie_datetime = datetime.datetime.strptime(datetime_str, str_format)
        return pytz.utc.localize(navie_datetime)


    def get_aware_datetime_from_timestamp(self, timestamp_in_secs):
        import datetime
        from django.utils import timezone

        return datetime.datetime.fromtimestamp(timestamp_in_secs, tz=timezone.utc)


class GoogleSourceApi(RESTFullApi):
    def get_api_url_prefix(self, detail_url):
        return 'https://%s/%s' % (self.domain, detail_url)

    def get_json_with_url(self, full_url):
        r = self.call_with_full_url(request_url=full_url, returnResponse=True)
        if not r.ok and r.status_code == 404:
            raise UrlNotFoundException(r, url=full_url)
        elif not r.ok or r.status_code != 200:
            raise Exception(r.url, r.reason, r.status_code)

        json_str = r.text.replace(")]}'", "")
        json_data = json.loads(json_str)
        return json_data

    ### how to identify the following two commits:
    ###    https://android.googlesource.com/kernel/common/+/8ef1b8364451459d26aa6d6cf395d424eda2d659
    ###    https://android.googlesource.com/kernel/common/+/30e51dea80fc9d70b34db60a6a1172b470c7f95b
    def get_first_parents_from_googlesource(self, current_sha_12bit, previous_sha_12bit):
        first_parents = []
        googlesource_domain = "android.googlesource.com"
        googlesource_log_url = f"https://{googlesource_domain}/kernel/common/+log/{current_sha_12bit}?format=JSON"
        try:
            commits_json = self.get_json_with_url(googlesource_log_url)
            for commit in commits_json.get("log"):
                commit['subject'] = commit.get('message').split("\n")[0]
                first_parents.append(commit)
                if commit.get("commit").startswith(previous_sha_12bit):
                    return first_parents

                if len(commit.get('parents')) > 1:
                    first_parents.extend(self.get_first_parents_from_googlesource(commit.get("parents")[0][:12], previous_sha_12bit))
                    # no need to check the remain commits anymore
                    break

            if first_parents[-1].get("commit").startswith(previous_sha_12bit):
                return first_parents

            if len(first_parents) > 0:
                first_parents.extend(self.get_first_parents_from_googlesource(first_parents[-1].get("parents")[0][:12], previous_sha_12bit))

        except UrlNotFoundException:
            logger.info(f"URL {googlesource_log_url} does not exist" )
            pass

        return first_parents


class TestNumbers():
    number_passed = 0
    number_failed = 0
    number_assumption_failure = 0
    number_ignored = 0
    number_total = 0
    number_regressions = 0
    number_antiregressions = 0
    modules_done = 0
    modules_total = 0
    jobs_finished = 0
    jobs_total = 0


    def addWithHash(self, numbers_of_result):
        self.number_passed = self.number_passed + numbers_of_result.get('number_passed')
        self.number_failed = self.number_failed + numbers_of_result.get('number_failed')
        self.number_assumption_failure = self.number_assumption_failure + numbers_of_result.get('number_assumption_failure', 0)
        self.number_ignored = self.number_ignored + numbers_of_result.get('number_ignored', 0)
        self.number_total = self.number_total + numbers_of_result.get('number_total')
        self.number_regressions = self.number_regressions + numbers_of_result.get('number_regressions', 0)
        self.number_antiregressions = self.number_antiregressions + numbers_of_result.get('number_antiregressions', 0)
        self.modules_done = self.modules_done + numbers_of_result.get('modules_done')
        self.modules_total = self.modules_total + numbers_of_result.get('modules_total')
        self.jobs_finished = self.jobs_finished + numbers_of_result.get('jobs_finished', 0)
        self.jobs_total = self.jobs_total + numbers_of_result.get('jobs_total', 0)

        return self


    def toHash(self):
        return  {
            'number_passed': self.number_passed,
            'number_failed': self.number_failed,
            'number_assumption_failure': self.number_assumption_failure,
            'number_ignored': self.number_ignored,
            'number_total': self.number_total,
            'number_regressions': self.number_regressions,
            'number_antiregressions': self.number_antiregressions,
            'modules_done': self.modules_done,
            'modules_total': self.modules_total,
            'jobs_finished': self.jobs_finished,
            'jobs_total': self.jobs_total,
            }


    def addWithTestNumbers(self, testNumbers):
        self.number_passed = self.number_passed + testNumbers.number_passed
        self.number_failed = self.number_failed + testNumbers.number_failed
        self.number_assumption_failure = self.number_assumption_failure + testNumbers.number_assumption_failure
        self.number_ignored = self.number_ignored + testNumbers.number_ignored
        self.number_total = self.number_total + testNumbers.number_total
        self.number_regressions = self.number_regressions + testNumbers.number_regressions
        self.number_antiregressions = self.number_antiregressions + testNumbers.number_antiregressions
        self.modules_done = self.modules_done + testNumbers.modules_done
        self.modules_total = self.modules_total + testNumbers.modules_total
        self.jobs_finished = self.jobs_finished + testNumbers.jobs_finished
        self.jobs_total = self.jobs_total + testNumbers.jobs_total

        return self


    def addWithDatabaseRecord(self, db_record):
        self.number_passed = self.number_passed + db_record.number_passed
        self.number_failed = self.number_failed + db_record.number_failed
        self.number_assumption_failure = self.number_assumption_failure + db_record.number_assumption_failure
        self.number_ignored = self.number_ignored + db_record.number_ignored
        self.number_total = self.number_total + db_record.number_total
        self.modules_done = self.modules_done + db_record.modules_done
        self.modules_total = self.modules_total + db_record.modules_total
        if hasattr(db_record, 'jobs_finished'):
            self.jobs_finished = self.jobs_finished + db_record.jobs_finished
        if hasattr(db_record, 'jobs_total'):
            self.jobs_total = self.jobs_total + db_record.jobs_total

        if hasattr(db_record, 'number_regressions'):
            self.number_regressions = self.number_regressions + db_record.number_regressions
        if hasattr(db_record, 'number_antiregressions'):
            self.number_antiregressions = self.number_antiregressions + db_record.number_antiregressions

        return self


    def setValueForDatabaseRecord(self, db_record):
        db_record.number_passed = self.number_passed
        db_record.number_failed = self.number_failed
        db_record.number_assumption_failure = self.number_assumption_failure
        db_record.number_ignored = self.number_ignored
        db_record.number_total = self.number_total
        db_record.modules_done = self.modules_done
        db_record.modules_total = self.modules_total

        if hasattr(db_record, 'jobs_finished'):
            db_record.jobs_finished = self.jobs_finished
        if hasattr(db_record, 'jobs_total'):
            db_record.jobs_total = self.jobs_total

        if hasattr(db_record, 'number_regressions'):
            db_record.number_regressions = self.number_regressions
        if hasattr(db_record, 'number_antiregressions'):
            db_record.number_antiregressions = self.number_antiregressions
        return db_record


    def setHashValueForDatabaseRecord(db_record, numbers_of_result):
        db_record.number_passed = numbers_of_result.get('number_passed')
        db_record.number_failed = numbers_of_result.get('number_failed')
        db_record.number_assumption_failure = numbers_of_result.get('number_assumption_failure', 0)
        db_record.number_ignored = numbers_of_result.get('number_ignored', 0)
        db_record.number_total = numbers_of_result.get('number_total')
        db_record.modules_done = numbers_of_result.get('modules_done')
        db_record.modules_total = numbers_of_result.get('modules_total')

        if hasattr(db_record, 'jobs_finished'):
            db_record.jobs_finished = numbers_of_result.get('jobs_finished', 0)
        if hasattr(db_record, 'jobs_total'):
            db_record.jobs_total = numbers_of_result.get('jobs_total', 0)

        if hasattr(db_record, 'number_regressions'):
            db_record.number_regressions = numbers_of_result.get('number_regressions', 0)
        if hasattr(db_record, 'number_antiregressions'):
            db_record.number_antiregressions = numbers_of_result.get('number_antiregressions', 0)

        return db_record
