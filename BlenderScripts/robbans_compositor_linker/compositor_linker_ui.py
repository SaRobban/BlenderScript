#from email.policy import default
import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty

from . import compositor_linker_core


class SceneCompositorLinkerProperties(PropertyGroup):
    filepath: StringProperty(
        name="Blend File",
        description="Path to the .blend file",
        subtype='FILE_PATH'
    )
    scene_name: StringProperty(
        name="Scene Name",
        description="Name of the scene to link",
        default="Scene"
    )
    group_name: StringProperty(
        name="Compositor Group",
        description="Name of the compositor node group to insert",
        default="FILTER"
    )

    auto_cleanup : BoolProperty(
        name="Purge on use", 
        description="Purges unused data on use",
        default=True
    )



class SCENE_LINKER_OT_LinkSceneAndGroup(Operator):
    bl_idname = "compositor_linker.link_scene_and_group"
    bl_label = "Link Compositor Group"
    bl_description = "Link and insert a compositor group node"

    def execute(self, context):
        props = context.scene.scene_compositor_linker_props
        path = bpy.path.abspath(props.filepath)
        scene_name = props.scene_name
        group_name = props.group_name

        auto_cleanup = props.auto_cleanup

        if not path or not scene_name or not group_name:
            self.report({'ERROR'}, "Please fill in all fields.")
            return {'CANCELLED'}

        success = compositor_linker_core.link_scene_and_group(path, scene_name)
        if not success:
            self.report({'ERROR'}, "Failed to link scene.")
            return {'CANCELLED'}

        if not compositor_linker_core.setup_compositor_with_group(group_name):
            self.report({'ERROR'}, f"Failed to add compositor group '{group_name}'")
            return {'CANCELLED'}

        self.report({'INFO'}, "Scene and compositor group linked successfully.")
        
        if not auto_cleanup:
            return {'FINISHED'}
        

        props = context.scene.scene_compositor_linker_props
        group_name = props.group_name.strip() or None

        compositor_linker_core.clean_unneeded_data(group_name)
        self.report({'INFO'}, "Auto Scene cleanup complete.")




        #Purge data 
        #NOTE!!! this purges globaly, for correct usage purge only linked data from our file
        #Ex. set fake user to all current file objects and list the changes. Purge data. And revert fake user in file.
        compositor_linker_core.purge_unused_data();
        self.report({'INFO'}, "Purge complete.")


        #while True:
        #    result = bpy.ops.outliner.orphans_purge(do_recursive=True)
        #    if 'FINISHED' in result:
        #        print("Purged unused data.")
        #    else:
        #        print("Unexpected result:", result)
        #        break

        return {'FINISHED'}


class SCENE_LINKER_OT_CleanupScene(Operator):
    bl_idname = "compositor_linker.cleanup_scene"
    bl_label = "Clean Unused Data"
    bl_description = "Delete unused objects, materials, scenes, etc., keeping only compositor data"

    def execute(self, context):
        props = context.scene.scene_compositor_linker_props
        group_name = props.group_name.strip() or None

        compositor_linker_core.clean_unneeded_data(group_name)
        self.report({'INFO'}, "Scene cleanup complete.")
        return {'FINISHED'}


class SCENE_LINKER_PT_Panel(Panel):
    bl_label = "Compositor Linker"
    bl_idname = "SCENE_LINKER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Compositor Linker'

    def draw(self, context):
        layout = self.layout
        props = context.scene.scene_compositor_linker_props

        layout.prop(props, "filepath")
        layout.prop(props, "scene_name")
        layout.prop(props, "group_name")

        if props.auto_cleanup:
            ghost_icon = "GHOST_DISABLED"
        else:
            ghost_icon = "GHOST_ENABLED"

        layout.prop(props, "auto_cleanup", icon=ghost_icon)

        layout.operator("compositor_linker.link_scene_and_group", icon="LINK_BLEND")
        layout.operator("compositor_linker.cleanup_scene", icon="TRASH")


# Registration
classes = (
    SceneCompositorLinkerProperties,
    SCENE_LINKER_OT_LinkSceneAndGroup,
    SCENE_LINKER_OT_CleanupScene,
    SCENE_LINKER_PT_Panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.scene_compositor_linker_props = PointerProperty(type=SceneCompositorLinkerProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.scene_compositor_linker_props
