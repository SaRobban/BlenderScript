# directional_shade.py
import bpy
from bpy.props import StringProperty, FloatVectorProperty, BoolProperty, PointerProperty
from mathutils import Vector
from . import config

# Properties
class DirectionalShadeProperties(bpy.types.PropertyGroup):
    result_name: StringProperty(
        name="Layer",
        description="Name of the vertex color attribute",
        default="Directional"
    )
    shade_direction: FloatVectorProperty(
        name="Direction Vector",
        description="Direction to shade against",
        default=(0.0, 0.0, 1.0),
        subtype='DIRECTION',
        size=3
    )
    use_world_space: BoolProperty(
        name="Use World Space",
        description="Interpret the direction in world space",
        default=True
    )

# Operators
class DIRECTIONAL_SHADE_OT_apply(bpy.types.Operator):
    bl_idname = "directional_shade.apply"
    bl_label = "Apply Directional Shade"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object

        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        props = context.scene.directional_shade_props
        result_name = props.result_name.strip()

        if not result_name:
            self.report({'ERROR'}, "Result name cannot be empty")
            return {'CANCELLED'}

        # Create new vertex color attribute if it doesn't exist (POINT domain)
        if result_name not in mesh.color_attributes:
            mesh.color_attributes.new(name=result_name, type='BYTE_COLOR', domain='POINT')
        color_layer = mesh.color_attributes[result_name]

        # Compute average normals per vertex
        vertex_normals = [Vector((0, 0, 0)) for _ in mesh.vertices]
        counts = [0] * len(mesh.vertices)

        for loop in mesh.loops:
            idx = loop.vertex_index
            vertex_normals[idx] += loop.normal
            counts[idx] += 1

        for i, count in enumerate(counts):
            if count > 0:
                vertex_normals[i] /= count
                vertex_normals[i].normalize()

        # Use user-defined direction
        shade_dir = Vector(props.shade_direction)
        if shade_dir.length == 0:
            self.report({'ERROR'}, "Direction vector cannot be zero")
            return {'CANCELLED'}

        if props.use_world_space:
            shade_dir = obj.matrix_world.to_3x3() @ shade_dir
        shade_dir.normalize()

        # Assign one color per vertex (POINT domain)
        for i, normal in enumerate(vertex_normals):
            dot = normal.dot(shade_dir)
            shade = max(0.0, min((dot + 1.0) / 2.0, 1.0))  # Map [-1,1] → [0,1]
            color_layer.data[i].color = (shade, shade, shade, 1.0)

        mesh.color_attributes.active_color = color_layer
        self.report({'INFO'}, f"Directional shade written to POINT attribute '{result_name}'")
        return {'FINISHED'}

class DIRECTIONAL_SHADE_OT_reset_vector(bpy.types.Operator):
    bl_idname = "directional_shade.reset_vector"
    bl_label = "Reset to Up Vector"
    bl_description = "Reset the direction vector to (0, 0, 1)"

    def execute(self, context):
        context.scene.directional_shade_props.shade_direction = (0.0, 0.0, 1.0)
        self.report({'INFO'}, "Direction reset to world up (0, 0, 1)")
        return {'FINISHED'}

# Panel
class DIRECTIONAL_SHADE_PT_controls(bpy.types.Panel):
    bl_label = "Directional Shade"
    bl_idname = "DIRECTIONAL_SHADE_PT_controls"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.directional_shade_props

        layout.prop(props, "result_name", icon='RENDERLAYERS')
        row = layout.row(align=True)
        row.prop(props, "shade_direction")
        row.operator("directional_shade.reset_vector", text="", icon='FILE_REFRESH')

        layout.prop(props, "use_world_space")
        layout.operator("directional_shade.apply", icon='EVENT_DOWN_ARROW')

# Registration
classes = (
    DirectionalShadeProperties,
    DIRECTIONAL_SHADE_PT_controls,
    DIRECTIONAL_SHADE_OT_apply,
    DIRECTIONAL_SHADE_OT_reset_vector,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.directional_shade_props = PointerProperty(type=DirectionalShadeProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.directional_shade_props
