# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from .shared_props import CyberGafferSharedProps


class CyberGafferCreateTargetOperator(bpy.types.Operator):
    bl_idname = "object.cybergaffer_create_target"
    bl_label = "Create probe target"

    def execute(self, context):
        new_target = bpy.data.objects.new("CyberGaffer_Target", None)
        context.collection.objects.link(new_target)
        new_target.empty_display_type = 'SINGLE_ARROW'

        scene = context.scene

        if hasattr(scene, 'cyber_gaffer_shared_props'):
            scene.cyber_gaffer_shared_props.target_obj = new_target.name

        return {'FINISHED'}
