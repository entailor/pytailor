"""
First execute this script with Part 2 commented out, then after all workflows are
finished execute the code under Part 2 into the same python session.
"""

worker_name = "test_worker"

from pytailor import Project

prj = Project.from_name("Test")


# Part 1. Start workflows
from test_2level_branching import wf as wf1
wf1.run(distributed=True, worker_name=worker_name)

# from test_engineering_example import wf as wf2
# wf2.run(distributed=True, worker_name=worker_name)

from test_many_branches import wf as wf3
wf3.run(distributed=True, worker_name=worker_name)

from test_multiple_files import wf as wf4
wf4.run(distributed=True, worker_name=worker_name)

from test_scope_inheritance import wf as wf5
wf5.run(distributed=True, worker_name=worker_name)

from test_unsymmetric_branch import wf as wf6
wf6.run(distributed=True, worker_name=worker_name)


# Part 2. make assertions after workflows are finished
# from test_2level_branching import target_outputs as target_outputs1
# wf1.refresh()
# assert wf1.outputs == target_outputs1
# assert wf1.state == "COMPLETED"
# prj.delete_workflow(wf1.id)
#
# # wf2.refresh()
# # assert wf2.state == "COMPLETED"
# # prj.delete_workflow(wf2.id)
#
# wf3.refresh()
# assert wf3.state == "COMPLETED"
# prj.delete_workflow(wf3.id)
#
# from test_multiple_files import target_outputs as target_outputs4
# wf4.refresh()
# assert wf4.outputs == target_outputs4
# assert wf4.state == "COMPLETED"
# prj.delete_workflow(wf4.id)
#
# from test_scope_inheritance import target_outputs as target_outputs5
# wf5.refresh()
# assert wf5.outputs == target_outputs5
# assert wf5.state == "COMPLETED"
# prj.delete_workflow(wf5.id)
#
# from test_unsymmetric_branch import target_outputs as target_outputs6
# wf6.refresh()
# assert wf6.outputs == target_outputs6
# assert wf6.state == "COMPLETED"
# prj.delete_workflow(wf6.id)
