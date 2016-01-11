# -*- coding: utf-8 -*-

"""
The most common network/Distributed Virtual Switch staff
"""

from pyVmomi import vim

from common.logger import getLogger
_logger = getLogger("vCenterCommon")


def network_is_standard(network):
    return isinstance(network, vim.Network) or (network and str(network).startswith("vim.Network:"))


def network_is_portgroup(network):
    return isinstance(network, vim.dvs.DistributedVirtualPortgroup) \
           or network and str(network).startswith("vim.dvs.VmwareDistributedVirtualSwitch:")
    #return True if network and str(network).startswith("vim.dvs.VmwareDistributedVirtualSwitch:") else False


#todo - REMOVE INFO bellow - just for development purposes
"""
(vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   port = (vim.dvs.PortConnection) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      switchUuid = '4a 56 22 50 c9 99 03 c0-03 94 cf df c1 62 99 ef',
      portgroupKey = 'dvportgroup-12521',
      portKey = '425',
      connectionCookie = 185489114
   }
}
               Array: <class 'pyVmomi.VmomiSupport.vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo[]'>
     dynamicProperty: (vmodl.DynamicProperty) []
         dynamicType: None
                port: (vim.dvs.PortConnection) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   switchUuid = '4a 56 22 50 c9 99 03 c0-03 94 cf df c1 62 99 ef',
   portgroupKey = 'dvportgroup-12521',
   portKey = '425',
   connectionCookie = 185489114
}
"""

