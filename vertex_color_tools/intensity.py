import bpy
from bpy.props import FloatProperty, PointerProperty
from . import config

# Properties
class VERTEX_COLOR_INTENSITY_Props(bpy.types.PropertyGroup):
    intensity: FloatProperty(
        name="Intensity",
        description="Scale color difference from center (0 = flat, 1 = original, >1 = more contrast)",
        default=1.0,
        min=-2.0,
        max=2.0
    )

    center: FloatProperty(
        name="Center",
        description="Gray midpoint for intensity adjustment (usually 0.5)",
        default=0.5,
        min=0.0,
        max=1.0
    )

# Operators
class VERTEX_COLOR_OT_adjust_intensity(bpy.types.Operator):
    bl_idname = "object.adjust_vertex_color_intensity"
    bl_label = "Adjust Vertex Color Intensity"
    bl_description = "Modifies the intensity (contrast) of the active vertex color layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.vc_intensity_props
        intensity = props.intensity
        center = props.center  # <- new

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

        for data in color_layer.data:
            original = data.color
            adjusted = [((c - center) * intensity + center) for c in original[:3]]
            adjusted = [min(1.0, max(0.0, c)) for c in adjusted]  # Clamp
            data.color = (*adjusted, original[3])  # Preserve alpha

        self.report({'INFO'}, f"Adjusted intensity on '{color_layer.name}' with center {center}")
        return {'FINISHED'}


class VERTEX_COLOR_OT_normalize_grayscale(bpy.types.Operator):
    bl_idname = "object.normalize_vertex_color_grayscale"
    bl_label = "Normalize Grayscale Vertex Colors"
    bl_description = "Normalizes grayscale values in active vertex color layer (remaps darkest to black and brightest to white)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object

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

        grayscale_values = [c.color[0] for c in color_layer.data]
        min_val = min(grayscale_values)
        max_val = max(grayscale_values)

        if min_val == max_val:
            self.report({'WARNING'}, "All values are the same. Normalization skipped.")
            return {'CANCELLED'}

        range_val = max_val - min_val

        for c in color_layer.data:
            gray = c.color[0]
            normalized = (gray - min_val) / range_val
            c.color = (normalized, normalized, normalized, 1.0)

        self.report({'INFO'}, f"Normalized vertex colors in '{color_layer.name}'.")
        return {'FINISHED'}

# Panel
class VERTEX_COLOR_PT_intensity_panel(bpy.types.Panel):
    bl_label = "Intensity Modifier"
    bl_idname = "VERTEX_COLOR_PT_intensity_panel"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        props = context.scene.vc_intensity_props
        obj = context.active_object
        color_layer = obj.data.color_attributes.active_color

        col = layout.column()

        if color_layer:
            layout.label(text=f"Adjust Layer: {color_layer.name}")
            col.prop(props, "intensity", slider=True)
            col.prop(props, "center", slider=True)  
            col.operator("object.adjust_vertex_color_intensity", text="Scale From Center", icon='DRIVER_DISTANCE')

            col.separator()
            col.operator("object.normalize_vertex_color_grayscale", text="Normalize Grayscale", icon='MOD_LENGTH')
        else:
            layout.label(text="No active vertex color layer", icon='ERROR')

# Registration
classes = (

    VERTEX_COLOR_INTENSITY_Props,
    VERTEX_COLOR_OT_adjust_intensity,
    VERTEX_COLOR_OT_normalize_grayscale,
    VERTEX_COLOR_PT_intensity_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vc_intensity_props = PointerProperty(type=VERTEX_COLOR_INTENSITY_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vc_intensity_props
