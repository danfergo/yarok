import yarok
from yarok import PlatformMJC, PlatformHW

from examples.vitac_world.grasp_rope_world import GraspRopeWorld, GraspRoleBehaviour

config = {
    'world': GraspRopeWorld,
    'behaviour': GraspRoleBehaviour,
    'defaults': {
        'environment': 'sim',
        'behaviour': {
            'dataset_path': '/home/danfergo/Projects/PhD/geltip_simulation/dataset/'
        },
        'components': {
            '/': {
                'object': 'cone'
            }
        }
    },
    'environments': {
        'sim': {
            'platform': {
                'class': PlatformMJC,
                'mode': 'view'
            },
            'inspector': True,
            'behaviour': {
                'dataset_name': 'sim_depth'
            }
        },
        'real': {
            'platform': PlatformHW,
            'behaviour': {
                'dataset_name': 'real_rgb'
            },
            # 'interfaces': {
            #     '/printer/printer': {
            #         'serial_path': '/dev/ttyUSB0'
            #     },
            #     '/printer': {
            #         'serial_path': '/dev/ttyUSB1'
            #     },
            #     '/geltip': {
            #         'cam_id': 0
            #     }
            # }
        }
    },
}

if __name__ == '__main__':
    yarok.run(config)
