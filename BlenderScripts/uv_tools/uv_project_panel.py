import bpy

class VIEW3D_PT_uv_project_panel(bpy.types.Panel):
    bl_label = "UV Project & Snap"
    bl_idname = "VIEW3D_PT_uv_project_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "UV Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Project UV per Face:")
        row = col.row(align=True)
        row.prop(context.scene, "uv_scale_mode", text="Scale Mode")
        row.prop(context.scene, "uv_preserve_aspect", text="Preserve Aspect")
        col.prop(context.scene, "uv_tile_range", text="Tile Range")
        op = col.operator("mesh.uv_project_per_quad", text="Project UV")
        # pass properties to operator
        op.tile_range = context.scene.uv_tile_range
        op.scale_mode = context.scene.uv_scale_mode
        op.preserve_aspect = context.scene.uv_preserve_aspect

        col.separator()
        col.label(text="Tile Picker:")

        tile_range = context.scene.uv_tile_range
        tile_size = 1.0 / tile_range
        row_count = tile_range
        active_tile = context.scene.uv_tile_position

        for y in reversed(range(row_count)):
            row = col.row(align=True)
            for x in range(tile_range):
                tile_index = y * tile_range + x
                emboss = tile_index != active_tile
                op = row.operator("mesh.set_tile_position", text="", emboss=emboss)
                op.tile_index = tile_index

        col.separator()
        col.label(text="Snap & Transform:")
        # Snap controls
        snap_row = col.row(align=True)
        snap_row.prop(context.scene, "uv_tile_position", text="Tile Pos")
        snap_btn = snap_row.operator("mesh.uv_snap_to_tile", text="Snap")
        snap_btn.tile_range = context.scene.uv_tile_range
        snap_btn.tile_position = context.scene.uv_tile_position

        # Transform buttons
        trans_row = col.row(align=True)
        trans_row.operator("mesh.uv_rotate_tiles", text="Rotate CCW").steps = -1
        trans_row.operator("mesh.uv_rotate_tiles", text="Rotate CW").steps = 1

        trans_row = col.row(align=True)
        op = trans_row.operator("mesh.uv_flip_tiles", text="Flip U")
        op.axis = 'U'
        op = trans_row.operator("mesh.uv_flip_tiles", text="Flip V")
        op.axis = 'V'


class MESH_OT_set_tile_position(bpy.types.Operator):
    bl_idname = "mesh.set_tile_position"
    bl_label = "Set Tile Position"
    bl_description = "Set tile_position value for snapping"

    tile_index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.uv_tile_position = self.tile_index
        bpy.ops.mesh.uv_snap_to_tile(
            tile_range=context.scene.uv_tile_range,
            tile_position=self.tile_index
        )
        self.report({'INFO'}, f"Tile position set to {self.tile_index}")
        return {'FINISHED'}


def on_tile_position_changed(self, context):
    obj = context.active_object
    if obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH':
        bpy.ops.mesh.uv_snap_to_tile(
            tile_range=context.scene.uv_tile_range,
            tile_position=context.scene.uv_tile_position
        )


def register():
    bpy.utils.register_class(MESH_OT_set_tile_position)
    bpy.utils.register_class(VIEW3D_PT_uv_project_panel)

    bpy.types.Scene.uv_tile_range = bpy.props.IntProperty(
        name="Tile Range", default=8, min=1
    )

    bpy.types.Scene.uv_tile_position = bpy.props.IntProperty(
        name="Tile Position",
        default=0,
        min=0,
        description="Tile index (row-major)",
        update=on_tile_position_changed
    )

    bpy.types.Scene.uv_scale_mode = bpy.props.EnumProperty(
        name="Scale Mode",
        items=(('TILE', "Tile", ""), ('WORLD', "World", "")),
        default='TILE'
    )

    bpy.types.Scene.uv_preserve_aspect = bpy.props.BoolProperty(
        name="Preserve Aspect", default=True
    )

def unregister():
    bpy.utils.unregister_class(MESH_OT_set_tile_position)
    bpy.utils.unregister_class(VIEW3D_PT_uv_project_panel)
    del bpy.types.Scene.uv_tile_range
    del bpy.types.Scene.uv_tile_position
    del bpy.types.Scene.uv_scale_mode
    del bpy.types.Scene.uv_preserve_aspect

if __name__ == "__main__":
    register()
