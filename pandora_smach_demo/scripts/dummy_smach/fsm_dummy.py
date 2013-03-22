#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import smach
import smach_ros

from move_base_msgs.msg import MoveBaseAction
from pandora_smach_demo_msgs.msg import InitialTurnAction

from smach import State, StateMachine
from smach_ros import SimpleActionState

import exploration 

def main():
    rospy.init_node("fsm_dummy")

    sm = StateMachine(outcomes=['succeeded','aborted','preempted'])
    with sm:
        StateMachine.add('INITIAL_TURN', SimpleActionState('/navigation/initial_turn', InitialTurnAction), transitions={'succeeded':'TARGET_CONTROLLER'})
        
        sm_target_selector = exploration.createTargetSelectorContainer(['target_sent'], 'explore')
        StateMachine.add('TARGET_CONTROLLER', sm_target_selector, transitions={'target_sent':'succeeded'})

    sis = smach_ros.IntrospectionServer('smach_server', sm, '/')
    sis.start()
    sm.execute()
    rospy.spin()
    sis.stop()

if __name__=="__main__":
    main()

