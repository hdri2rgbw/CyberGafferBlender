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

    backup_start_frame = None
    backup_end_frame = None
    backup_current_frame = None

    @classmethod
    def poll(cls, context):
        # TODO: check textures to selected range
        return True

    @staticmethod
    def on_frame_changed(scene, depsgraph):
        # TODO: check scene?
        current_frame = scene.frame_current
        props: CyberGafferSharedProps = scene.cyber_gaffer_shared_props

        image_name = f'{props.target_obj}_{current_frame}.exr'
        print(image_name)

        # if bpy.data.images.find(image_name) == -1:
        bpy.ops.image.open(filepath=path.join(props.output_folder, image_name))
        bpy.data.images[image_name].pack()

        image = bpy.data.images[image_name]

        pixels = image.pixels
        rgb_pixels = [v for i, v in enumerate(pixels) if (i + 1) % 4 != 0]
        byte_array = array.array('f', rgb_pixels).tobytes()

        url = f'http://{props.server_address}:{props.server_port}/UploadEnvironment'

        fps = scene.render.fps
        fps_base = 1.0
        if hasattr(scene.render, 'fps_base'):
            fps_base = scene.render.fps_base

        try:
            requests.post(url, data=byte_array, headers={'Content-Type': 'application/octet-stream'}, timeout=1.0 / (fps / fps_base) / 2.0)
            # print(f'Response: {response}')
        except ConnectionError:
            print('POST failed due to connection error')
        except TimeoutError:
            print('POST failed due to timeout')
        except requests.exceptions.RequestException as e:
            print(f'POST failed due to {e}')

        try:
            image.user_clear()
            remove = True
        except:
            remove = False

        if remove:
            try:
                bpy.data.images.remove(image)
            except:
                print(f'Image {image.name} cannot be removed')

        if current_frame == props.end_frame:
            bpy.ops.screen.animation_cancel(False)

    @staticmethod
    def on_animation_playback_post(start_frame, end_frame, current_frame):
        def handler(scene, depsgraph):
            # self.restore_settings(scene)
            bpy.app.handlers.animation_playback_post.clear()
            bpy.app.handlers.frame_change_post.clear()

            scene.frame_current = current_frame
            scene.frame_start = start_frame
            scene.frame_end = end_frame

        return handler

    def store_current_settings(self, scene):
        self.backup_current_frame = scene.frame_current
        self.backup_start_frame = scene.frame_start
        self.backup_end_frame = scene.frame_end

    def restore_settings(self, scene):
        scene.frame_current = self.backup_current_frame
        scene.frame_start = self.backup_start_frame
        scene.frame_end = self.backup_end_frame

    def execute(self, context):
        scene = context.scene
        props: CyberGafferSharedProps = scene.cyber_gaffer_shared_props

        scene = context.scene
        self.store_current_settings(scene)

        scene.frame_start = props.start_frame
        scene.frame_end = props.end_frame
        scene.frame_current = props.start_frame - 1

        bpy.app.handlers.animation_playback_post.clear()
        bpy.app.handlers.frame_change_post.clear()

        bpy.app.handlers.animation_playback_post.append(self.on_animation_playback_post(scene.frame_start, scene.frame_end, scene.frame_current))
        bpy.app.handlers.frame_change_post.append(self.on_frame_changed)

        bpy.ops.screen.animation_play()

        return {'PASS_THROUGH'}
