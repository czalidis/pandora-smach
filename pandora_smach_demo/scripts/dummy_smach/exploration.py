#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from move_base_msgs.msg import MoveBaseAction
from pandora_smach_demo_msgs.msg import SelectTargetAction, SelectTargetGoal, VictimFound

from smach import State, StateMachine, Concurrence
from smach_ros import SimpleActionState, MonitorState

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


def createTargetSelectorContainer():
	target_selection_goal = SelectTargetGoal()
	target_selection_goal.targetType = SelectTargetGoal.TYPE_EXPLORATION
	
	sm_target_selector = StateMachine(['target_sent','aborted'])
	
	with sm_target_selector:
		
		StateMachine.add('GET_TARGET', SimpleActionState('/select_target', SelectTargetAction, goal=target_selection_goal, result_slots=['target_pose']), transitions={'succeeded':'MOVE_BASE','aborted':'aborted'}, remapping={'target_pose':'next_target'})
		
		StateMachine.add('MOVE_BASE', SimpleActionState('/navigation/move_base', MoveBaseAction, goal_key='move_to_target'), transitions={'succeeded':'target_sent','aborted':'aborted'}, remapping={'next_target':'move_to_target'})
		
	return sm_target_selector


def createExplorationContainer():
	cc = Concurrence(outcomes=['next_target','victim_thermal','victim_camera'], default_outcome='next_target', outcome_map={'next_target':{'TARGET_CONTROLLER':'target_sent'},'victim_thermal':{'VICTIM_MONITOR':'victim_thermal'}, 'victim_camera':{'VICTIM_MONITOR':'victim_camera'}})
	
	with cc:
		Concurrence.add('TARGET_CONTROLLER', createTargetSelectorContainer())
		
		sm_victim_monitor = StateMachine(outcomes=['victim_thermal','victim_camera'])
		with sm_victim_monitor:
			sm_victim_monitor.userdata.victim_type = 0
						
			StateMachine.add('VICTIM_MONITORING', MonitorVictimState(), transitions={'invalid':'VICTIM_MONITORING', 'valid':'VICTIM_DECIDE'})
			
			StateMachine.add('VICTIM_DECIDE', DecideVictimState(), transitions={'thermal':'victim_thermal','camera':'victim_camera'})
			
		Concurrence.add('VICTIM_MONITOR', sm_victim_monitor)
		
	return cc
	
	
