#!/usr/bin/evn python

rawkernels = {
    ## For presubmit jobs
    'android11-54-db845c-presubmit': [
            '5.4-gki-android11-android11-db845c-presubmit',
            ],
    'android13-510-db845c-presubmit': [
            '5.10-gki-android13-aosp-master-db845c-presubmit',
            ],
    'android12-54-db845c-presubmit': [
            '5.4-gki-android12-android12-db845c-presubmit',
            ],
    'android12-510-db845c-presubmit': [
            '5.10-gki-android12-android12-db845c-presubmit',
            ],

    'android-4.9-q-hikey':[
            '4.9q-10.0-gsi-hikey960',
            '4.9q-10.0-gsi-hikey',
            '4.9q-android11-hikey960',
            '4.9q-android12gsi-hikey960',
            ],
    'android-4.14-q-hikey': [
            '4.14q-10.0-gsi-hikey960',
            '4.14q-10.0-gsi-hikey',
            '4.14q-android11-hikey960',
            '4.14q-android12gsi-hikey960',
            '4.14q-master-hikey960'
            ],
    'android-hikey-linaro-4.14-stable-lkft': [
            '4.14-stable-master-hikey960-lkft',
            '4.14-stable-master-hikey-lkft',
            '4.14-stable-android11-hikey960-lkft',
            '4.14-stable-android12-hikey960-lkft-public',
            ],
    'android-beagle-x15-4.14-stable-lkft': [
            '4.14-stable-aosp-x15',
            ],
    'android-4.19-q-hikey':[
            '4.19q-10.0-gsi-hikey960',
            '4.19q-10.0-gsi-hikey',
            '4.19q-android11-hikey960',
            '4.19q-android12gsi-hikey960',
            '4.19q-master-hikey960',
            ],
    'android-hikey-linaro-4.19-stable-lkft': [
            '4.19-stable-master-hikey960-lkft',
            '4.19-stable-master-hikey-lkft',
            '4.19-stable-android11-hikey960-lkft',
            ],
    'android-beagle-x15-4.19-stable-lkft': [
            '4.19-stable-aosp-x15',
            ],

    'android12-5.4':[
            '5.4-gki-aosp-master-db845c',  # android12-5.4
            '5.4-gki-aosp-master-hikey960', # android12-5.4
            '5.4-aosp-master-x15', # android12-5.4
            '5.4-gki-android12-android11-db845c', # android12-5.4
            '5.4-gki-android12-android12-db845c', # android12-5.4
            '5.4-gki-android12-android12-hikey960', # android12-5.4
            ],
    'android11-5.4-lts':[
            '5.4-lts-gki-android11-android11-db845c', # android11-5.4-lts
            '5.4-lts-gki-android11-android11-hikey960', # android11-5.4-lts
            ],
    'android11-5.4':[
            '5.4-gki-android11-android11-db845c', # android11-5.4
            '5.4-gki-android11-android11-hikey960', # android11-5.4
            '5.4-gki-android11-android12-db845c', # android11-5.4
            '5.4-gki-android11-android12-hikey960', # android11-5.4
            '5.4-gki-android11-aosp-master-db845c', # android11-5.4
            '5.4-gki-android11-aosp-master-hikey960', # android11-5.4
            ],
    'android13-5.10':[
            '5.10-gki-android13-aosp-master-db845c',
            '5.10-gki-android13-aosp-master-hikey960',
            ],
    'android12-5.10':[
            '5.10-gki-aosp-master-db845c',
            '5.10-gki-aosp-master-hikey960',
            '5.10-gki-android12-android12-db845c',
            '5.10-gki-android12-android12-hikey960',
            ],
    'android13-5.15':[
            '5.15-gki-android13-aosp-master-db845c',
            ],

    'android12-5.10-lts':[
            '5.10-lts-gki-android12-android12-db845c',
            '5.10-lts-gki-android12-android12-hikey960',
            ],
    'android12-5.4-lts':[
            '5.4-lts-gki-android12-android12-db845c', # android12-5.4-lts
            '5.4-lts-gki-android12-android12-hikey960', # android12-5.4-lts
            ],
    'android-mainline':[
            'mainline-gki-aosp-master-db845c',
            'mainline-gki-aosp-master-hikey960',
            'mainline-gki-aosp-master-hikey',
            'mainline-gki-aosp-master-x15',
            ],

    'android13-5.10-full-cts-vts':[
            '5.10-gki-android13-aosp-master-db845c-full-cts-vts',
            ],
    'android12-5.10-full-cts-vts':[
            '5.10-gki-android12-android12-db845c-full-cts-vts',
            ],
    'android11-5.4-full-cts-vts':[
            '5.4-gki-android11-android11-db845c-full-cts-vts',
            ],
}

