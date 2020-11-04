data_accounts = [
    {
        "id": "1",
        "organization_name": "Entail",
        "organization_id": "920868797",
        "projects": ["1", "2"],
        "users": ["1", "2", "3", "4"],
        "workflow_definitions_owned": ["1", "2", "3", "4"],
        "workflow_definitions_subscriptions": None,
    }
]

data_project = {
    "id": "1",
    "name": "Test",
    "account_id": "1",
    "storage_type": "S3_BUCKET",
    "storage_identifier": "bucketname1",
    "users": ["1", "2", "3", "4"],
}

data_projects = [
    {
        "id": "1",
        "name": "Test",
        "account_id": "1",
        "storage_type": "S3_BUCKET",
        "storage_identifier": "bucketname1",
        "users": ["1", "2", "3", "4"],
    },
    {
        "id": "2",
        "name": "Other",
        "account_id": "1",
        "storage_type": "S3_BUCKET",
        "storage_identifier": "bucketname2",
        "users": ["1", "2"],
    },
]

data_empty_fileset = {"id": "a_fileset_id", "tags": []}

data_fileset_download = {"task_id": None, "tags": ["tag1", "tag2"]}

data_fileset_upload = {
    "task_id": None,
    "tags": {
        "tag1": ["filename1.txt", "filename2.txt"],
        "tag2": ["other_file.txt"],
    },
}

data_fileset = {
    "id": "a_fileset_id",
    "tags": [
        {
            "tag": "tag1",
            "links": [
                {
                    "filename": "filename1.txt",
                    "url": "https://path/to/tag1/0/filename1.txt",
                },
                {
                    "filename": "filename2.txt",
                    "url": "https://path/to/tag1/1/filename2.txt",
                },
            ],
        },
        {
            "tag": "tag2",
            "links": [
                {
                    "filename": "other_file.txt",
                    "url": "https://path/to/tag2/0/other_file.txt",
                }
            ],
        },
    ],
}

data_workflow = {
    "id": "237",
    "name": "duplicate workflow",
    "project_id": "1",
    "updated_utc": "2020-09-07T18:34:26.098000+00:00",
    "user_id": "1",
    "state": "COMPLETED",
    "created_utc": "2020-09-07T18:33:25.130000+00:00",
    "task_links": {
        "857": [858, 859, 862, 861],
        "858": [860],
        "859": [860],
        "860": [],
        "861": [863],
        "862": [863],
        "863": [],
    },
    "root_tasks": ["857"],
    "task_states": {
        "857": "COMPLETED",
        "858": "COMPLETED",
        "859": "COMPLETED",
        "860": "COMPLETED",
        "861": "COMPLETED",
        "862": "COMPLETED",
        "863": "COMPLETED",
    },
    "fileset_id": "1",
    "dag": {
        "name": "dag",
        "links": {},
        "tasks": [
            {
                "name": "duplicate",
                "task": {
                    "name": "sub-dag",
                    "links": {"0": [2], "1": [2], "2": []},
                    "tasks": [
                        {
                            "name": "task 1",
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 2",
                            "args": [
                                "This arg will be overwritten by the DuplicateTask"
                            ],
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 3",
                            "args": "Hello from task 3 which got no args from duplicate...",
                            "function": "builtins.print",
                            "type": "python",
                        },
                    ],
                    "type": "dag",
                },
                "args": ["Duplicated 1", "Duplicated 2"],
                "type": "branch",
            }
        ],
        "type": "dag",
    },
    "inputs": {},
    "outputs": {},
    "from_definition_id": None,
    "tasks": [
        {"id": "857", "name": "duplicate", "type": "branch"},
        {"id": "858", "name": "task 1", "type": "python"},
        {"id": "859", "name": "task 2", "type": "python"},
        {"id": "860", "name": "task 3", "type": "python"},
        {"id": "861", "name": "task 1", "type": "python"},
        {"id": "862", "name": "task 2", "type": "python"},
        {"id": "863", "name": "task 3", "type": "python"},
    ],
}

data_workflow_create_dag = {
    "from_definition_id": None,
    "dag": {
        "name": "dag",
        "links": {},
        "tasks": [
            {
                "name": "duplicate",
                "task": {
                    "name": "sub-dag",
                    "links": {"0": [2], "1": [2], "2": []},
                    "tasks": [
                        {
                            "name": "task 1",
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 2",
                            "args": [
                                "This arg will be overwritten by the DuplicateTask"
                            ],
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 3",
                            "args": "Hello from task 3 which got no args from duplicate...",
                            "function": "builtins.print",
                            "type": "python",
                        },
                    ],
                    "type": "dag",
                },
                "args": ["Duplicated 1", "Duplicated 2"],
                "type": "branch",
            }
        ],
        "type": "dag",
    },
    "name": "A workflow",
    "inputs": {},
    "worker_name_restriction": None,
    "fileset_id": "1",
}


dag_data = {
        "name": "dag",
        "links": {},
        "tasks": [
            {
                "name": "branch",
                "task": {
                    "name": "sub-dag",
                    "links": {"0": [2], "1": [2], "2": []},
                    "tasks": [
                        {
                            "name": "task 1",
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 2",
                            "args": [
                                "This arg will be overwritten by the BranchTask"
                            ],
                            "function": "builtins.print",
                            "type": "python",
                        },
                        {
                            "name": "task 3",
                            "args": ["Hello from task 3 which got no args from duplicate..."],
                            "function": "builtins.print",
                            "type": "python",
                        },
                    ],
                    "type": "dag",
                },
                "branch_data": ["Duplicated 1", "Duplicated 2"],
                "type": "branch",
            }
        ],
        "type": "dag",
}