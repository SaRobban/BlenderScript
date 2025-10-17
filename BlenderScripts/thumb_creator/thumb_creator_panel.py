import bpy

class THUMBGEN_PT_Panel(bpy.types.Panel):
    bl_label = "Thumbnail Generator"
    bl_idname = "VIEW3D_PT_thumbgen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ThumbnailGen'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.thumbgen_settings

        layout.prop(settings, "root_folder")
        layout.prop(settings, "thumb_width")
        layout.prop(settings, "thumb_height")

        layout.operator("thumbgen.find_files", icon='FILE_FOLDER')
        layout.operator("thumbgen.generate_thumbnails", icon='RENDER_STILL')

        if settings.blend_files:
            layout.label(text=f"{len(settings.blend_files)} files found:")
            for item in settings.blend_files[:10]:
                layout.label(text=item.name, icon='FILE_BLEND')
            if len(settings.blend_files) > 10:
                layout.label(text=f"...and {len(settings.blend_files) - 10} more")
