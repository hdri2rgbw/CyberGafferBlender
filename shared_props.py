# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


def item_callback(self, context):
    empties = []
    empties.append(("NONE", "None", "", 0))

    objs = ([o for o in bpy.context.scene.objects])
    counter = 1

    for obj in objs:
        if obj.type == 'EMPTY':
            empties.append((obj.name, obj.name, "", counter))
            counter = counter + 1

    return empties


class CyberGafferSharedProps(bpy.types.PropertyGroup):
    img_size: bpy.props.IntProperty(name="Image Size", description="Size of task images, that will be send to CyberGaffer. Recommended size is (256, 256)", default=256)
    output_folder: bpy.props.StringProperty(name="Output Folder", description="", default="", maxlen=1024, subtype='DIR_PATH')
    target_obj: bpy.props.EnumProperty(name="Target", items=item_callback)
    # TODO: check values for improper ranges
    start_frame: bpy.props.IntProperty(name="Start Frame", default=bpy.context.scene.frame_start)
    end_frame: bpy.props.IntProperty(name="End Frame", default=bpy.context.scene.frame_end)
