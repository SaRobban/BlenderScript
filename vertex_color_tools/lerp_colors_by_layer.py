# lerp_colors_by_layer.py
import bpy
from bpy.props import FloatVectorProperty, PointerProperty
from . import config

# Property Group for Colors A and B
class VERTEX_COLOR_LERP_Props(bpy.types.PropertyGroup):
    color_a: FloatVectorProperty(
        name="Color A",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        description="Start color for lerp"
    )

    color_b: FloatVectorProperty(
        name="Color B",
        subtype='COLOR',
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        description="End color for lerp"
    )


# Operator
class VERTEX_COLOR_OT_lerp_colors_by_red(bpy.types.Operator):
    bl_idname = "object.lerp_vertex_colors_by_red"
    bl_label = "Lerp Between Colors by Red"
    bl_description = "Interpolates between Color A and B using red channel of active vertex color layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.vertex_color_lerp_props

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object.")
            return {'CANCELLED'}

        mesh = obj.data
        color_layer = mesh.color_attributes.active_color

        if not color_layer:
            self.report({'ERROR'}, "No active vertex color layer found.")
            return {'CANCELLED'}

        if color_layer.domain not in {'POINT', 'CORNER'}:
            self.report({'ERROR'}, f"Unsupported color domain: {color_layer.domain}")
            return {'CANCELLED'}

        col_a = props.color_a
        col_b = props.color_b

        for data in color_layer.data:
            red = data.color[0]
            lerped = [
                (1 - red) * a + red * b
                for a, b in zip(col_a, col_b)
            ]
            data.color = (*lerped, 1.0)  # Preserve alpha as 1.0

        self.report({'INFO'}, "Lerped vertex colors using red channel.")
        return {'FINISHED'}


# Panel
class VERTEX_COLOR_PT_lerp_panel(bpy.types.Panel):
    bl_label = "Lerp Color by R"
    bl_idname = "VERTEX_COLOR_PT_lerp_panel"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.vertex_color_lerp_props

        layout.label(text="Lerp Colors by Red Channel:")
        layout.prop(props, "color_a")
        layout.prop(props, "color_b")
        layout.operator("object.lerp_vertex_colors_by_red", icon='IPO_BEZIER')


# ----------------------------------------------------
# Register / Unregister
# ----------------------------------------------------
classes = (
    VERTEX_COLOR_LERP_Props,
    VERTEX_COLOR_OT_lerp_colors_by_red,
    VERTEX_COLOR_PT_lerp_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_color_lerp_props = PointerProperty(type=VERTEX_COLOR_LERP_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_color_lerp_props