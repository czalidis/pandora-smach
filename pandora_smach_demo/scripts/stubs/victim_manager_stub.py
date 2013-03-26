#!/usr/bin/env python
import roslib; roslib.load_manifest('pandora_smach_demo')
import rospy
#~ import actionlib
#~ from geometry_msgs import Pose
from pandora_smach_demo_msgs.msg import VictimFound


class VictimManagerStub:
	
	def __init__(self):
				
		self.victimNotifierPub = rospy.Publisher('victim_found', VictimFound)
		
		
		victimFoundMsg = VictimFound(victimNotificationType = VictimFound.TYPE_THERMAL )
		#~ VictimFound.victimNotificationType =  VictimFound.TYPE_THERMAL
		while not rospy.is_shutdown():
			self.victimNotifierPub.publish(victimFoundMsg)
			rospy.sleep(35)
				
		#~ self._actionStubServer = actionlib.SimpleActionServer('/get_victim_queue', SelectTargetAction, self.executeCb, False)
		#~ self._actionStubServer.start()
		

	#~ def executeCb(self,goal):
		#~ 
		#~ result = GetTargetResult()
		#~ self._actionStubServer.set_succeeded(result)

	


if __name__ == '__main__':
	rospy.init_node('victim_manager_stub')
	try:
		VictimManagerStub()
		rospy.spin()
	except rospy.ROSInterruptException:
		pass

