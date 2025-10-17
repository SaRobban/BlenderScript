import bpy
from . import config 

# Panel
class VIEW3D_PT_vertex_color_preview(bpy.types.Panel):
    bl_label = "Vertex Color Preview Layer"
    bl_idname = "VIEW3D_PT_vertex_color_preview"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "vcol_layer_selector", text="Layer")

        obj = context.active_object
        color_layer = obj.data.color_attributes.active_color

        if color_layer:
            layout.label(text=f"Active Layer: {color_layer.name}")
        else:
            layout.label(text="No active vertex color layer", icon='ERROR')


# Dynamic dropdown items from active object's vertex color layers
def update_vcol_enum(self, context):
    obj = context.active_object
    if obj and obj.type == 'MESH':
        return [(layer.name, layer.name, "") for layer in obj.data.color_attributes]
    return []


# Callback on selection changes
def on_vcol_layer_changed(self, context):
    obj = context.active_object
    selected_layer_name = context.scene.vcol_layer_selector

    if not obj or obj.type != 'MESH':
        return

    if selected_layer_name in obj.data.color_attributes:
        obj.data.color_attributes.active_color = obj.data.color_attributes[selected_layer_name]

        # Force viewport to use vertex color shading
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'VERTEX'
                        break


# Register and unregister functions
def register():
    bpy.utils.register_class(VIEW3D_PT_vertex_color_preview)

    bpy.types.Scene.vcol_layer_selector = bpy.props.EnumProperty(
        name="Vertex Color Layers",
        description="Select vertex color layer",
        items=update_vcol_enum,
        update=on_vcol_layer_changed
    )


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_vertex_color_preview)
    del bpy.types.Scene.vcol_layer_selector


if __name__ == "__main__":
    register()
