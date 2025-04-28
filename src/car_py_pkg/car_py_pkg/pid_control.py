#!/usr/bin/env python3
import rclpy
import math

from rclpy.node import Node
from geometry_msgs.msg import Pose2D,Twist

class PID_control_Orientation():
    def __init__(self):
        self.kp = 1
        self.kd = 2

        self.r = ...


        self.prev_error = None

    def calculation(self,theta_d,theta_current,dt,distance_error):
        self.angular_error = normalize_angular(theta_d - theta_current)
        # if distance_error > 1.0:
        #     self.kp = 2.0
        #     self.kd = 1.0
        # elif distance_error > 0.5:
        #     self.kp = 1.0
        #     self.kd = 0.5
        # else:
        #     self.kp = 0.5
        #     self.kd = 0.2

        if self.prev_error != None:
            self.angular_error_dot = (self.angular_error - self.prev_error) * dt
            self.prev_error = self.angular_error
        else:
            self.angular_error_dot = 0
            self.prev_error = self.angular_error
        
        #print(f"self.prev_error = {self.prev_error}")

        self.w_comm = self.kp * self.angular_error + self.kd * self.angular_error_dot
        return self.w_comm
        #print(f"W_comm = {self.w_comm}")
        # if status == 'r':
        #     return (self.w_comm / self.r)
        # else:
        #     return -(self.w_comm / self.r)

class control_logic_node(Node):
    def __init__(self):
        super().__init__("pid_control")
        # self.service = self.create_service(
        #     DesiredPos,
        #     "collect_desired_pos",
        #     self.response_callback
        # )

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel',10)

        #self.pose_subsriber_ = self.create_subscription(Pose2D,'random_pos_output_node',self.time_callback,10)

        self.dt = 0.1

        self.goal_pose = Pose2D()
        self.current_pose = Pose2D()

        self.current_pose.x = 5.544445
        self.current_pose.y = 5.544445
        self.current_pose.theta = 0.0

        #self.Position_Control = PID_control()
        self.Orientaion_Control = PID_control_Orientation()

        self.control_timer = self.create_timer(self.dt, self.control_loop)

        self.control_active = False

    #def chech_if_reach():


    def response_callback(self, request, response):
        self.goal_pose.x = request.x_d
        self.goal_pose.y = request.y_d
        
        self.get_logger().info(f"Received Goal -> x: {request.x_d}, y: {request.y_d}")
        self.get_logger().info(f"Starting Control Algorithm ...")

        self.control_active = True

        #while rclpy.ok() and self.control_active:
            #rclpy.spin_once(self,timeout_sec=0.1)

        response.success = True
        return response

    def control_loop(self):
        if not self.control_active:
            return 

        dx = self.goal_pose.x - self.current_pose.x
        dy = self.goal_pose.y - self.current_pose.y
        #self.get_logger().info(f"{dx} {dy}")
        self.goal_pose.theta = math.atan2(dy,dx)
        self.angular_error = normalize_angular(self.goal_pose.theta - self.current_pose.theta)
        self.distance_error = math.hypot(dy,dx)

        twist = Twist()

        allowed_angular_error = max(0.05, min(0.2, self.distance_error * 0.5))

        angular_threshold = 0.018
        distance_threshold = 0.05

        #Orientation Control
        if abs(self.angular_error) > angular_threshold:
            twist.angular.z = self.Orientaion_Control.calculation(self.goal_pose.theta,self.current_pose.theta,self.dt,self.distance_error)
            twist.linear.x = 0.0
            self.get_logger().info(f"The robot is currently turning")
        elif abs(self.angular_error) <= angular_threshold and self.distance_error > distance_threshold:
            twist.angular.z = 0.0
            twist.linear.x = min(0.5, 0.2 + 0.5 * self.distance_error)
            self.get_logger().info(f"The robot is currently moving")
        else:
            twist.angular.z = 0.0
            twist.linear.x = 0.0
            self.get_logger().info(f"The robot has reached the destination")

        #self.get_logger().info(f"current z is {twist.angular.z}")
        #self.get_logger().info(f"current x is {twist.angular.x}")

        
        self.cmd_pub.publish(twist)

        self.current_pose.theta += twist.angular.z * self.dt
        self.current_pose.x += twist.linear.x * math.cos(self.current_pose.theta) * self.dt
        self.current_pose.y += twist.linear.x * math.sin(self.current_pose.theta) * self.dt
        
        #self.get_logger().info(f"current theta is: {self.current_pose.theta}")

    def time_callback(self, msg : Pose2D):
        self.get_logger().info(str(msg.x) + " " + str(msg.y))

def normalize_angular(angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    node = control_logic_node()
    rclpy.spin(node)
    rclpy.shutdown()