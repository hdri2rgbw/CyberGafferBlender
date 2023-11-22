# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Panel


class CyberGafferMainPanel(Panel):
    bl_label = "CyberGaffer"
    bl_idname = "OBJECT_PT_cyberGaffer_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        current_renderer = context.scene.render.engine
        if not (current_renderer == 'CYCLES' or current_renderer == 'EEVEE'):
            layout.alert = True
            layout.label(text='Only Cycles and Eevee current supported')

        layout.operator('object.cybergaffer_create_target')
