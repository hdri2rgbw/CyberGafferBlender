# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


def item_callback(self, context):
    empties = [("NONE", "None", "", 0)]

    objs = ([o for o in bpy.context.scene.objects])
    counter = 1

    for obj in objs:
        if obj.type == 'EMPTY':
            empties.append((obj.name, obj.name, "", counter))
            counter = counter + 1

    return empties


def on_frame_range_changed(self, context, what):
    props: CyberGafferSharedProps = context.scene.cyber_gaffer_shared_props
    current_start = props.start_frame
    current_end = props.end_frame

    if current_start < 0:
        props.start_frame = 0

    if current_end < 0:
        props.end_frame = 0

    if what == 'start':
        if current_start > current_end:
            props.end_frame = current_start
    elif what == 'end':
        if current_end < current_start:
            props.start_frame = current_end


class CyberGafferSharedProps(bpy.types.PropertyGroup):
    img_size: bpy.props.IntProperty(name="Image Size", description="Size of task images, that will be send to CyberGaffer. Recommended size is (256, 256)", default=256)
    output_folder: bpy.props.StringProperty(name="Output Folder", description="", default="", maxlen=1024, subtype='DIR_PATH')
    target_obj: bpy.props.EnumProperty(name="Target", items=item_callback)
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1, update=lambda self, context: on_frame_range_changed(self, context, 'start'))
    end_frame: bpy.props.IntProperty(name="End Frame", default=250, update=lambda self, context: on_frame_range_changed(self, context, 'end'))
