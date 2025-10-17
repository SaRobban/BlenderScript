import bpy
from . import config

class VCTOOLBOX_PT_main(bpy.types.Panel):
    bl_label = "GO! Vertex Warrior"
    bl_idname = "VCTOOLBOX_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = config.BL_CATEGORY

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        #row.label(icon='FORCE_TURBULENCE')
        #row.label(icon='AUTO')
        row.label(icon='CON_ARMATURE')
        #row.label(icon='MOD_ARMATURE')
        row.label(icon='ARMATURE_DATA')
        #row.label(icon='FORCE_WIND')

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Choose a tool below.")


        
def register():
    bpy.utils.register_class(VCTOOLBOX_PT_main)

def unregister():
    bpy.utils.unregister_class(VCTOOLBOX_PT_main)