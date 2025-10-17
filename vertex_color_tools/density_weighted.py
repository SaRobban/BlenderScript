# density_weighted.py

import bpy
import bmesh
import math
from mathutils import kdtree
from . import config

# Operator
class VERTEXDENSITY_OT_PaintDensityWeighted(bpy.types.Operator):
    bl_idname = "object.paint_vertex_density_weighted"
    bl_label = "Paint Weighted Vertex Density"
    bl_description = "Color vertices based on weighted local vertex density"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object.")
            return {'CANCELLED'}

        scene = context.scene
        radius = scene.vdp_radius
        max_density = scene.vdp_max_density
        layer_name = scene.vdp_layer_name.strip()

        if not layer_name:
            self.report({'ERROR'}, "Layer name is empty.")
            return {'CANCELLED'}

        mesh = obj.data

        # Create or get vertex color attribute (vertex domain)
        color_layer = mesh.color_attributes.get(layer_name)
        if not color_layer:
            color_layer = mesh.color_attributes.new(name=layer_name, type='FLOAT_COLOR', domain='POINT')

        mesh.color_attributes.active_color = color_layer

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()

        # Build KD-tree
        size = len(bm.verts)
        kd = kdtree.KDTree(size)
        for i, v in enumerate(bm.verts):
            kd.insert(v.co, i)
        kd.balance()

        # Compute weighted densities
        densities = [0.0] * size
        for i, v in enumerate(bm.verts):
            neighbors = kd.find_range(v.co, radius)
            weighted_density = 0.0
            for (co, index, dist) in neighbors:
                w = math.exp(- (dist / radius) ** 2)
                weighted_density += w
            weighted_density -= 1.0  # exclude self
            densities[i] = min(weighted_density / max_density, 1.0)

        # Write colors to vertex color attribute (vertex domain)
        for i, dens in enumerate(densities):
            color_layer.data[i].color = (dens, dens, dens, 1.0)

        bm.free()
        mesh.update()

        self.report({'INFO'}, f"Weighted vertex density painted to '{layer_name}'")
        return {'FINISHED'}


# Panel
class VERTEXDENSITY_PT_Panel(bpy.types.Panel):
    bl_label = "Density Shade"
    bl_idname = "VERTEXDENSITY_PT_panel"
    bl_parent_id = config.MAIN_PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "vdp_radius", slider=True)
        layout.prop(scene, "vdp_max_density", slider=True)
        layout.prop(scene, "vdp_layer_name", text="Layer Name")
        layout.operator("object.paint_vertex_density_weighted", icon='BRUSH_DATA', text="Apply Weighted Density")


# Register properties and classes
def register():
    bpy.utils.register_class(VERTEXDENSITY_OT_PaintDensityWeighted)
    bpy.utils.register_class(VERTEXDENSITY_PT_Panel)

    bpy.types.Scene.vdp_radius = bpy.props.FloatProperty(
        name="Radius",
        description="Radius to search neighbors",
        min=0.001,
        max=10.0,
        default=0.1,
        precision=3,
        step=0.1
    )

    bpy.types.Scene.vdp_max_density = bpy.props.FloatProperty(
        name="Max Density",
        description="Max density for normalization",
        min=0.1,
        max=100.0,
        default=10.0,
        precision=1,
        step=1
    )

    bpy.types.Scene.vdp_layer_name = bpy.props.StringProperty(
        name="Layer",
        description="Name of the vertex color layer",
        default="DensityColorWeighted"
    )


def unregister():
    bpy.utils.unregister_class(VERTEXDENSITY_OT_PaintDensityWeighted)
    bpy.utils.unregister_class(VERTEXDENSITY_PT_Panel)

    del bpy.types.Scene.vdp_radius
    del bpy.types.Scene.vdp_max_density
    del bpy.types.Scene.vdp_layer_name
