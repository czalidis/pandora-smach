#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from pandora_smach_demo_msgs.msg import SelectTargetGoal, SelectTargetAction
from move_base_msgs.msg import MoveBaseAction

from smach import StateMachine
from smach_ros import SimpleActionState


def targetSelectionGoal(target_type):
	target_selection_goal = SelectTargetGoal()
	if target_type == 'explore':
		target_selection_goal.targetType = SelectTargetGoal.TYPE_EXPLORATION
	elif target_type == 'victim':
		target_selection_goal.targetType = SelectTargetGoal.TYPE_VICTIM
	else:
		rospy.logerr('Wrong target type!')
	return target_selection_goal
	
	
def TargetSelectorContainer(target_type):
	
	sm_target_selector = StateMachine(['target_sent','aborted','preempted'])
	
	with sm_target_selector:
		
		target_selection_goal = targetSelectionGoal(target_type)
		StateMachine.add('GET_TARGET', SimpleActionState('/select_target', SelectTargetAction, 
		goal=target_selection_goal, result_slots=['target_pose']), 
		transitions={'succeeded':'MOVE_BASE','aborted':'aborted','preempted':'preempted'}, 
		remapping={'target_pose':'next_target'})
		
		StateMachine.add('MOVE_BASE', SimpleActionState('/navigation/move_base', MoveBaseAction, goal_key='move_to_target'), 
		transitions={'succeeded':'target_sent','aborted':'aborted','preempted':'preempted'}, 
		remapping={'next_target':'move_to_target'})
		
	return sm_target_selector
	
def ParkContainer():
	return False
	
	
