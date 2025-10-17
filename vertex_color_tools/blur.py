# blur.py
import bpy
import bmesh
from mathutils import Color
from . import config

# Core function

def blur_vertex_colors(obj, iterations=1):
    mesh = obj.data
    color_layer = mesh.color_attributes.active_color

    if not color_layer:
        print("No active vertex color layer found.")
        return

    if color_layer.domain != 'POINT':
        print("Only POINT domain vertex colors supported.")
        return

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    # Store current colors
    color_data = list(color_layer.data)
    for _ in range(iterations):
        new_colors = []

        for i, v in enumerate(bm.verts):
            current_col = Color(color_data[i].color[:3])
            total_col = Color((0.0, 0.0, 0.0))
            total_weight = 0.0

            for e in v.link_edges:
                neighbor = e.other_vert(v)
                n_idx = neighbor.index
                n_col = Color(color_data[n_idx].color[:3])

                dist = (v.co - neighbor.co).length
                weight = 1.0 / dist if dist > 0 else 1.0

                total_col += n_col * weight
                total_weight += weight

            # Include self in average
            total_col += current_col * 1.0
            total_weight += 1.0

            avg_col = total_col / total_weight
            new_colors.append(avg_col)

        # Apply new colors to temp color data
        for i, col in enumerate(new_colors):
            color_data[i].color = (col.r, col.g, col.b, 1.0)

    # Write final result to the mesh
    for i, col in enumerate(color_data):
        color_layer.data[i].color = col.color

    bm.free()
    mesh.update()
    print(f"Blur applied to '{color_layer.name}' with {iterations} iteration(s).")


#  Operator

class OBJECT_OT_blur_vertex_colors(bpy.types.Operator):
    bl_idname = "object.blur_vertex_colors"
    bl_label = "Apply Blur"
    bl_description = "Apply blur effect to active vertex color layer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

        iterations = context.scene.vcol_blur_strength
        blur_vertex_colors(obj, iterations)
        return {'FINISHED'}


# Panel

class VIEW3D_PT_vertex_color_blur(bpy.types.Panel):
    bl_label = "Blur"
    bl_idname = "VIEW3D_PT_vertex_color_blur"
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
        obj = context.active_object
        color_layer = obj.data.color_attributes.active_color

        if color_layer:
            layout.label(text=f"Active Layer: {color_layer.name}")
            layout.prop(context.scene, "vcol_blur_strength", text="Strength (Iterations)")
            layout.operator("object.blur_vertex_colors", icon="MOD_SMOOTH")
        else:
            layout.label(text="No active vertex color layer", icon='ERROR')



# Propertis

def register_props():
    bpy.types.Scene.vcol_blur_strength = bpy.props.IntProperty(
        name="Blur Iterations",
        description="How many times to apply the blur",
        default=1,
        min=1,
        max=50
    )

def unregister_props():
    del bpy.types.Scene.vcol_blur_strength


# Register

classes = (
    OBJECT_OT_blur_vertex_colors,
    VIEW3D_PT_vertex_color_blur,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_props()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_props()

if __name__ == "__main__":
    register()
