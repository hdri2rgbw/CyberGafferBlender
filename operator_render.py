# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import bmesh
import math

from . import shared_props
from os import path

class CyberGafferRenderOperator(bpy.types.Operator):
    bl_idname = "render.cybergaffer"
    bl_label = "CyberGaffer Render"

    @staticmethod
    def create_sphere(collection):
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('CyberGaffer_Probe')
        basic_sphere = bpy.data.objects.new("CyberGaffer_Probe", mesh)

        # Add the object into the scene.
        collection.objects.link(basic_sphere)

        # Select the newly created object
        bpy.context.view_layer.objects.active = basic_sphere
        basic_sphere.select_set(True)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=64, radius=0.05)
        bm.to_mesh(mesh)
        bm.free()

        # bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.shade_smooth()

        basic_sphere.select_set(False)

        return basic_sphere

    @staticmethod
    def create_camera(collection):
        camera_data = bpy.data.cameras.new('CyberGaffer_Camera')
        camera_object = bpy.data.objects.new('CyberGaffer_Camera', camera_data)
        collection.objects.link(camera_object)

        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = 0.1
        camera_data.clip_start = 0.1
        camera_data.clip_end = 0.2
        camera_data.display_size = camera_data.clip_end
        camera_data.show_limits = True

        camera_object.location = [0, -0.15, 0]
        camera_object.rotation_euler = [math.radians(90), 0, 0]

        camera_object.hide_select = True

        return camera_object

    @staticmethod
    def delete_objects(objs_to_remove):
        objs = bpy.data.objects
        for o in objs_to_remove:
            objs.remove(o, do_unlink=True)

    @classmethod
    def poll(cls, context):
        props: shared_props.CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props

        if props is None:
            print(f'CyberGafferOperatorRender.poll: No CyberGafferSharedProps')
            return False

        if props.target_obj is None or props.target_obj == "NONE" or props.target_obj == "":
            # print(f'CyberGafferOperatorRender.poll: Target object is None')
            return False

        current_renderer = context.scene.render.engine
        if not(current_renderer == 'CYCLES' or current_renderer == 'EEVEE'):
            return False

        return True

    def execute(self, context):
        props: shared_props.CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props
        scene = context.scene

        target = bpy.data.objects[props.target_obj]
        # TODO: should we link probe and camera to the ALL collections?
        target_collection = target.users_collection[0]

        # Init render objects
        probe = self.create_sphere(target_collection)
        camera = self.create_camera(target_collection)
        camera.parent = probe
        probe.parent = target

        # Save current settings
        backup_render_path = scene.render.filepath
        backup_current_camera = scene.camera
        backup_current_frame = scene.frame_current
        backup_resolution_x = scene.render.resolution_x
        backup_resolution_y = scene.render.resolution_y
        backup_film_transparent = scene.render.film_transparent

        image_settings = scene.render.image_settings
        backup_file_format = image_settings.file_format
        backup_color_management = image_settings.color_management
        backup_color_depth = image_settings.color_depth
        backup_color_mode = image_settings.color_mode
        backup_exr_codec = image_settings.exr_codec

        view_settings = scene.view_settings
        backup_view_transform = view_settings.view_transform
        backup_look = view_settings.look

        # Apply settings for CyberGaffer
        scene.render.film_transparent = True

        image_settings.file_format = 'OPEN_EXR'
        image_settings.color_management = 'OVERRIDE'
        image_settings.color_depth = '16'
        image_settings.color_mode = 'RGBA'
        image_settings.exr_codec = 'NONE'

        view_settings.view_transform = 'Raw'
        view_settings.look = 'None'

        scene.camera = camera
        scene.render.resolution_x = scene.render.resolution_y = props.img_size
        for frame in range(props.start_frame, props.end_frame + 1):
            scene.frame_current = frame
            scene.render.filepath = path.join(props.output_folder, f'{target.name}_{frame}.exr')
            bpy.ops.render.render(write_still=True)

        # Cleanup
        scene.camera = backup_current_camera
        self.delete_objects([probe, camera])

        # Restore settings
        scene.render.film_transparent = backup_film_transparent

        view_settings.look = backup_look
        view_settings.view_transform = backup_view_transform

        image_settings.exr_codec = backup_exr_codec
        image_settings.file_format = backup_file_format
        image_settings.color_mode = backup_color_mode
        image_settings.color_depth = backup_color_depth
        image_settings.color_management = backup_color_management

        scene.render.filepath = backup_render_path
        scene.frame_current = backup_current_frame
        scene.render.resolution_x = backup_resolution_x
        scene.render.resolution_y = backup_resolution_y

        return {'FINISHED'}
