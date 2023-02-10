#!/usr/bin/env python3

# my NAME :Ahmed Kamal Eldin Hussein ElSenussi

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg  import Pose
import math
import random
from turtlesim.srv import Spawn
from turtlesim.srv import Kill
from std_srvs.srv import Empty

class mNode (Node):

    def __init__(self):
        super().__init__("mover")

        self.x_goal = random.uniform(1, 10)
        self.y_goal = random.uniform(1, 10)
        self.counter = 0
        self.current_name = ""

        self.putTurtleClient = self.create_client(Spawn, "spawn")
        self.putTurtle_call()

        self.control = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_listener = self.create_subscription(Pose, "/turtle1/pose", self.control_call, 10)

        self.killTurtle = self.create_client(Kill, "kill")
        self.clearLine = self.create_client(Empty, "clear")

    #-------------------------------------------------------

    def killTurtle_call(self):
 
        rq = Kill.Request()
        rq.name = self.current_name

        comeKill = self.killTurtle.call_async(rq)
        comeKill.add_done_callback(self.killing)
    def killing(self, msg):
        print("")   

    #-------------------------------------------------------    

    def clear(self):
        req = Empty.Request()
        self.clearLine.call_async(req)

    #------------------------------------------------------

    def putTurtle_call(self):

        rq = Spawn.Request()
        rq.x = self.x_goal
        rq.y = self.y_goal
        rq.theta = 0.0
        rq.name = ''

        comming = self.putTurtleClient.call_async(rq)
        comming.add_done_callback(self.putting)

    def putting(self, rsp):
        self.current_name = rsp.result().name

    #--------------------------------------------------------

    def control_call(self, pose : Pose):

        k_linear = 0.95
        distance = abs(math.sqrt((self.x_goal - pose.x)**2+(self.y_goal - pose.y)**2))
        linear_speed = distance * k_linear

        #--------------------------------------------------------------------------------
        k_angular = 4.0
        desired_angle_goal = math.atan2((self.y_goal - pose.y), (self.x_goal - pose.x))
        ang_err = desired_angle_goal - pose.theta

        if ang_err > math.pi:
            ang_err -= 2*math.pi

        elif ang_err < -math.pi:
            ang_err += 2*math.pi
 
        angular_speed = ang_err * k_angular 
        #--------------------------------------------------------------------------------
        cmd = Twist()
        cmd.linear.x = linear_speed + 1.0
        cmd.angular.z = angular_speed 

        self.control.publish(cmd)

        if distance < 0.53:

            self.counter += 1

            print(f"Goal Reached (x = {round(self.x_goal)}, y ={round(self.y_goal)})")
            print(f'Eat {self.counter} Turtles')

            self.x_goal = random.uniform(1, 10) 
            self.y_goal = random.uniform(1, 10) 

            self.killTurtle_call()
            self.putTurtle_call()
            self.clear()

def main(args = None):
    rclpy.init()
    node = mNode()
    rclpy.spin(node)
    rclpy.shutdown()

main()
         