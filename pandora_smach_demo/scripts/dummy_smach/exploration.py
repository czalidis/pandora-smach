#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from move_base_msgs.msg import MoveBaseAction
from pandora_smach_demo_msgs.msg import SelectTargetAction, SelectTargetGoal

from smach import State, StateMachine
from smach_ros import SimpleActionState


def createTargetSelectorContainer(out, target_type):
	target_selection_goal = SelectTargetGoal()
	if target_type == 'explore':
		target_selection_goal.targetType = SelectTargetGoal.TYPE_EXPLORATION
	elif target_type == 'victim':
		target_selection_goal.targetType = SelectTargetGoal.TYPE_VICTIM
	else:
		rospy.logerr('Wrong target type!')
	
	sm_target_selector = StateMachine(outcomes=out)
	
	with sm_target_selector:
		
		StateMachine.add('GET_TARGET', SimpleActionState('/select_target', SelectTargetAction, goal=target_selection_goal, result_slots=['target_pose']), transitions={'succeeded':'MOVE_BASE'}, remapping={'target_pose':'next_target'})
		
		StateMachine.add('MOVE_BASE', SimpleActionState('move_base', MoveBaseAction, goal_key='move_to_target'), transitions={'succeeded':'target_sent'}, remapping={'next_target':'move_to_target'})
		
	return sm_target_selector