"""

'vim.dvs.DistributedVirtualPortgroup:dvportgroup-12337'
               Array: <class 'pyVmomi.VmomiSupport.vim.dvs.DistributedVirtualPortgroup[]'>
DVPortgroupRollback_Task: <function <lambda> at 0x7f1d758f4410>
             Destroy: <function <lambda> at 0x7f1d758f4410>
      DestroyNetwork: <function <lambda> at 0x7f1d758f4410>
        Destroy_Task: <function <lambda> at 0x7f1d758f4410>
         Reconfigure: <function <lambda> at 0x7f1d758f4410>
ReconfigureDVPortgroup_Task: <function <lambda> at 0x7f1d758f4410>
              Reload: <function <lambda> at 0x7f1d758f4410>
              Rename: <function <lambda> at 0x7f1d758f4410>
         Rename_Task: <function <lambda> at 0x7f1d758f4410>
            Rollback: <function <lambda> at 0x7f1d758f4410>
      SetCustomValue: <function <lambda> at 0x7f1d758f4410>
 alarmActionsEnabled: True
      availableField: (vim.CustomFieldsManager.FieldDef) []
              config: (vim.dvs.DistributedVirtualPortgroup.ConfigInfo) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   key = 'dvportgroup-12337',
   name = 'aa-dvPortGroup2A',
   numPorts = 32,
   distributedVirtualSwitch = 'vim.dvs.VmwareDistributedVirtualSwitch:dvs-11822',
   defaultPortConfig = (vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      blocked = (vim.BoolPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = false
      },
      vmDirectPathGen2Allowed = (vim.BoolPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = false
      },
      inShapingPolicy = (vim.dvs.DistributedVirtualPort.TrafficShapingPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         enabled = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = false
         },
         averageBandwidth = (vim.LongPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 100000000L
         },
         peakBandwidth = (vim.LongPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 100000000L
         },
         burstSize = (vim.LongPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 104857600L
         }
      },
      outShapingPolicy = (vim.dvs.DistributedVirtualPort.TrafficShapingPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         enabled = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = false
         },
         averageBandwidth = (vim.LongPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 100000000L
         },
         peakBandwidth = (vim.LongPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 100000000L
         },
         burstSize = (vim.LongPolicy) {
            dynamicType = <unset>,
            inherited = true,
            value = 104857600L
         }
      },
      vendorSpecificConfig = (vim.dvs.DistributedVirtualPort.VendorSpecificConfig) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         keyValue = (vim.dvs.KeyedOpaqueBlob) []
      },
      networkResourcePoolKey = (vim.StringPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = '-1'
      },
      filterPolicy = (vim.dvs.DistributedVirtualPort.FilterPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         filterConfig = (vim.dvs.DistributedVirtualPort.FilterConfig) []
      },
      vlan = (vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = false,
         vlanId = 32
      },
      qosTag = (vim.IntPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = -1
      },
      uplinkTeamingPolicy = (vim.dvs.VmwareDistributedVirtualSwitch.UplinkPortTeamingPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         policy = (vim.StringPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 'loadbalance_srcid'
         },
         reversePolicy = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = true
         },
         notifySwitches = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = true
         },
         rollingOrder = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = false
         },
         failureCriteria = (vim.dvs.VmwareDistributedVirtualSwitch.FailureCriteria) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            checkSpeed = (vim.StringPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = 'minimum'
            },
            speed = (vim.IntPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = 10
            },
            checkDuplex = (vim.BoolPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = false
            },
            fullDuplex = (vim.BoolPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = false
            },
            checkErrorPercent = (vim.BoolPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = false
            },
            percentage = (vim.IntPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = 0
            },
            checkBeacon = (vim.BoolPolicy) {
               dynamicType = <unset>,
               dynamicProperty = (vmodl.DynamicProperty) [],
               inherited = true,
               value = false
            }
         },
         uplinkPortOrder = (vim.dvs.VmwareDistributedVirtualSwitch.UplinkPortOrderPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            activeUplinkPort = (str) [
               'dvUplink1',
               'dvUplink2',
               'dvUplink3',
               'dvUplink4'
            ],
            standbyUplinkPort = (str) []
         }
      },
      securityPolicy = (vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = false,
         allowPromiscuous = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = false,
            value = true
         },
         macChanges = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = false,
            value = false
         },
         forgedTransmits = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = false,
            value = true
         }
      },
      ipfixEnabled = (vim.BoolPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = false
      },
      txUplink = (vim.BoolPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         value = false
      },
      lacpPolicy = (vim.dvs.VmwareDistributedVirtualSwitch.UplinkLacpPolicy) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         inherited = true,
         enable = (vim.BoolPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = false
         },
         mode = (vim.StringPolicy) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            inherited = true,
            value = 'passive'
         }
      }
   },
   description = <unset>,
   type = 'earlyBinding',
   policy = (vim.dvs.VmwareDistributedVirtualSwitch.VMwarePortgroupPolicy) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      blockOverrideAllowed = true,
      shapingOverrideAllowed = false,
      vendorConfigOverrideAllowed = false,
      livePortMovingAllowed = false,
      portConfigResetAtDisconnect = true,
      networkResourcePoolOverrideAllowed = false,
      trafficFilterOverrideAllowed = false,
      vlanOverrideAllowed = false,
      uplinkTeamingOverrideAllowed = false,
      securityPolicyOverrideAllowed = false,
      ipfixOverrideAllowed = false
   },
   portNameFormat = <unset>,
   scope = (vim.ManagedEntity) [],
   vendorSpecificConfig = (vim.dvs.KeyedOpaqueBlob) [],
   configVersion = '0',
   autoExpand = true,
   vmVnicNetworkResourcePoolKey = <unset>
}
         configIssue: (vim.event.Event) []
        configStatus: green
         customValue: (vim.CustomFieldsManager.Value) []
  declaredAlarmState: (vim.alarm.AlarmState) []
      disabledMethod: (str) []
       effectiveRole: (int) [
   -1
]
                host: (ManagedObject) [
   'vim.HostSystem:host-15',
   'vim.HostSystem:host-13'
]
                 key: dvportgroup-12337
                name: aa-dvPortGroup2A
       overallStatus: green
              parent: 'vim.Folder:group-n6'
          permission: (vim.AuthorizationManager.Permission) []
            portKeys: (str) [
   '264',
   '265',
   '266',
   '267',
   '268',
   '269',
   '270',
   '271',
   '272',
   '273',
   '274',
   '275',
   '276',
   '277',
   '278',
   '279',
   '280',
   '281',
   '282',
   '283',
   '284',
   '285',
   '286',
   '287',
   '288',
   '289',
   '290',
   '291',
   '292',
   '293',
   '294',
   '295'
]
          recentTask: (ManagedObject) []
      setCustomValue: <function <lambda> at 0x7f1d758f4410>
             summary: (vim.Network.Summary) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   network = 'vim.dvs.DistributedVirtualPortgroup:dvportgroup-12337',
   name = 'aa-dvPortGroup2A',
   accessible = true,
   ipPoolName = '',
   ipPoolId = <unset>
}
                 tag: (vim.Tag) []
 triggeredAlarmState: (vim.alarm.AlarmState) []
               value: (vim.CustomFieldsManager.Value) []
                  vm: (ManagedObject) []
"""


