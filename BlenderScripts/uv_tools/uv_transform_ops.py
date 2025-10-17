import bpy
import bmesh
from mathutils import Vector

class MESH_OT_uv_rotate_tiles(bpy.types.Operator):
    bl_idname = "mesh.uv_rotate_tiles"
    bl_label = "Rotate UV Tile"
    bl_description = "Rotate selected face UVs by 90 degree steps around their bounding box center"
    bl_options = {'REGISTER', 'UNDO'}

    steps: bpy.props.IntProperty(
        name="90° Steps",
        default=1,
        min=-3,
        max=3,
        description="Number of 90-degree steps to rotate (positive = clockwise)"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        steps = self.steps % 4
        if steps == 0:
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer")
            return {'CANCELLED'}

        selected_faces = [f for f in bm.faces if f.select and len(f.verts) >= 3]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected to rotate.")
            return {'CANCELLED'}

        for face in selected_faces:
            uvs = [loop[uv_layer].uv.copy() for loop in face.loops]
            min_uv = Vector((min(uv.x for uv in uvs), min(uv.y for uv in uvs)))
            max_uv = Vector((max(uv.x for uv in uvs), max(uv.y for uv in uvs)))
            center = (min_uv + max_uv) * 0.5
            new_uvs = []
            for uv in uvs:
                rel = uv - center
                x, y = rel.x, rel.y
                # Apply 90deg rotation 'steps' times (clockwise): (x,y) -> (y, -x)
                for i in range(steps):
                    x, y = y, -x
                new_uvs.append(Vector((x, y)) + center)
            # After rotation, align bbox min back to original min to keep tile anchoring
            new_min = Vector((min(uv.x for uv in new_uvs), min(uv.y for uv in new_uvs)))
            delta = min_uv - new_min
            for loop, uv in zip(face.loops, new_uvs):
                loop[uv_layer].uv = uv + delta

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


class MESH_OT_uv_flip_tiles(bpy.types.Operator):
    bl_idname = "mesh.uv_flip_tiles"
    bl_label = "Flip UV Tile"
    bl_description = "Flip selected face UVs horizontally (U) or vertically (V) around their bounding box center"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=(('U', "U (Horizontal)", "Flip horizontally"),
               ('V', "V (Vertical)", "Flip vertically")),
        default='U'
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
            self.report({'WARNING'}, "No faces selected to flip.")
            return {'CANCELLED'}

        for face in selected_faces:
            uvs = [loop[uv_layer].uv.copy() for loop in face.loops]
            min_uv = Vector((min(uv.x for uv in uvs), min(uv.y for uv in uvs)))
            max_uv = Vector((max(uv.x for uv in uvs), max(uv.y for uv in uvs)))
            center = (min_uv + max_uv) * 0.5
            new_uvs = []
            for uv in uvs:
                rel = uv - center
                if self.axis == 'U':
                    new_uvs.append(Vector((-rel.x, rel.y)) + center)
                else:
                    new_uvs.append(Vector((rel.x, -rel.y)) + center)
            # Align bbox min back to original min to keep tile anchoring
            new_min = Vector((min(uv.x for uv in new_uvs), min(uv.y for uv in new_uvs)))
            delta = min_uv - new_min
            for loop, uv in zip(face.loops, new_uvs):
                loop[uv_layer].uv = uv + delta

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_uv_rotate_tiles)
    bpy.utils.register_class(MESH_OT_uv_flip_tiles)

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_rotate_tiles)
    bpy.utils.unregister_class(MESH_OT_uv_flip_tiles)

if __name__ == "__main__":
    register()
