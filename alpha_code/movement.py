import sys
import rclpy
from rclpy.node import Node
from rclpy.signal import SignalHandlerOptions
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import Int8, Bool
from enum import Enum
import math
import random

LINEAR_VELOCITY = 0.3
ANGULAR_VELOCITY = 1.0
MB = 361.0
ALPHA = 3

class Outer_State(Enum):
    INITIAL = 0
    MOVE_AND_AVOID = 1
    TURNING = 2

class Inner_State(Enum):
    INITIAL = 0
    MOVE = 1
    AVOID = 2
    TURN = 3
    RAND_TURN = 4

class Action(Enum):
    ENTRY = 0
    DURING = 1
    EXIT = 2

class Position(Enum):
    left = 0
    right = 1

class Movement(Node):
    def __init__(self):
        super().__init__('movement')

        self.outer_state = Outer_State.INITIAL
        self.inner_state = Inner_State.INITIAL
        self.outer_action = Action.ENTRY
        self.inner_action = Action.ENTRY

        self.n = int(0)
        self.p = Position.left
        self.turned = False
        self.obstacle_found = False
        self.time_unit = 0.1
        self.timer_period = 0.1
        self.clock_MBC = 0
        self.waiting = 0
        self.wait = 0

        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('yaw', 0.0)
        self.robot_id = self.get_parameter('robot_id').value
        self.x = self.get_parameter('x').get_parameter_value().double_value
        self.y = self.get_parameter('y').get_parameter_value().double_value
        self.yaw = self.get_parameter('yaw').get_parameter_value().double_value

        self.timer = self.create_timer(self.timer_period, self.control_loop)

        self.move_publisher = self.create_publisher(Twist, '/move', 10)

        #Message type needs changing - maybe
        self.obstacle_subscriber = self.create_subscriber(Int8, '/obstacle', self.obstacle_callback, 10)
        self.neighbours_subscriber = self.create_subscriber(Int8, '/neighbours', self.neighbours_calback, 10)

    def since_clock_MBC(self): #Get current time since clock reset
        return self.timer_period * self.clock_MBC / self.time_unit

    def obstacle_callback(self, msg):
        if msg == 0:
            self.p = Position.left
        if msg == 1:
            self.p = Position.right
        self.obstacle_found = True

    def neighbours_callback(self, msg):
        self.n = int(msg)

    def control_loop(self):
        self.clock_MBC += 1
        match self.outer_state:
            case Outer_State.INITIAL:
                self.clock_MBC = 0
                self.obstacle_found = False
                self.outer_state = Outer_State.MOVE_AND_AVOID
            case Outer_State.MOVE_AND_AVOID:
                match self.outer_action:
                    case Action.ENTRY:
                        self.outer_action = Action.DURING
                    case Action.DURING:
                        match self.inner_state:
                            case Inner_State.INITIAL:
                                self.inner_state = Inner_State.MOVE
                            case Inner_State.MOVE:
                                match self.inner_action:
                                    case Action.ENTRY:
                                        msg = Twist()
                                        msg.linear.x = LINEAR_VELOCITY
                                        self.move_publisher.publish(msg)
                                        self.inner_action = Action.DURING
                                    case Action.DURING:
                                        if self.obstacle_found == True and self.since_clock_MBC()<MB-360/ANGULAR_VELOCITY:
                                            self.inner_action = Action.ENTRY
                                            self.inner_state = Inner_State.AVOID
                                    case _:
                                        pass
                            case Inner_State.AVOID:
                                match self.inner_action:
                                    case Action.ENTRY:
                                        msg = Twist()
                                        if self.p == Position.left:
                                            msg.angular.z = ANGULAR_VELOCITY
                                        else:
                                            msg.angular.z = -ANGULAR_VELOCITY
                                        self.move_publisher.publish(msg)
                                        self.waiting = self.since_clock_MBC()
                                        self.wait = math.floor(random.uniform(0, 1)*360/ANGULAR_VELOCITY)
                                        self.inner_action = Action.DURING
                                    case Action.DURING:
                                        if self.since_clock_MBC() - self.waiting >= self.wait:
                                            self.obstacle_found = False
                                            self.inner_action = Action.ENTRY
                                            self.inner_state = Inner_State.MOVE
                                    case _:
                                        pass
                            case _:
                                self.inner_state = Inner_State.INITIAL
                                self.inner_action = Action.ENTRY         
                        if self.since_clock_MBC() >= MB:
                            self.since_clock_MBC() = 0
                            self.inner_action = Action.ENTRY
                            self.outer_action = Action.ENTRY
                            self.inner_state = Inner_State.INITIAL
                            self.outer_state = Outer_State.TURNING
            case Outer_State.TURNING:
                match self.outer_action:
                    case Action.ENTRY:
                        self.turned = False
                    case Action.DURING:
                        match self.inner_state:
                            case Inner_State.INITIAL:
                                self.inner_action = Action.ENTRY
                                if self.n < ALPHA:
                                    self.inner_state = Inner_State.TURN
                                elif self.n >= ALPHA:
                                    self.inner_state = Inner_State.RAND_TURN
                            case Inner_State.TURN:
                                match self.inner_action:
                                    case Action.ENTRY:
                                        msg = Twist()
                                        msg.angular.z = ANGULAR_VELOCITY
                                        self.move_publisher.publish(msg)
                                        self.waiting = self.since_clock_MBC()
                                        self.inner_action = Action.DURING
                                    case Action.DURING:
                                        if self.since_clock_MBC() - self.waiting >= math.floor(180/ANGULAR_VELOCITY):
                                            self.turned = True
                                    case _:
                                        pass
                            case Inner_State.RAND_TURN:
                                match self.inner_action:
                                    case Action.ENTRY:
                                        msg = Twist()
                                        msg.angular.z = ANGULAR_VELOCITY
                                        self.move_publisher(msg)
                                        self.waiting = self.since_clock_MBC()
                                        self.wait = math.floor(random.uniform(0, 1)*360/ANGULAR_VELOCITY)
                                        self.inner_action = Action.DURING
                                    case Action.DURING:
                                        if self.since_clock_MBC() - self.waiting >= self.wait:
                                            self.turned = True
                                    case _:
                                        pass
                            case _:
                                self.inner_state = Inner_State.INITIAL
                                self.inner_action = Action.ENTRY
                        if self.turned == True:
                            self.inner_action = Action.ENTRY
                            self.outer_action = Action.ENTRY
                            self.inner_state = Inner_State.INITIAL
                            self.outer_state = Outer_State.MOVE_AND_AVOID

            case _:
                pass

    def destroy_node(self):
        super().destroy_node()

def main(args=None):
    rclpy.init(args = args, signal_handler_options = SignalHandlerOptions.NO)
    node = Movement()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    except ExternalShutdownException:
        sys.exit(1)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()