projectids = {
    '4.9q-10.0-gsi-hikey':
                    {'project_id': 212,
                     'hardware': 'HiKey',
                     'OS' : 'Android10',
                     'kern' : '4.9',
                     'branch' : 'Android-4.9-q',},
    '4.9q-10.0-gsi-hikey960':
                    {'project_id': 213,
                     'hardware': 'HiKey960',
                     'OS' : 'Android10',
                     'kern' : '4.9',
                     'branch' : 'Android-4.9-q',},
    '4.9q-android11-hikey960':
                    {'slug': '4.9q-android11-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android11',
                     'kern' : '4.9',
                     'branch': 'Android-4.9-q',},
    '4.9q-android12gsi-hikey960':
                    {'slug': '4.9q-android12gsi-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '4.9',
                     'branch': 'Android-4.9-q',},

    '4.14q-10.0-gsi-hikey':
                    {'project_id': 211,
                     'hardware': 'HiKey',
                     'OS' : 'Android10',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-q',},
    '4.14q-10.0-gsi-hikey960':
                    {'project_id': 214,
                     'hardware': 'HiKey960',
                     'OS' : 'Android10',
                     'kern' : '4.14',
                     'branch' : 'Android-4.14-q',},
    '4.14q-android11-hikey960':
                    {'slug': '4.14q-android11-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android11',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-q',},
    '4.14q-android12gsi-hikey960':
                    {'slug': '4.14q-android12gsi-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-q',},
    '4.14q-master-hikey960':
                    {'slug': '4.14q-master-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-q',},

    '4.14-stable-aosp-x15':
                    {'project_id': 320,
                     'hardware': 'X15',
                     'OS' : 'AOSP',
                     'kern' : '4.14',
                     'branch' : 'Android-4.14-stable',},
    '4.14-stable-master-hikey-lkft':
                    {'project_id': 297,
                     'hardware': 'HiKey',
                     'OS' : 'AOSP',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-stable',},
    '4.14-stable-master-hikey960-lkft':
                    {'project_id': 298,
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-stable',},
    '4.14-stable-android11-hikey960-lkft':
                    {'slug': '4.14-stable-android11-hikey960-lkft',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android11',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-stable',},
    '4.14-stable-android12-hikey960-lkft-public':
                    {'slug': '4.14-stable-android12-hikey960-lkft-public',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '4.14',
                     'branch': 'Android-4.14-stable',},

    '4.19-stable-master-hikey960-lkft':
                    {'slug': '4.19-stable-master-hikey960-lkft',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-stable',},
    '4.19-stable-master-hikey-lkft':
                    {'slug': '4.19-stable-master-hikey-lkft',
                     'group':'android-lkft',
                     'hardware': 'HiKey',
                     'OS' : 'AOSP',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-stable',},
    '4.19-stable-android11-hikey960-lkft':
                    {'slug': '4.19-stable-android11-hikey960-lkft',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android11',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-stable',},
    '4.19q-10.0-gsi-hikey':
                    {'project_id': 210,
                     'hardware': 'HiKey',
                     'OS' : 'Android10',
                     'kern' : '4.19',
                     'branch' : 'Android-4.19-q',},
    '4.19q-10.0-gsi-hikey960':
                    {'project_id': 215,
                     'hardware': 'HiKey960',
                     'OS' : 'Android10',
                     'kern' : '4.19',
                     'branch' : 'Android-4.19-q',},
    '4.19-stable-aosp-x15':
                    {'project_id': 335,
                     'hardware': 'x15',
                     'OS' : 'AOSP',
                     'kern' : '4.19',
                     'branch' : 'Android-4.19-stable',},

    '4.19q-android11-hikey960':
                    {'slug': '4.19q-android11-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android11',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-q',},
    '4.19q-android12gsi-hikey960':
                    {'slug': '4.19q-android12gsi-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-q',},
    '4.19q-master-hikey960':
                    {'slug': '4.19q-master-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '4.19',
                     'branch': 'Android-4.19-q',},


    # projects for android12-5.4
    '5.4-gki-aosp-master-hikey960':
                    {'project_id': 257,
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},
    '5.4-gki-aosp-master-db845c':
                    {'project_id': 261,
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},
    '5.4-aosp-master-x15':
                    {'project_id': 339,
                     'hardware': 'x15',
                     'OS' : 'AOSP',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},
    '5.4-gki-android12-android11-db845c':
                    {'slug': '5.4-gki-android12-android11-db845c',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},

    # projects for android11-5.4-lts
    '5.4-lts-gki-android11-android11-db845c':
                    {'project_id': 524,
                     'hardware': 'db845',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4-lts',},
    '5.4-lts-gki-android11-android11-hikey960':
                    {'project_id': 519,
                     'hardware': 'hikey960',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4-lts',},
    # projects for android11-5.4
    '5.4-gki-android11-android11-db845c':
                    {'project_id': 414,
                     'hardware': 'db845',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-android11-db845c-presubmit':
                    {'slug': '5.4-gki-android11-android11-db845c-presubmit',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-android11-hikey960':
                    {'project_id': 409,
                     'hardware': 'hikey960',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-aosp-master-db845c':
                    {'slug': '5.4-gki-android11-aosp-master-db845c',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-aosp-master-hikey960':
                    {'slug': '5.4-gki-android11-aosp-master-hikey960',
                     'group':'android-lkft',
                     'hardware': 'hikey960',
                     'OS' : 'AOSP',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-android11-db845c-full-cts-vts':
                    {'slug': '5.4-gki-android11-android11-db845c-full-cts-vts',
                     'group':'android-lkft',
                     'hardware': 'db845c',
                     'OS' : 'Android11',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},

    # projects for android12-5.10
    '5.10-gki-aosp-master-hikey960':
                    {'project_id': 607,
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},
    '5.10-gki-aosp-master-db845c':
                    {'project_id': 606,
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},
    '5.10-gki-android12-android12-db845c':
                    {'slug': '5.10-gki-android12-android12-db845c',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},
    '5.10-gki-android12-android12-db845c-presubmit':
                    {'slug': '5.10-gki-android12-android12-db845c-presubmit',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},
    '5.10-gki-android12-android12-hikey960':
                    {'slug': '5.10-gki-android12-android12-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},
    '5.10-gki-android12-android12-db845c-full-cts-vts':
                    {'slug': '5.10-gki-android12-android12-db845c-full-cts-vts',
                     'group':'android-lkft',
                     'hardware': 'db845c',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10',},

    # projects for android13-5.10
    '5.10-gki-android13-aosp-master-hikey960':
                    {'project_id': 731,
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : '5.10',
                     'branch' : 'Android13-5.10',},
    '5.10-gki-android13-aosp-master-db845c':
                    {'project_id': 730,
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.10',
                     'branch' : 'Android13-5.10',},
    '5.10-gki-android13-aosp-master-db845c-presubmit':
                    {'slug': '5.10-gki-android13-aosp-master-db845c-presubmit',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.10',
                     'branch' : 'Android13-5.10',},
    '5.10-gki-android13-aosp-master-db845c-full-cts-vts':
                    {'slug': '5.10-gki-android13-aosp-master-db845c-full-cts-vts',
                     'group':'android-lkft',
                     'hardware': 'db845c',
                     'OS' : 'Android13',
                     'kern' : '5.10',
                     'branch' : 'Android13-5.10',},

    # projects for android12-5.10-lts
    '5.10-lts-gki-android12-android12-hikey960':
                    {'slug': '5.10-lts-gki-android12-android12-hikey960',
                     'group': 'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10-lts',},
    '5.10-lts-gki-android12-android12-db845c':
                    {'slug': '5.10-lts-gki-android12-android12-db845c',
                     'group': 'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.10',
                     'branch' : 'Android12-5.10-lts',},

    # projects for android12-5.4
    '5.4-gki-android12-android12-db845c':
                    {'slug': '5.4-gki-android12-android12-db845c',
                     'group': 'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},
    '5.4-gki-android12-android12-db845c-presubmit':
                    {'slug': '5.4-gki-android12-android12-db845c-presubmit',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},
    '5.4-gki-android12-android12-hikey960':
                    {'slug': '5.4-gki-android12-android12-hikey960',
                     'group':'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4',},

    # projects for android12-5.4-lts
    '5.4-lts-gki-android12-android12-hikey960':
                    {'slug': '5.4-lts-gki-android12-android12-hikey960',
                     'group': 'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4-lts',},
    '5.4-lts-gki-android12-android12-db845c':
                    {'slug': '5.4-lts-gki-android12-android12-db845c',
                     'group': 'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android12-5.4-lts',},

    # projects for android11-5.4
    '5.4-gki-android11-android12-hikey960':
                    {'slug': '5.4-gki-android11-android12-hikey960',
                     'group': 'android-lkft',
                     'hardware': 'HiKey960',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},
    '5.4-gki-android11-android12-db845c':
                    {'slug': '5.4-gki-android11-android12-db845c',
                     'group': 'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'Android12',
                     'kern' : '5.4',
                     'branch' : 'Android11-5.4',},

    # projects for android13-5.15
    '5.15-gki-android13-aosp-master-db845c':
                    {'slug': '5.15-gki-android13-aosp-master-db845c',
                     'group':'android-lkft',
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : '5.15',
                     'branch' : 'Android13-5.15',},
    # projects for android-mainline
    'mainline-gki-aosp-master-db845c':
                    {'project_id': 236,
                     'hardware': 'db845',
                     'OS' : 'AOSP',
                     'kern' : 'android-mainline',
                     'branch' : 'android-mainline',},
    'mainline-gki-aosp-master-hikey960':
                    {'project_id': 219,
                     'hardware': 'HiKey960',
                     'OS' : 'AOSP',
                     'kern' : 'android-mainline',
                     'branch' : 'android-mainline',},
    'mainline-gki-aosp-master-hikey':
                    {'project_id': 216,
                     'hardware': 'Hikey',
                     'OS' : 'AOSP',
                     'kern' : 'android-mainline',
                     'branch' : 'android-mainline',},
    'mainline-gki-aosp-master-x15':
                    {'project_id': 237,
                     'hardware': 'x15',
                     'OS' : 'AOSP',
                     'kern' : 'android-mainline',
                     'branch' : 'android-mainline',},

}

def get_all_report_kernels():
    return rawkernels

def get_all_report_projects():
    return projectids
