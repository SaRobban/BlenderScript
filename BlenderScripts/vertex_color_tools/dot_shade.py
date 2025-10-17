#dot_shade.py


import bpy
import bmesh
from mathutils import Vector
from . import config

# Core logic
def vertex_normal_direction_dot(v: bmesh.types.BMVert):
    dir_sum = Vector((0.0, 0.0, 0.0))
    n_dir = 0
    for e in v.link_edges:
        ov = e.other_vert(v)
        edge_vec = ov.co - v.co
        if edge_vec.length > 1e-6:
            dir_sum += edge_vec.normalized()
            n_dir += 1
    if n_dir == 0:
        return None
    avg_dir = dir_sum / n_dir
    if avg_dir.length < 1e-6:
        return None
    avg_dir.normalize()

    norm_sum = Vector((0.0, 0.0, 0.0))
    n_norm = 0
    for f in v.link_faces:
        norm_sum += f.normal
        n_norm += 1
    if n_norm == 0:
        return None
    avg_norm = norm_sum / n_norm
    if avg_norm.length < 1e-6:
        return None
    avg_norm.normalize()

    dot = avg_dir.dot(avg_norm)
    # Normalize dot from [-1, 1] to [0, 1]
    val = (dot + 1) / 2
    return val


def apply_dot_vertex_colors(obj, layer_name="dot_color"):
    if obj.type != 'MESH':
        return

    obj = bpy.context.object
    old_mode = obj.mode

    bpy.ops.object.mode_set(mode='EDIT')
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    bm.verts.ensure_lookup_table()

    # Use POINT domain color layer
    color_layer = bm.verts.layers.color.get(layer_name)
    if color_layer is None:
        color_layer = bm.verts.layers.color.new(layer_name)

    for v in bm.verts:
        val = vertex_normal_direction_dot(v)
        if val is None:
            val = 0.5  # fallback mid-gray

        val = 1.0 - val
        col = (val, val, val, 1.0)
        v[color_layer] = col

    bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
    
  
    print(f"Vertex coloring done with POINT domain layer: {layer_name}")



    if old_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=old_mode)

   # me.color_attributes.active_color = color_layer

# Operator
class DOT_COLOR_OT_dot_color(bpy.types.Operator):
    bl_idname = "object.vertex_dot_color"
    bl_label = "Apply Dot Shade"
    bl_description = "Colors vertices based on dot product of edge direction and face normals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        settings = context.scene.dot_color_settings
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "No mesh object selected.")
            return {'CANCELLED'}

        apply_dot_vertex_colors(obj, settings.color_layer_name)
        return {'FINISHED'}

# UI Panel
class DOT_COLOR_PT_controls(bpy.types.Panel):
    bl_label = "Dot Shade"
    bl_idname = "DOT_COLOR_PT_controls"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.dot_color_settings

        layout.prop(settings, "color_layer_name", icon='RENDERLAYERS')
        layout.operator("object.vertex_dot_color", icon='FORCE_HARMONIC')

# Property Group
class DotColorSettings(bpy.types.PropertyGroup):
    color_layer_name: bpy.props.StringProperty(
        name="Layer",
        default="Dot shade",
        description="Name of the vertex color attribute"
    )

# Registration
classes = (
    DotColorSettings,
    DOT_COLOR_OT_dot_color,
    DOT_COLOR_PT_controls,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dot_color_settings = bpy.props.PointerProperty(type=DotColorSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.dot_color_settings
