# bake_ao.py
import bpy
from . import config



# Property Group
class AOBakeSettings(bpy.types.PropertyGroup):
    layer_name: bpy.props.StringProperty(
        name="AO Layer Name",
        default="AO",
        description="Name of the vertex color layer to bake AO into"
    )


# Operator
class AO_BAKE_OT_vertex_color(bpy.types.Operator):
    bl_idname = "object.ao_bake_vertex_color"
    bl_label = "Bake AO to Vertex Colors"
    bl_description = "Bake ambient occlusion to vertex colors and restore settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        layer_name = context.scene.ao_bake_settings.layer_name

        # Save current render engine & bake settings
        scene = context.scene
        render = scene.render
        cycles = scene.cycles
        bake = render.bake

        old_render_engine = render.engine
        old_bake_type = cycles.bake_type
        old_use_pass_direct = bake.use_pass_direct
        old_use_pass_indirect = bake.use_pass_indirect
        old_target = bake.target
        old_use_clear = bake.use_clear
        old_use_selected_to_active = bake.use_selected_to_active
        old_margin = bake.margin

        try:
            # Ensure object is selected and active
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Ensure in Object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Create vertex color layer if it doesn't exist
            if layer_name not in obj.data.color_attributes:
                obj.data.color_attributes.new(name=layer_name, type='FLOAT_COLOR', domain='POINT')

            # Set the layer as active
            obj.data.color_attributes.active_color = obj.data.color_attributes[layer_name]

            # Set Cycles render engine
            render.engine = 'CYCLES'

            # Bake settings
            cycles.bake_type = 'AO'
            bake.use_pass_direct = False
            bake.use_pass_indirect = False
            bake.target = 'VERTEX_COLORS'
            bake.use_clear = True
            bake.use_selected_to_active = False
            bake.margin = 1

            # Run bake
            bpy.ops.object.bake(type='AO')

            self.report({'INFO'}, f"AO bake completed to layer '{layer_name}'.")

        except Exception as e:
            self.report({'ERROR'}, f"Bake failed: {e}")
            return {'CANCELLED'}

        finally:
            # Restore settings
            render.engine = old_render_engine
            cycles.bake_type = old_bake_type
            bake.use_pass_direct = old_use_pass_direct
            bake.use_pass_indirect = old_use_pass_indirect
            bake.target = old_target
            bake.use_clear = old_use_clear
            bake.use_selected_to_active = old_use_selected_to_active
            bake.margin = old_margin

        return {'FINISHED'}


# Panel
class AO_BAKE_PT_panel(bpy.types.Panel):
    bl_label = "Bake AO"
    bl_idname = "AO_BAKE_PT_panel"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.ao_bake_settings

        layout.prop(settings, "layer_name", icon='GROUP_VCOL')
        layout.operator(AO_BAKE_OT_vertex_color.bl_idname, icon='IPO_EXPO')


# Registration
classes = (
    AOBakeSettings,
    AO_BAKE_OT_vertex_color,
    AO_BAKE_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ao_bake_settings = bpy.props.PointerProperty(type=AOBakeSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ao_bake_settings



