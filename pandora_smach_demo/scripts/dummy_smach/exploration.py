#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from pandora_smach_demo_msgs.msg import VictimFound

from smach import State, StateMachine, Concurrence
from smach_ros import SimpleActionState
from my_monitor_state import MyMonitorState

import utils

class MonitorVictimState(MyMonitorState):
	def __init__(self, input_keys=[], output_keys=[]):
		MyMonitorState.__init__(self,'/victim_found', VictimFound, 
		self.monitor_cb, ik=input_keys, ok=output_keys)
		
	def monitor_cb(self, userdata, msg):
		if msg.victimNotificationType == msg.TYPE_THERMAL or msg.victimNotificationType == msg.TYPE_CAMERA:
			userdata[0].victim_type = msg.victimNotificationType
			return False
		else:
			return True

class DecideVictimState(State):
	def __init__(self):
		State.__init__(self,outcomes=['thermal','camera'], input_keys=['victim_type'])
	
	def execute(self, userdata):
		victim_msg = VictimFound()
		if userdata.victim_type == victim_msg.TYPE_THERMAL:
			return 'thermal'
		elif userdata.victim_type == victim_msg.TYPE_CAMERA:
			return 'camera'
		else:
			rospy.logerr('Wrong message type!'+' victim_type = '+str(userdata.victim_type))

def _termination_cb(outcome_map):
	#~ print outcome_map
	#~ if outcome_map['TARGET_CONTROLLER'] == 'target_sent' and outcome_map['VICTIM_MONITOR'] == None:
		#~ return False
	return True

def ExplorationContainer():
	cc = Concurrence(outcomes=['next_target','victim_thermal','victim_camera','aborted','preempted'], 
	default_outcome='next_target', outcome_map={'next_target':{'TARGET_CONTROLLER':'target_sent'},
	'victim_thermal':{'VICTIM_MONITOR':'victim_thermal'}, 'victim_camera':{'VICTIM_MONITOR':'victim_camera'}, 
	'preempted':{'TARGET_CONTROLLER':'preempted','VICTIM_MONITOR':'preempted'}, 'aborted':{'TARGET_CONTROLLER':'aborted'}},
	child_termination_cb=_termination_cb)
	
	with cc:
		Concurrence.add('TARGET_CONTROLLER', utils.TargetSelectorContainer('explore'))
		
		sm_victim_monitor = StateMachine(outcomes=['victim_thermal','victim_camera','preempted'])
		sm_victim_monitor.userdata.victim_type = 0
		with sm_victim_monitor:
			
			StateMachine.add('VICTIM_MONITORING', MonitorVictimState(
			input_keys=['victim_type'], output_keys=['victim_type']), 
			transitions={'invalid':'VICTIM_DECIDE', 'valid':'VICTIM_MONITORING', 'preempted':'preempted'}, 
			remapping={'victim_type':'victim_type'})
			
			StateMachine.add('VICTIM_DECIDE', DecideVictimState(), 
			transitions={'thermal':'victim_thermal','camera':'victim_camera'})
			
		Concurrence.add('VICTIM_MONITOR', sm_victim_monitor)
		
	return cc
	
	
