# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Panel

from .shared_props import CyberGafferSharedProps
from .operator_render import CyberGafferRenderOperator
from .panel_main import CyberGafferMainPanel

class CyberGafferRenderPanel(Panel):
    bl_label = "Prerender"
    bl_idname = "OBJECT_PT_cyberGaffer_prerender"
    bl_parent_id = "OBJECT_PT_cyberGaffer_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cyber_gaffer_shared_props

        layout.prop(props, 'img_size')
        layout.prop(props, 'output_folder')
        layout.prop(props, 'target_obj')

        layout.label(text=" Frame range:")
        row = layout.row()
        row.prop(props, 'start_frame')
        row.prop(props, 'end_frame')

        layout.operator('render.cybergaffer')
