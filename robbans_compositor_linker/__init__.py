bl_info = {
    "name": "Scene Compositor Linker",
    "author": "Robban",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Compositor Linker",
    "description": "Link scenes and compositor node groups from external blend files",
    "category": "Compositing",
}

if "bpy" in locals():
    import importlib
    importlib.reload(compositor_linker_core)
    importlib.reload(compositor_linker_ui)
else:
    from . import compositor_linker_core
    from . import compositor_linker_ui


def register():
    compositor_linker_ui.register()

def unregister():
    compositor_linker_ui.unregister()
