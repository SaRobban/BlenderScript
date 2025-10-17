import bpy
import bmesh
from mathutils import Vector

UV_LAYER_NAME = "UVSprite"

class MESH_OT_uv_project_per_quad(bpy.types.Operator):
    bl_idname = "mesh.uv_project_per_quad"
    bl_label = "UV Project Per Face"
    bl_description = "Planar UV unwrap per face, scaled and aligned to global up. Each face starts UV at (0,0) or world-scaled."
    bl_options = {'REGISTER', 'UNDO'}

    tile_range: bpy.props.IntProperty(
        name="Tile Range",
        default=8,
        min=1,
        description="Number of tiles per UV unit (1.0 / tile_range = UV scale)"
    )

    scale_mode: bpy.props.EnumProperty(
        name="Scale Mode",
        items=(
            ('TILE', "Tile Units", "Normalize each face to a tile (fits exactly in 1/tile_range space)"),
            ('WORLD', "World Units", "Use face world-space size scaled by 1/tile_range"),
        ),
        default='TILE'
    )

    preserve_aspect: bpy.props.BoolProperty(
        name="Preserve Aspect Ratio",
        default=True,
        description="Keep original face proportions when scaling into a tile"
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}

        in_edit_mode = (context.mode == 'EDIT_MESH')

        if in_edit_mode:
            bm = bmesh.from_edit_mesh(obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)

        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        global_up = Vector((0, 0, 1))
        global_x = Vector((1, 0, 0))
        global_y = Vector((0, 1, 0))
        threshold = 0.999

        # Create or get the UV layer
        uv_layer = bm.loops.layers.uv.get(UV_LAYER_NAME)
        if not uv_layer:
            uv_layer = bm.loops.layers.uv.new(UV_LAYER_NAME)

        tile_size = 1.0 / self.tile_range
        eps = 1e-9

        for face in bm.faces:
            # Support all polygons (tris, quads, ngons)
            if len(face.verts) < 3:
                continue

            origin = face.calc_center_median()
            normal = face.normal.normalized()
            alignment = abs(normal.dot(global_up))

            if alignment > threshold:
                u_axis = global_x
                v_axis = global_y
            else:
                u_axis = global_up.cross(normal).normalized()
                v_axis = normal.cross(u_axis).normalized()

            # Collect raw u/v coordinates (object-space projected onto the chosen axes)
            raw_uvs = []
            for loop in face.loops:
                rel = loop.vert.co - origin
                u = rel.dot(u_axis)
                v = rel.dot(v_axis)
                raw_uvs.append(Vector((u, v)))

            # Compute bounding box in raw UV space
            min_u = min(uv.x for uv in raw_uvs)
            max_u = max(uv.x for uv in raw_uvs)
            min_v = min(uv.y for uv in raw_uvs)
            max_v = max(uv.y for uv in raw_uvs)

            size_u = max_u - min_u
            size_v = max_v - min_v

            if self.scale_mode == 'TILE':
                # Compute scales so the UV bbox maps to tile_size
                if size_u < eps and size_v < eps:
                    # Degenerate face - map to (0,0)
                    for loop in face.loops:
                        loop[uv_layer].uv = Vector((0.0, 0.0))
                    continue

                if self.preserve_aspect:
                    # Uniform scale based on largest dimension so face fits within tile
                    larger = max(size_u, size_v, eps)
                    scale = tile_size / larger
                    scale_u = scale_v = scale
                else:
                    scale_u = tile_size / size_u if size_u > eps else 1.0
                    scale_v = tile_size / size_v if size_v > eps else 1.0

                # Map into tile space with bottom-left at (0,0)
                for loop, raw in zip(face.loops, raw_uvs):
                    mapped = Vector(((raw.x - min_u) * scale_u, (raw.y - min_v) * scale_v))
                    loop[uv_layer].uv = mapped

            else:  # WORLD mode
                # World-space scaled by 1/tile_range so textures repeat predictably
                # Here tile_size acts as the multiplier to convert world unit to UV unit
                if size_u < eps and size_v < eps:
                    for loop in face.loops:
                        loop[uv_layer].uv = Vector((0.0, 0.0))
                    continue

                # Map raw units directly multiplied by tile_size and shift so bbox min is (0,0)
                for loop, raw in zip(face.loops, raw_uvs):
                    mapped = Vector(( (raw.x - min_u) * tile_size, (raw.y - min_v) * tile_size ))
                    loop[uv_layer].uv = mapped

        if in_edit_mode:
            bmesh.update_edit_mesh(obj.data)
        else:
            bm.to_mesh(obj.data)
            obj.data.update()
            bm.free()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_uv_project_per_quad)

def unregister():
    bpy.utils.unregister_class(MESH_OT_uv_project_per_quad)

if __name__ == "__main__":
    register()
