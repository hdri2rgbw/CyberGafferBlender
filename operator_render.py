# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
import bmesh
import math

from . import shared_props
from os import path


class CyberGafferRenderOperator(bpy.types.Operator):
    bl_idname = "render.cybergaffer"
    bl_label = "CyberGaffer Render"

    modal_timer = None
    is_rendering = False
    stop_pressed = False
    frames_to_render = None

    probe = None
    camera = None

    # Saved scene settings
    backup_render_path = None
    backup_current_camera = None
    backup_current_frame = None
    backup_resolution_x = None
    backup_resolution_y = None
    backup_film_transparent = None

    backup_file_format = None
    backup_color_management = None
    backup_color_depth = None
    backup_color_mode = None
    backup_exr_codec = None

    backup_view_transform = None
    backup_look = None

    @staticmethod
    def create_probe_material():
        mat = bpy.data.materials.get('CyberGafferProbeMaterial')
        if mat is None:
            mat = bpy.data.materials.new(name='CyberGafferProbeMaterial')

        mat = bpy.data.materials.get('CyberGafferProbeMaterial')
        if mat is None:
            mat = bpy.data.materials.new(name='CyberGafferProbeMaterial')

        # Cleanup material
        mat.use_nodes = True
        mat_nodes = mat.node_tree.nodes
        for node in mat_nodes:
            mat_nodes.remove(node)

        output_node = mat_nodes.new(type="ShaderNodeOutputMaterial")
        output_node.location = (0, 0)

        shader_node = mat_nodes.new(type="ShaderNodeBsdfDiffuse")
        shader_node.inputs['Color'].default_value = (1, 1, 1, 1)
        shader_node.inputs['Roughness'].default_value = 0.0
        shader_node.location = (-200, 0)

        mat.node_tree.links.new(output_node.inputs['Surface'], shader_node.outputs['BSDF'])

        return mat

    @staticmethod
    def create_sphere(collection, radius: float):
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('CyberGaffer_Probe')
        sphere = bpy.data.objects.new("CyberGaffer_Probe", mesh)

        # Add the object into the scene.
        collection.objects.link(sphere)

        # Select the newly created object
        bpy.context.view_layer.objects.active = sphere
        sphere.select_set(True)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=64, radius=radius)
        bm.to_mesh(mesh)
        bm.free()

        # bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.shade_smooth()

        sphere.select_set(False)
        sphere.hide_select = True

        return sphere

    @staticmethod
    def create_camera(collection, offset):
        camera_data = bpy.data.cameras.new('CyberGaffer_Camera')
        camera_object = bpy.data.objects.new('CyberGaffer_Camera', camera_data)
        collection.objects.link(camera_object)

        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = 0.1
        camera_data.clip_start = 0.1
        camera_data.clip_end = 0.2
        camera_data.display_size = camera_data.clip_end
        camera_data.show_limits = True

        camera_object.location = [0, 0, offset]
        camera_object.rotation_euler = [math.radians(180), 0, 0]

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
        if not (current_renderer == 'CYCLES' or current_renderer == 'BLENDER_EEVEE'):
            return False

        return True

    def save_scene_settings(self, scene):
        # backup_start_frame = scene.frame_start
        # backup_end_frame = scene.frame_end

        self.backup_render_path = scene.render.filepath
        self.backup_current_camera = scene.camera
        self.backup_current_frame = scene.frame_current
        self.backup_resolution_x = scene.render.resolution_x
        self.backup_resolution_y = scene.render.resolution_y
        self.backup_film_transparent = scene.render.film_transparent

        image_settings = scene.render.image_settings
        self.backup_file_format = image_settings.file_format
        self.backup_color_management = image_settings.color_management
        self.backup_color_depth = image_settings.color_depth
        self.backup_color_mode = image_settings.color_mode
        self.backup_exr_codec = image_settings.exr_codec

        view_settings = scene.view_settings
        self.backup_view_transform = view_settings.view_transform
        self.backup_look = view_settings.look

    def apply_cyber_gaffer_scene_settings(self, scene, cg_camera, img_size):
        scene.render.film_transparent = True

        image_settings = scene.render.image_settings
        image_settings.file_format = 'OPEN_EXR'
        image_settings.color_management = 'OVERRIDE'
        image_settings.color_depth = '16'
        image_settings.color_mode = 'RGBA'
        image_settings.exr_codec = 'NONE'

        view_settings = scene.view_settings
        view_settings.view_transform = 'Raw'
        view_settings.look = 'None'

        scene.camera = cg_camera
        scene.render.resolution_x = scene.render.resolution_y = img_size

    def restore_scene_settings(self, scene):
        scene.render.film_transparent = self.backup_film_transparent

        view_settings = scene.view_settings
        view_settings.look = self.backup_look
        view_settings.view_transform = self.backup_view_transform

        image_settings = scene.render.image_settings
        image_settings.exr_codec = self.backup_exr_codec
        image_settings.file_format = self.backup_file_format
        image_settings.color_mode = self.backup_color_mode
        image_settings.color_depth = self.backup_color_depth
        image_settings.color_management = self.backup_color_management

        scene.render.filepath = self.backup_render_path
        scene.frame_current = self.backup_current_frame
        scene.render.resolution_x = self.backup_resolution_x
        scene.render.resolution_y = self.backup_resolution_y

    def prerender(self, scene, context=None):
        self.is_rendering = True

    def postrender(self, scene, context=None):
        self.frames_to_render.pop(0)
        self.is_rendering = False

    def cancelled(self, scene, context=None):
        self.stop_pressed = True

    def execute(self, context):
        props: shared_props.CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props
        scene = context.scene

        target = bpy.data.objects[props.target_obj]
        # TODO: should we link probe and camera to the ALL collections?
        target_collection = target.users_collection[0]

        radius = 0.05
        camera_offset = -radius * 3

        # Init render objects
        self.probe = self.create_sphere(target_collection, radius)
        self.camera = self.create_camera(target_collection, camera_offset)
        self.camera.parent = self.probe
        self.probe.parent = target

        mat = self.create_probe_material()

        if self.probe.data.materials:
            self.probe.data.materials.clear()

        self.probe.data.materials.append(mat)

        self.save_scene_settings(scene)
        self.apply_cyber_gaffer_scene_settings(scene, self.camera, props.img_size)

        self.frames_to_render = list(range(props.start_frame, props.end_frame + 1))

        self.is_rendering = False
        self.stop_pressed = False

        bpy.app.handlers.render_pre.append(self.prerender)
        bpy.app.handlers.render_post.append(self.postrender)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self.modal_timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            scene = context.scene

            if True in (not self.frames_to_render, self.stop_pressed is True):
                bpy.app.handlers.render_pre.remove(self.prerender)
                bpy.app.handlers.render_post.remove(self.postrender)
                bpy.app.handlers.render_cancel.remove(self.cancelled)

                context.window_manager.event_timer_remove(self.modal_timer)

                # Cleanup
                scene.camera = self.backup_current_camera
                self.delete_objects([self.probe, self.camera])

                self.restore_scene_settings(scene)

                self.probe = None
                self.camera = None

                context.area.header_text_set(None)

                return {'FINISHED'}
            elif self.is_rendering is False:
                props: shared_props.CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props

                frame = self.frames_to_render[0]

                iteration = (frame - props.start_frame) / (props.end_frame - props.start_frame) * 100.0
                context.area.header_text_set(f'Rendering probes... {iteration}%')

                scene.frame_current = frame
                scene.render.filepath = path.join(props.output_folder, f'{props.target_obj}_{frame}.exr')
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

        return {'PASS_THROUGH'}
