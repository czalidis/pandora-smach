#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
import actionlib
#~ from geometry_msgs import Pose
from move_base_msgs.msg import * 


class MoveBaseActionStub:
	
	def __init__(self):
				
		self._actionStubServer = actionlib.SimpleActionServer('/navigation/move_base', MoveBaseAction, self.executeCb, False)
		self._actionStubServer.start()
		

	def executeCb(self,goal):
		rospy.sleep(4)
		self._actionStubServer.set_succeeded()


if __name__ == '__main__':
	rospy.init_node('move_base_action_stub')
	try:
		MoveBaseActionStub()
		rospy.spin()
	except rospy.ROSInterruptException:
		pass

