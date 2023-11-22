# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import requests
import array

from bpy.types import Operator
from os import path
from .shared_props import CyberGafferSharedProps


class CyberGafferPlayOperator(Operator):
    bl_idname = "cybergaffer.play"
    bl_label = "CyberGaffer Play"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        props: CyberGafferSharedProps = scene.cyber_gaffer_shared_props
        target = bpy.data.objects[props.target_obj]

        print(f'Frame range: [[{props.start_frame}, {props.end_frame + 1}]')

        for frame in range(props.start_frame, props.end_frame + 1):
            scene.frame_set(frame)

            image_name = f'{target.name}_{frame}.exr'
            print(image_name)

            if bpy.data.images.find(image_name) == -1:
                bpy.ops.image.open(filepath=path.join(props.output_folder, image_name))
                bpy.data.images[image_name].pack()

            image = bpy.data.images[image_name]

            # width = image.size[0]
            # height = image.size[1]

            pixels = image.pixels
            rgb_pixels = [v for i, v in enumerate(pixels) if (i + 1) % 4 != 0]
            byte_array = array.array('f', rgb_pixels).tobytes()
            print(f'Pixels array length: {len(pixels)}, byte array length: {len(byte_array)}')

            url = f'http://{props.server_address}:{props.server_port}/UploadEnvironment'

            try:
                requests.post(url, data=byte_array, headers={'Content-Type': 'application/octet-stream'}, timeout=2.0)
                # print(f'Response: {response}')
            except ConnectionError:
                print('POST failed due to connection error')
            except TimeoutError:
                print('POST failed due to timeout')
            except requests.exceptions.RequestException as e:
                print(f'POST failed due to {e.strerror}')

        return {'FINISHED'}
