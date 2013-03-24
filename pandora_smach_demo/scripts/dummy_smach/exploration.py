#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from pandora_smach_demo_msgs.msg import VictimFound

from smach import State, StateMachine, Concurrence
from smach_ros import SimpleActionState, MonitorState

import utils

class MonitorVictimState(MonitorState):
	def __init__(self):
		MonitorState.__init__(self,'/victim_found', VictimFound, self.monitor_cb)
		
	def monitor_cb(self, userdata, msg):
		if msg.victimNotificationType == msg.TYPE_THERMAL or msg.victimNotificationType == msg.TYPE_CAMERA:
			userdata.victim_type = msg.victimNotificationType
			return True
		else:
			return False

class DecideVictimState(State):
	def __init__(self):
		State.__init__(self,outcomes=['thermal','camera'])
	
	def execute(self, userdata):
		victim_msg = VictimFound()
		if userdata.victim_type == victim_msg.TYPE_THERMAL:
			return 'thermal'
		elif userdata.victim_type == victim_msg.TYPE_CAMERA:
			return 'camera'
		else:
			rospy.logerr('Wrong message type!')



def ExplorationContainer():
	cc = Concurrence(outcomes=['next_target','victim_thermal','victim_camera','aborted','preempted'], 
	default_outcome='next_target', outcome_map={'next_target':{'TARGET_CONTROLLER':'target_sent'},
	'victim_thermal':{'VICTIM_MONITOR':'victim_thermal'}, 'victim_camera':{'VICTIM_MONITOR':'victim_camera'}, 
	'preempted':{'TARGET_CONTROLLER':'preempted'}, 'aborted':{'TARGET_CONTROLLER':'aborted'}},
	child_termination_cb=lambda so: True)
	
	with cc:
		Concurrence.add('TARGET_CONTROLLER', utils.TargetSelectorContainer('explore'))
		
		sm_victim_monitor = StateMachine(outcomes=['victim_thermal','victim_camera','preempted'])
		with sm_victim_monitor:
			sm_victim_monitor.userdata.victim_type = 0
						
			StateMachine.add('VICTIM_MONITORING', MonitorVictimState(), 
			transitions={'invalid':'VICTIM_MONITORING', 'valid':'VICTIM_DECIDE', 'preempted':'preempted'})
			
			StateMachine.add('VICTIM_DECIDE', DecideVictimState(), 
			transitions={'thermal':'victim_thermal','camera':'victim_camera'})
			
		Concurrence.add('VICTIM_MONITOR', sm_victim_monitor)
		
	return cc
	
	
