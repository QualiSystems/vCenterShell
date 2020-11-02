'''
Copyright 2013-2014 Reubenur Rahman
All Rights Reserved
@author: reuben.13@gmail.com
'''

import atexit
import argparse
import sys
import time

from pyVmomi import vim, vmodl
from pyVim import connect
from pyVim.connect import Disconnect, SmartConnect, GetSi

inputs = {'vcenter_ip': '15.10.10.211',
          'vcenter_password': 'Password123',
          'vcenter_user': 'Administrator',
          'vm_name' : 'reuben-test',
          #create, remove or revert
          'operation' : 'create',
          'snapshot_name' : 'my_test_snapshot',
          }


def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def wait_for_task(task, raiseOnError=True, si=None, pc=None):
    if si is None:
        si = GetSi()

    if pc is None:
        sc = si.RetrieveContent()
        pc = sc.propertyCollector

    # First create the object specification as the task object.
    objspec = vmodl.Query.PropertyCollector.ObjectSpec()
    objspec.SetObj(task)

    # Next, create the property specification as the state.
    propspec = vmodl.Query.PropertyCollector.PropertySpec()
    propspec.SetType(vim.Task);
    propspec.SetPathSet(["info.state"]);
    propspec.SetAll(True)

    # Create a filter spec with the specified object and property spec.
    filterspec = vmodl.Query.PropertyCollector.FilterSpec()
    filterspec.SetObjectSet([objspec])
    filterspec.SetPropSet([propspec])

    # Create the filter
    filter = pc.CreateFilter(filterspec, True)

    # Loop looking for updates till the state moves to a completed state.
    taskName = task.GetInfo().GetName()
    update = pc.WaitForUpdates(None)
    state = task.GetInfo().GetState()
    while state != vim.TaskInfo.State.success and \
            state != vim.TaskInfo.State.error:
        if (state == 'running') and (taskName.info.name != "Destroy"):
            # check to see if VM needs to ask a question, thow exception
            vm = task.GetInfo().GetEntity()
            if vm is not None and isinstance(vm, vim.VirtualMachine):
                qst = vm.GetRuntime().GetQuestion()
            if qst is not None:
                raise Exception("Task blocked, User Intervention required")

    update = pc.WaitForUpdates(update.GetVersion())
    state = task.GetInfo().GetState()

    filter.Destroy()
    if state == "error" and raiseOnError:
        raise task.GetInfo().GetError()

    return state


def invoke_and_track(func, *args, **kw):
    try :
        task = func(*args, **kw)
        wait_for_task(task)
    except:
        raise

def main():

    try:
        si = None
        try:
            print("Trying to connect to VCENTER SERVER . . .")
            #si = connect.Connect(args.host, int(args.port), args.user, args.password, service="hostd")
            si = connect.Connect(inputs['vcenter_ip'], 443, inputs['vcenter_user'], inputs['vcenter_password'])
        except IOError as e:
            pass
            atexit.register(Disconnect, si)

        print("Connected to VCENTER SERVER !")

        content = si.RetrieveContent()

        operation = inputs['operation']

        vm_name = inputs['vm_name']
        snapshot_name = inputs['snapshot_name']

        vm = get_obj(content, [vim.VirtualMachine], vm_name)

        if operation == 'create':

            description = "Test snapshot"
            # Read about dumpMemory : http://pubs.vmware.com/vi3/sdk/ReferenceGuide/vim.VirtualMachine.html#createSnapshot
            dumpMemory = False
            quiesce = True

            invoke_and_track(vm.CreateSnapshot(snapshot_name, description, dumpMemory, quiesce))

        elif operation == 'remove':
            snapshots = vm.snapshot.rootSnapshotList

            for snapshot in snapshots:
                if snapshot_name == snapshot.name:
                    snap_obj = snapshot.snapshot
                    print(("Removing snapshot ", snap_obj))
                    invoke_and_track(snap_obj.RemoveSnapshot_Task(True))
                else:
                    print("Couldn't find any snapshots")

    except vmodl.MethodFault as e:
        print(("Caught vmodl fault: %s" % e.msg))
        return 1
    except Exception as e:
        if str(e).startswith("'vim.Task'"):
            return 1
        print(("Caught exception: %s" % str(e)))
        return 1

# Start program
if __name__ == "__main__":
    main()