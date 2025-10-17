bl_info = {
    "name": "Blend Thumbnail Generator",
    "author": "OpenAI & You",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > ThumbnailGen",
    "description": "Generate thumbnails for .blend files in a folder",
    "category": "Render",
}

import bpy

from . import thumb_creator_core, thumb_creator_panel

classes = (
    thumb_creator_core.ThumbnailGenSettings,
    thumb_creator_core.THUMBGEN_OT_FindFiles,
    thumb_creator_core.THUMBGEN_OT_GenerateThumbs,
    thumb_creator_panel.THUMBGEN_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.thumbgen_settings = bpy.props.PointerProperty(type=thumb_creator_core.ThumbnailGenSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.thumbgen_settings

if __name__ == "__main__":
    register()
