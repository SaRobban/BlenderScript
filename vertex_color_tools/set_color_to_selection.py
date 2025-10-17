# set_color_to_selection.py
import bpy
import bmesh
from bpy.props import FloatVectorProperty, StringProperty
from . import config

# Utility
def get_or_create_float_color_layer(mesh, name):
    # Must be called in OBJECT mode
    if name not in mesh.color_attributes:
        return mesh.color_attributes.new(name=name, type='FLOAT_COLOR', domain='POINT')
    layer = mesh.color_attributes[name]
    if layer.data_type != 'FLOAT_COLOR' or layer.domain != 'POINT':
        raise TypeError(f"Layer '{name}' exists but is not FLOAT_COLOR with POINT domain.")
    return layer

# Operators
class SET_VERTEX_COLOR_OT(bpy.types.Operator):
    bl_idname = "vertexcolor.apply_color"
    bl_label = "Apply Vertex Color"
    bl_description = "Apply the selected color to selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        color = context.scene.vertex_color_painter_color
        layer_name = context.scene.vertex_color_painter_layer_name

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh.")
            return {'CANCELLED'}
        if obj.mode != 'EDIT':
            self.report({'WARNING'}, "Operator must be run in Edit Mode.")
            return {'CANCELLED'}

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.verts.ensure_lookup_table()
        selected_indices = [v.index for v in bm.verts if v.select]

        if not selected_indices:
            self.report({'WARNING'}, "No vertices selected.")
            return {'CANCELLED'}

        # Switch to OBJECT mode for safe access
        bpy.ops.object.mode_set(mode='OBJECT')

        try:
            layer = get_or_create_float_color_layer(mesh, layer_name)
        except TypeError as e:
            self.report({'ERROR'}, str(e))
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        if len(layer.data) != len(mesh.vertices):
            self.report({'ERROR'}, f"Color layer has {len(layer.data)} entries, but mesh has {len(mesh.vertices)} vertices.")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        for i in selected_indices:
            layer.data[i].color = (*color, 1.0)

        mesh.color_attributes.active_color = layer

        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"Applied color to {len(selected_indices)} vertices in layer '{layer_name}'.")
        return {'FINISHED'}

class FILL_VERTEX_COLOR_OT(bpy.types.Operator):
    bl_idname = "vertexcolor.fill_model"
    bl_label = "Fill Model with Vertex Color"
    bl_description = "Fill the entire model with the selected vertex color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        color = context.scene.vertex_color_painter_color
        layer_name = context.scene.vertex_color_painter_layer_name

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Must be a mesh object.")
            return {'CANCELLED'}

        was_in_edit = obj.mode == 'EDIT'
        if was_in_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data

        try:
            layer = get_or_create_float_color_layer(mesh, layer_name)
        except TypeError as e:
            self.report({'ERROR'}, str(e))
            if was_in_edit:
                bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}

        for data in layer.data:
            data.color = (*color, 1.0)

        mesh.color_attributes.active_color = layer

        if was_in_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"Model filled with color in layer '{layer_name}'.")
        return {'FINISHED'}

# Panel
class SET_VERTEX_COLOR_PT(bpy.types.Panel):
    bl_label = "Set Color"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_idname = "VERTEXCOLOR_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "vertex_color_painter_color", text="Color")
        layout.prop(scene, "vertex_color_painter_layer_name", text="Layer")

        col = layout.column(align=True)
        col.operator("vertexcolor.apply_color", text="Apply to Selected", icon='POINTCLOUD_POINT')

        layout.separator()
        layout.operator("vertexcolor.fill_model", text="Fill Entire Model", icon='SNAP_VOLUME')

# Registration
classes = [
    SET_VERTEX_COLOR_OT,
    FILL_VERTEX_COLOR_OT,
    SET_VERTEX_COLOR_PT,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_color_painter_color = FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    bpy.types.Scene.vertex_color_painter_layer_name = StringProperty(
        name="Layer Name",
        description="Name of the vertex color layer to use",
        default="Color"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_color_painter_color
    del bpy.types.Scene.vertex_color_painter_layer_name