"""
(vim.vm.device.VirtualDeviceSpec) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   operation = 'add',
   fileOperation = <unset>,
   device = (vim.vm.device.VirtualVmxnet3) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      key = 0,
      deviceInfo = (vim.Description) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         label = 'aa-dvPortGroup2A',
         summary = 'aa-dvPortGroup2A'
      },
      backing = (vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         port = (vim.dvs.PortConnection) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            switchUuid = '4a 56 22 50 c9 99 03 c0-03 94 cf df c1 62 99 ef',
            portgroupKey = 'dvportgroup-12337',
            portKey = <unset>,
            connectionCookie = <unset>
         }
      },
      connectable = (vim.vm.device.VirtualDevice.ConnectInfo) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         startConnected = true,
         allowGuestControl = true,
         connected = false,
         status = <unset>
      },
      slotInfo = <unset>,
      controllerKey = <unset>,
      unitNumber = <unset>,
      addressType = <unset>,
      macAddress = <unset>,
      wakeOnLanEnabled = true,
      resourceAllocation = <unset>,
      externalId = <unset>,
      uptCompatibilityEnabled = <unset>
   },
   profile = (vim.vm.ProfileSpec) []
}
               Array: <class 'pyVmomi.VmomiSupport.vim.vm.device.VirtualDeviceSpec[]'>
              device: (vim.vm.device.VirtualVmxnet3) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   key = 0,
   deviceInfo = (vim.Description) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      label = 'aa-dvPortGroup2A',
      summary = 'aa-dvPortGroup2A'
   },
   backing = (vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      port = (vim.dvs.PortConnection) {
         dynamicType = <unset>,
         dynamicProperty = (vmodl.DynamicProperty) [],
         switchUuid = '4a 56 22 50 c9 99 03 c0-03 94 cf df c1 62 99 ef',
         portgroupKey = 'dvportgroup-12337',
         portKey = <unset>,
         connectionCookie = <unset>
      }
   },
   connectable = (vim.vm.device.VirtualDevice.ConnectInfo) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      startConnected = true,
      allowGuestControl = true,
      connected = false,
      status = <unset>
   },
   slotInfo = <unset>,
   controllerKey = <unset>,
   unitNumber = <unset>,
   addressType = <unset>,
   macAddress = <unset>,
   wakeOnLanEnabled = true,
   resourceAllocation = <unset>,
   externalId = <unset>,
   uptCompatibilityEnabled = <unset>
}
     dynamicProperty: (vmodl.DynamicProperty) []
         dynamicType: None
       fileOperation: None
           operation: add
             profile: (vim.vm.ProfileSpec) []
"""

"""
'vim.Task:task-34813'
               Array: <class 'pyVmomi.VmomiSupport.vim.Task[]'>
              Cancel: <function <lambda> at 0x7f7a6d043848>
          CancelTask: <function <lambda> at 0x7f7a6d043848>
      SetCustomValue: <function <lambda> at 0x7f7a6d043848>
            SetState: <function <lambda> at 0x7f7a6d043848>
  SetTaskDescription: <function <lambda> at 0x7f7a6d043848>
        SetTaskState: <function <lambda> at 0x7f7a6d043848>
   UpdateDescription: <function <lambda> at 0x7f7a6d043848>
      UpdateProgress: <function <lambda> at 0x7f7a6d043848>
      availableField: (vim.CustomFieldsManager.FieldDef) []
                info: (vim.TaskInfo) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   key = 'task-34813',
   task = 'vim.Task:task-34813',
   description = <unset>,
   name = vim.ManagedEntity.Destroy,
   descriptionId = 'dvs.DistributedVirtualPortgroup.destroy',
   entity = 'vim.dvs.DistributedVirtualPortgroup:dvportgroup-12520',
   entityName = 'aa-dvPortGroup2',
   locked = (vim.ManagedEntity) [],
   state = 'success',
   cancelled = false,
   cancelable = false,
   error = <unset>,
   result = <unset>,
   progress = <unset>,
   reason = (vim.TaskReasonUser) {
      dynamicType = <unset>,
      dynamicProperty = (vmodl.DynamicProperty) [],
      userName = 'QUALISYSTEMS\\sergii.t'
   },
   queueTime = 2016-01-04T09:45:38.744637Z,
   startTime = 2016-01-04T09:45:38.745638Z,
   completeTime = 2016-01-04T09:45:39.066946Z,
   eventChainId = 255494,
   changeTag = <unset>,
   parentTaskKey = <unset>,
   rootTaskKey = <unset>,
   activationId = <unset>
}
      setCustomValue: <function <lambda> at 0x7f7a6d043848>
               value: (vim.CustomFieldsManager.Value) []
"""