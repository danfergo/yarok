import yarok
from examples.hello_world.pick_and_place_world import PickAndPlaceWorld

from yarok.components.ur5.ur5 import UR5
from yarok.components.robotiq_2f85.robotiq_2f85 import robotiq_2f85
from yarok import wait

class PickAndPlaceBehaviour:

    def __init__(self, arm: UR5, gripper: robotiq_2f85):
        self.arm = arm
        self.gripper = gripper
        self.BASE_POSITION = [0, 1., 1.]  # x,y,z position w.r.t the base of the robot, in meters.
        self.BLOCK_HEIGHT = 0.1
        self.TOWER_POS = [
            [-0.5, 1., 0],
            [0.5, 1., 0]
        ]
        self.N_BLOCKS = 3

    # def wake_up(self):
    #
    #
    #     self.arm.move_xyz(self.BASE_POSITION)
    #     for i in range(self.N_BLOCKS):
    #
    #         # move high up, prepare to grasp block
    #         p = [self.TOWER_POS[0][0] + (self.N_BLOCKS - i) * self.BLOCK_HEIGHT,
    #              self.TOWER_POS[0][1],
    #              0.1]
    #         self.arm.move_xyz(p)
    #         print('xxx')
    #         wait(lambda: self.arm.is_at(p))
    #
    #         # move to grasp the block
    #         p = [self.TOWER_POS[0][0] + (self.N_BLOCKS - i) * self.BLOCK_HEIGHT,
    #              self.TOWER_POS[0][1],
    #              self.TOWER_POS[0][2]]
    #
    #         self.arm.move_xyz(p)
    #         self.gripper1.open()
    #         wait(lambda: self.arm.is_at(p) and self.gripper1.is_open())
    #
    #         # close in, grasp the block
    #         self.gripper1.move(0.5)
    #         wait(lambda: self.gripper1.is_at(0.5))
    #
    #         # move high up
    #         p = [self.TOWER_POS[0][0] + (self.N_BLOCKS - i) * self.BLOCK_HEIGHT,
    #              self.TOWER_POS[0][1],
    #              0.1]
    #         self.arm.move(p)
    #         wait(lambda: self.arm.is_at(p))
    #
    #         # move to dropping zone, high up
    #         p = [self.TOWER_POS[1][0] + (self.N_BLOCKS - i) * self.BLOCK_HEIGHT,
    #              self.TOWER_POS[1][1],
    #              0.1]
    #         self.arm.move(p)
    #         wait(lambda: self.arm.is_at(p))
    #
    #         # move down to drop position
    #         p = [self.TOWER_POS[1][0] + i * self.BLOCK_HEIGHT,
    #              self.TOWER_POS[1][1],
    #              0.1]
    #         self.arm.move(p)
    #         wait(lambda: self.arm.is_at(p))
    #
    #
    #         # open gripper



# The same as running
# yarok run hello_world.pick_and_place_world hello_word.pick_and_place_behaviour
def main():
    import sys

    yarok.run(PickAndPlaceWorld,
              PickAndPlaceBehaviour,
              {
                  'platform_args': {
                      'viewer_mode': sys.argv[1]
                  }
              })


if __name__ == '__main__':
    main()
