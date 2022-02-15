import sys

import yarok.__main__


# from src.env import yarok
# from yarok.worlds.empty_world.empty_world import EmptyWorld


def main():
    yarok.__main__.main()

    # yarok.run(EmptyWorld, {
    #     'platform_args': {
    #         'viewer_mode': sys.argv[1]
    #     }
    # })

    # environment = SimEnvironment(
    #     mode='view',
    #     path='/home/danfergo/Projects/PhD/mj_geltip_sim/src/env/empty_world.xml'
    #     # path='/home/danfergo/Projects/PhD/mj_geltip_sim/src/_models/rope.xml'
    # )

    # ur5 = UR5(environment)

    # while True:
    #     environment.step()
    # ur5.step()

    # print(environment.sim.model.actuator_id2name(50))
    # print(dir(environment.sim.model))
    # print(environment.sim.model.actuator_names)
    # print(environment.sim.model.actuator_name2id('arm_joint1_motor'))
    # print(environment.sim.model.sensor_name2id('arm_joint1_sensor'))
    # print(environment.sim.data.ctrl)
    # print(environment.sim.data.get_sensor('arm_joint0_sensor'))
    # print(dir(environment.sim.data))

    # environment.sim.data.ctrl[0] = pid.output
    # pass


if __name__ == '__main__':
    main()
