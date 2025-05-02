import rclpy
from rclpy.node import Node
import matplotlib.pyplot as plt
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class ArucoFinder(Node):
    def __init__(self):
        super().__init__('aruco_finder')

        # Publisher to cmd_vel
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber to camera raw image
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

        self.bridge = CvBridge()

        # Set ArUco dictionary and parameters
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        self.aruco_params = cv2.aruco.DetectorParameters_create()

        # To control robot movement state
        self.found_aruco = False

        # PID controller parameters
        self.kp = 0.003
        self.kd = 0.0002
        self.ki = 0.0000
        self.prev_error = 0.0
        self.integral = 0.0
        self.dt = 1/30.0  # 30 FPS

        # Output limits
        self.max_output = 10.0
        self.min_output = -self.max_output

        # Deadband threshold
        self.deadband = 0  # pixels

        self.image_width = None  # will be updated when first image comes
        self.error_history = []
        self.output_history = []
    def image_callback(self, msg):
        # Convert ROS image to OpenCV image
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

        # Save image width if unknown
        if self.image_width is None:
            self.image_width = frame.shape[1]

        # Detect ArUco markers
        corners, ids, _ = cv2.aruco.detectMarkers(frame, self.aruco_dict, parameters=self.aruco_params)

        twist = Twist()

        if ids is not None:
            # ArUco detected
            self.found_aruco = True

            # Calculate marker center position
            for corner in corners:
                center_x = int((corner[0][0][0] + corner[0][2][0]) / 2)
                center_y = int((corner[0][0][1] + corner[0][2][1]) / 2)

                self.get_logger().info(f"Found ArUco at (x={center_x}, y={center_y})")

                # PID control
                error = (self.image_width / 2) - center_x  # positive if marker is left of center

                # Apply deadband
                if abs(error) < self.deadband:
                    error = 0.0

                self.integral += error * self.dt
                derivative = (error - self.prev_error) / self.dt
                output = self.kp * error + self.ki * self.integral + self.kd * derivative
                self.prev_error = error

                # Apply output limit
                output = max(min(output, self.max_output), self.min_output)

                # Save error and output
                self.error_history.append(error)
                self.output_history.append(output)

                # Set angular velocity based on PID output
                twist.angular.z = output
                twist.linear.x = 0.0
                self.cmd_vel_pub.publish(twist)

        else:
            # No ArUco found
            if not self.found_aruco:
                twist.angular.z = self.min_output  # Rotate slowly to search
                twist.linear.x = 0.0
                self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoFinder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        # Assume self.error_history and self.output_history are your existing lists
        samples = len(node.error_history)
        time = np.arange(samples) / 30  # 30 samples per second

        # Create the figure and subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

        # Plot error history
        ax1.plot(time, node.error_history)
        ax1.set_ylabel('Error')
        ax1.set_title('Error over Time')

        # Plot output history
        ax2.plot(time, node.output_history)
        ax2.set_ylabel('PID Output')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_title('PID Output over Time')

        # Adjust layout
        plt.tight_layout()
        plt.show()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
