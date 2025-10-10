import bpy
import os

def link_scene_and_group(blend_file_path, scene_name):
    if not os.path.exists(blend_file_path):
        print(f"File not found: {blend_file_path}")
        return False

    # Link the scene (this brings in all associated data, including node groups)
    with bpy.data.libraries.load(blend_file_path, link=True) as (data_from, data_to):
        if scene_name in data_from.scenes:
            data_to.scenes.append(scene_name)
            return True
        else:
            print(f"Scene '{scene_name}' not found.")
            return False


def setup_compositor_with_group(group_name):
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree

    # Check if group exists
    node_group = bpy.data.node_groups.get(group_name)
    if not node_group:
        print(f"Compositor node group '{group_name}' not found.")
        return False

    # Clear existing nodes (optional)
    for node in tree.nodes:
        tree.nodes.remove(node)

    # Add basic nodes
    render_layer = tree.nodes.new("CompositorNodeRLayers")
    group_node = tree.nodes.new("CompositorNodeGroup")
    composite = tree.nodes.new("CompositorNodeComposite")

    group_node.node_tree = node_group

    # Position nodes
    render_layer.location = (-400, 0)
    group_node.location = (0, 0)
    composite.location = (400, 0)

    # Auto-connect
    try:
        tree.links.new(render_layer.outputs["Image"], group_node.inputs[0])
        tree.links.new(group_node.outputs[0], composite.inputs["Image"])
    except IndexError:
        print("⚠️ Group may not have expected input/output sockets.")
        return False

    return True

def clean_unneeded_data(keep_node_group_name=None):
    #import bpy

    keep_groups = set()

    if keep_node_group_name:
        group = bpy.data.node_groups.get(keep_node_group_name)
        if group:
            keep_groups.add(group)

    comp_tree = bpy.context.scene.node_tree
    if comp_tree:
        for node in comp_tree.nodes:
            if node.type == 'GROUP' and node.node_tree:
                keep_groups.add(node.node_tree)

    current_scene = bpy.context.scene
    for scene in list(bpy.data.scenes):
        if scene != current_scene:
            bpy.data.scenes.remove(scene)

    for obj in list(bpy.data.objects):
        if obj.users == 0:
            bpy.data.objects.remove(obj)

    for datablock in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.textures,
        bpy.data.images,
        bpy.data.curves,
        bpy.data.metaballs,
        bpy.data.collections,
    ):
        for item in list(datablock):
            if item.users == 0:
                datablock.remove(item)

    for ng in list(bpy.data.node_groups):
        if ng not in keep_groups and ng.users == 0:
            bpy.data.node_groups.remove(ng)

    print("🧹 Scene cleanup complete.")


def purge_unused_data():
    while True:
        result = bpy.ops.outliner.orphans_purge(do_recursive=True)
        if 'FINISHED' in result:
            print("Purged unused data.")
        else:
            print("Unexpected result:", result)
            break

