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
        self.layout.label(text="CyberGaffer by Antilatency")
