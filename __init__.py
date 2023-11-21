# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "CyberGaffer",
    "author": "Antilatency",
    "description": "",
    "blender": (3, 0, 0),
    "location": "",
    "warning": "",
    "category": "Generic"
}

if "bpy" in locals():
    import importlib
    importlib.reload(shared_props)
    importlib.reload(operator_render)
    importlib.reload(panel_main)
    importlib.reload(panel_render)
else:
    from . import shared_props
    from . import operator_render
    from . import panel_main
    from . import panel_render

import bpy
from bpy.props import (
    PointerProperty
)


def register():
    bpy.utils.register_class(shared_props.CyberGafferSharedProps)
    bpy.types.Scene.cyber_gaffer_shared_props = PointerProperty(type=shared_props.CyberGafferSharedProps)

    bpy.utils.register_class(operator_render.CyberGafferRenderOperator)

    bpy.utils.register_class(panel_main.CyberGafferMainPanel)
    bpy.utils.register_class(panel_render.CyberGafferRenderPanel)

def unregister():
    del bpy.types.Scene.cyber_gaffer_shared_props
    bpy.utils.unregister_class(shared_props.CyberGafferSharedProps)

    bpy.utils.unregister_class(operator_render.CyberGafferRenderOperator)

    bpy.utils.unregister_class(panel_main.CyberGafferMainPanel)
    bpy.utils.unregister_class(panel_render.CyberGafferRenderPanel)

