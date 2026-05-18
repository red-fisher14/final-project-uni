import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from enum import Enum

LINEAR_VELOCITY = 0.3 #meters per second
ANGULAR_VELOCITY = 1.0 #radians per second
PI = math.pi

class State(Enum): #FSM states
    MOVING = 0
    TURNING = 1

class Action(Enum): #State actions
    ENTRY = 0
    DURING = 1
    EXIT = 2

class Movement(Node):
    def __init__(self):
        super().__init__('robot_controller')

        self.state = State.MOVING
        self.action = Action.ENTRY
        self.obstacle_found = False #Has an obstacle been detected?
        self.waiting = 0.1 #Ignores first clock increase
        
        #Clock
        self.clock_MBC = 0

        # Periodic callback for executing FSM
        self.timer_period = 0.1 # 100 milliseconds = 10 Hz for the control loop
        self.time_unit = 1 # 1 second is the value chosen for one 'time unit'
        self.timer = self.create_timer(self.timer_period, self.control_loop)

        #Publishers
        self.move_publisher = self.create_publisher(Twist, '/move', 10)
        self.stop_publisher = self.create_publisher(Empty, '/stop', 10)
        
        #Subscriber
        self.obstacle_subscriber = self.create_subscription(
            Empty,
            '/obstacle',
            self.obstacle_callback,
            10)
        
    def since_clock_MBC(self): #Get current time since clock reset
        return self.timer_period * self.clock_MBC / self.time_unit

    def obstacle_callback(self, msg): #Subscriber callback
        self.obstacle_found = True

    def control_loop(self):
        self.clock_MBC += 1 #Increment clock
        match self.state:
            case State.MOVING:
                match self.action:
                    case Action.ENTRY:
                        #move(lv, 0)
                        msg = Twist()
                        msg.linear.x = LINEAR_VELOCITY
                        msg.angular.z = 0.0
                        self.move_publisher.publish(msg)
                        #wait(1)
                        if self.since_clock_MBC() - self.waiting >= self.time_unit:
                            self.action = Action.DURING
                    case Action.DURING:
                        if self.obstacle_found == True:
                            self.clock_MBC = 0 #'#MBC'
                            self.action = Action.EXIT
                    case Action.EXIT:
                        #stop()
                        msg = Empty()
                        self.stop_publisher.publish(msg)
                        #wait(1)
                        if self.since_clock_MBC() >= self.time_unit:
                            self.waiting = self.since_clock_MBC()
                            self.action = Action.ENTRY
                            self.state = State.TURNING
                    case _:
                        pass
            case State.TURNING:
                match self.action:
                    case Action.ENTRY:
                        #move(0, av)
                        msg = Twist()
                        msg.linear.x = 0.0
                        msg.angular.z = ANGULAR_VELOCITY
                        self.move_publisher.publish(msg)
                        #wait(1)
                        if self.since_clock_MBC() - self.waiting >= self.time_unit:
                            self.action = Action.DURING
                    case Action.DURING:
                        #since(MBC)>=PI/av
                        if self.since_clock_MBC() >= PI/ANGULAR_VELOCITY:
                            self.waiting = self.since_clock_MBC()
                            self.obstacle_found = False
                            self.action = Action.ENTRY
                            self.state = State.MOVING
                    case _:
                        pass
            case _:
                pass

    def destroy_node(self):
        msg = Empty()
        self.stop_publisher.publish(msg)
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