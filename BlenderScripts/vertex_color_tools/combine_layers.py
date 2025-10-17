# combine_layers.py
import bpy
import numpy as np
from bpy.props import EnumProperty, StringProperty, PointerProperty
from . import config

# Operator
class COMBINE_LAYER_OT(bpy.types.Operator):
    bl_idname = "mesh.combine_color_attributes"
    bl_label = "Combine Color Layer"
    bl_description = "Combines two vertex color layers using the selected blend mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        mesh = obj.data
        props = context.scene.vertex_color_combiner

        color_a_name = props.color_a
        color_b_name = props.color_b
        result_name = props.result_name.strip()
        blend_mode = props.blend_mode

        if not result_name:
            self.report({'ERROR'}, "Result name cannot be empty")
            return {'CANCELLED'}

        try:
            color_a = mesh.color_attributes[color_a_name]
            color_b = mesh.color_attributes[color_b_name]
        except KeyError:
            self.report({'ERROR'}, "One or both color attributes not found")
            return {'CANCELLED'}

        if color_a.domain != color_b.domain:
            self.report({'ERROR'}, "Color attribute domains do not match")
            return {'CANCELLED'}

        if result_name not in mesh.color_attributes:
            mesh.color_attributes.new(name=result_name, type='BYTE_COLOR', domain=color_a.domain)

        color_result = mesh.color_attributes[result_name]

        data_a = np.array([c.color for c in color_a.data])
        data_b = np.array([c.color for c in color_b.data])

        # Blend mode logic
        if blend_mode == 'MAX':
            result = np.maximum(data_a, data_b)
        elif blend_mode == 'MIN':
            result = np.minimum(data_a, data_b)
        elif blend_mode == 'ADD':
            result = np.clip(data_a + data_b, 0, 1)
        elif blend_mode == 'MULTIPLY':
            result = data_a * data_b
        elif blend_mode == 'AVERAGE':
            result = (data_a + data_b) * 0.5
        elif blend_mode == 'OVERLAY':
            result = np.where(data_a <= 0.5,
                              2 * data_a * data_b,
                              1 - 2 * (1 - data_a) * (1 - data_b))
            result = np.clip(result, 0, 1)
        else:
            self.report({'ERROR'}, f"Unsupported blend mode: {blend_mode}")
            return {'CANCELLED'}

        for i, c in enumerate(result):
            color_result.data[i].color = c.tolist()

        self.report({'INFO'}, f"Combined using {blend_mode} mode into '{result_name}'")
        return {'FINISHED'}

# Panel
class COMBINE_LAYER_PT(bpy.types.Panel):
    bl_label = "Layer Combiner"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_idname = "VERTEXTOOLS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        props = context.scene.vertex_color_combiner
        obj = context.object
        mesh = obj.data if obj and obj.type == 'MESH' else None

        layout.label(text="Select Layers:")

        if mesh:
            layout.prop_search(props, "color_a", mesh, "color_attributes", text="Layer A")
            layout.prop_search(props, "color_b", mesh, "color_attributes", text="Layer B")
        else:
            layout.label(text="No mesh selected", icon='ERROR')

        layout.prop(props, "result_name")
        layout.prop(props, "blend_mode", text="Blend Mode")
        layout.operator("mesh.combine_color_attributes", text="Combine Layers", icon="EXPERIMENTAL")

# Properties
class CombineLayerProps(bpy.types.PropertyGroup):
    color_a: StringProperty(name="Layer A")
    color_b: StringProperty(name="Layer B")
    result_name: StringProperty(name="Result Layer", default="ColorCombined")

    blend_mode: EnumProperty(
        name="Blend Mode",
        description="How to combine the vertex color layers",
        items=[
            ('MAX', "Max", "Use the maximum value per channel"),
            ('MIN', "Min", "Use the minimum value per channel"),
            ('ADD', "Add", "Add the values and clamp to 1.0"),
            ('MULTIPLY', "Multiply", "Multiply values per channel"),
            ('AVERAGE', "Average", "Average the two layers"),
            ('OVERLAY', "Overlay", "Overlay blend like Photoshop"),
        ],
        default='MAX'
    )



# Register/unregister
classes = [
    COMBINE_LAYER_OT,
    COMBINE_LAYER_PT,
    CombineLayerProps,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_color_combiner = bpy.props.PointerProperty(type=CombineLayerProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_color_combiner
