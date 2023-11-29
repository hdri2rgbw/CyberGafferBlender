# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from bpy.types import Panel

from .shared_props import CyberGafferSharedProps

class CyberGafferPlayPanel(Panel):
    bl_label = "Play"
    bl_idname = "OBJECT_PT_cyberGaffer_play"
    bl_parent_id = "OBJECT_PT_cyberGaffer_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props: CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props

        layout.prop(props, 'play_delay')
        layout.prop(props, 'play_start_sequence')

        layout.prop(props, 'server_address')
        layout.prop(props, 'server_port')

        layout.operator("cybergaffer.play")
