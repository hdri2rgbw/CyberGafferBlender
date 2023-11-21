# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import bmesh
import math

from . import shared_props


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
        basic_sphere.hide_render = True

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

        if props.target_obj is None or props.target_obj == "NONE":
            # print(f'CyberGafferOperatorRender.poll: Target object is None')
            return False

        return True

    def execute(self, context):
        props: shared_props.CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props

        target = bpy.data.objects[props.target_obj]
        # TODO: should we link probe and camera to the ALL collections?
        target_collection = target.users_collection[0]

        # Init render objects
        probe = self.create_sphere(target_collection)
        camera = self.create_camera(target_collection)
        camera.parent = probe
        probe.parent = target

        # TODO: render sequence

        # Cleanup
        self.delete_objects([probe, camera])

        return {'FINISHED'}
