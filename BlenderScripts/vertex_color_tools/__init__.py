#__init.py__

bl_info = {
    "name": "Vertex Tools",
    "author": "SaRobban & OpenAI",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > VCT tab",
    "description": "Combine and paint vertex colors",
    "category": "Mesh",
}

import bpy
from . import config
from . import main_menu
#from . import color_picker
from . import vertex_color_preview
from . import set_color_to_selection
from . import bake_ao
from . import directional_shade
from . import dot_shade
from . import density_weighted
from . import blur 
from . import intensity
from . import combine_layers
from . import lerp_colors_by_layer

# Register all modules
def register():
    main_menu.register()
    vertex_color_preview.register()
    set_color_to_selection.register()
    bake_ao.register()
    directional_shade.register()
    dot_shade.register()
    density_weighted.register()
    blur.register()
    intensity.register()
    combine_layers.register()
    lerp_colors_by_layer.register()

def unregister():
    main_menu.unregister()
    vertex_color_preview.unregister()
    set_color_to_selection.unregister()
    bake_ao.unregister()
    directional_shade.unregister()
    dot_shade.unregister()
    density_weighted.unregister()
    blur.unregister()
    intensity.unregister()
    combine_layers.unregister()
    lerp_colors_by_layer.unregister()

if __name__ == "__main__":
    register()
