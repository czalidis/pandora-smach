#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros


from smach import State, StateMachine, Concurrence
from smach_ros import SimpleActionState, MonitorState

from pandora_smach_demo_msgs.msg import InitialTurnAction

import utils

def IdentificationSimpleContainer():
	
	sm_identification_simple = StateMachine(['parked','aborted','preempted'])
	
	with sm_identification_simple:
		
		StateMachine.add('GET_VICTIMS', SimpleActionState('/navigation/initial_turn', InitialTurnAction), 
		transitions={'succeeded':'GO_TO_VICTIM'})
		
		StateMachine.add('GO_TO_VICTIM', utils.TargetSelectorContainer('victim'), 
		transitions={'target_sent':'PARK','aborted':'aborted','preempted':'preempted'})
		
		StateMachine.add('PARK', SimpleActionState('/navigation/initial_turn', InitialTurnAction), 
		transitions={'succeeded':'parked','aborted':'aborted','preempted':'preempted'})
	
	return sm_identification_simple


def IdentificationTrackingContainer():
	
	sm_identification_tracking = StateMachine(['identification_finished','aborted','preempted'])
	
	with sm_identification_tracking:
		
		StateMachine.add('DO_NOTHING', SimpleActionState('/navigation/initial_turn', InitialTurnAction), 
		transitions={'succeeded':'identification_finished','aborted':'aborted','preempted':'preempted'})
	
	return sm_identification_tracking
	
	
	
