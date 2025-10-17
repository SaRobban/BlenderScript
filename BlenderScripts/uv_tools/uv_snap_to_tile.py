import bpy
import bmesh
from mathutils import Vector

class MESH_OT_uv_snap_to_tile(bpy.types.Operator):
    bl_idname = "mesh.uv_snap_to_tile"
    bl_label = "Snap UV to Tile"
    bl_description = "Move selected quad UVs to a specific tile in the UV grid"
    bl_options = {'REGISTER', 'UNDO'}

    tile_range: bpy.props.IntProperty(
        name="Tile Range",
        default=8,
        min=1,
        description="Number of tiles per unit (tiles per row/column)"
    )

    tile_position: bpy.props.IntProperty(
        name="Tile Position",
        default=0,
        min=0,
        description="Tile index (row-major order)"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}

        selected_faces = [f for f in bm.faces if f.select and len(f.verts) >= 3]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected to snap.")
            return {'CANCELLED'}

        tile_size = 1.0 / self.tile_range
        tile_x = self.tile_position % self.tile_range
        tile_y = self.tile_position // self.tile_range
        target_offset = Vector((tile_x * tile_size, tile_y * tile_size))

        for face in selected_faces:
            uvs = [loop[uv_layer].uv.copy() for loop in face.loops]
            min_uv = Vector((min(uv.x for uv in uvs), min(uv.y for uv in uvs)))
            delta = target_offset - min_uv
            for loop in face.loops:
                loop[uv_layer].uv += delta

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_uv_snap_to_tile)

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_snap_to_tile)

if __name__ == "__main__":
    register()
