bl_info = {
    "name": "UV Tools: Project & Snap",
    "author": "User / ChatGPT",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > UV Tools",
    "description": "Planar UV projection per face, snapping and basic UV transforms for sprite-sheet workflows.",
    "category": "UV",
}

import importlib

from . import uv_project_operator
from . import uv_snap_to_tile
from . import uv_transform_ops
from . import uv_project_panel

modules = (
    uv_project_operator,
    uv_snap_to_tile,
    uv_transform_ops,
    uv_project_panel,
)

def register():
    for m in modules:
        importlib.reload(m)
        if hasattr(m, "register"):
            m.register()

def unregister():
    for m in reversed(modules):
        if hasattr(m, "unregister"):
            m.unregister()

if __name__ == "__main__":
    register()
