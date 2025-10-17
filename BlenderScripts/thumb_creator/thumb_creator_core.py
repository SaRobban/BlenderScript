import bpy
import os
import subprocess
import tempfile

BLENDER_EXECUTABLE = bpy.app.binary_path

THUMB_SCRIPT = '''
import bpy

output_path = "{output_path}"
width = {width}
height = {height}

scene = bpy.context.scene

# ⚠️ Check for camera
if not scene.camera:
    # Try to find one
    for obj in scene.objects:
        if obj.type == 'CAMERA':
            scene.camera = obj
            break
    else:
        # No camera found — create one
        cam_data = bpy.data.cameras.new("AutoThumbnailCamera")
        cam_obj = bpy.data.objects.new("AutoThumbnailCamera", cam_data)
        scene.collection.objects.link(cam_obj)
        scene.camera = cam_obj

        # Default position
        cam_obj.location = (5, -5, 5)
        cam_obj.rotation_euler = (1.1, 0, 0.785)

# Render settings
scene.render.resolution_x = width
scene.render.resolution_y = height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 90
scene.render.filepath = output_path

# Render
bpy.ops.render.render(write_still=True)
print(f"✅ Thumbnail saved: {{output_path}}")
'''

class ThumbnailGenSettings(bpy.types.PropertyGroup):
    root_folder: bpy.props.StringProperty(
        name="Root Folder",
        subtype='DIR_PATH',
        description="Folder to search for .blend files"
    )
    thumb_width: bpy.props.IntProperty(name="Width", default=512, min=1)
    thumb_height: bpy.props.IntProperty(name="Height", default=512, min=1)
    blend_files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

def find_blend_files(folder):
    results = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".blend"):
                results.append(os.path.join(root, f))
    return results

def generate_thumbnail_external(blend_path, width, height):
    base = os.path.splitext(blend_path)[0]
    output_path = base + "_thumb.jpg"

    script_text = THUMB_SCRIPT.format(
        output_path=output_path.replace("\\", "\\\\"),
        width=width,
        height=height,
    )

    with tempfile.NamedTemporaryFile('w', delete=False, suffix=".py") as tmp_script:
        tmp_script.write(script_text)
        tmp_script_path = tmp_script.name

    subprocess.run([
        BLENDER_EXECUTABLE,
        "--background",
        blend_path,
        "--python", tmp_script_path
    ], check=True)

class THUMBGEN_OT_FindFiles(bpy.types.Operator):
    bl_idname = "thumbgen.find_files"
    bl_label = "Find .blend Files"
    bl_description = "Search recursively for .blend files in the selected folder"

    def execute(self, context):
        settings = context.scene.thumbgen_settings
        settings.blend_files.clear()

        if not os.path.isdir(settings.root_folder):
            self.report({'WARNING'}, "Invalid root folder")
            return {'CANCELLED'}

        found = find_blend_files(settings.root_folder)
        for path in found:
            item = settings.blend_files.add()
            item.name = os.path.basename(path)
            item["full_path"] = path

        self.report({'INFO'}, f"Found {len(found)} .blend files.")
        return {'FINISHED'}

class THUMBGEN_OT_GenerateThumbs(bpy.types.Operator):
    bl_idname = "thumbgen.generate_thumbnails"
    bl_label = "Generate Thumbnails"
    bl_description = "Render thumbnails for each .blend file"

    def execute(self, context):
        settings = context.scene.thumbgen_settings

        if not settings.blend_files:
            self.report({'WARNING'}, "No files found.")
            return {'CANCELLED'}

        for item in settings.blend_files:
            blend_path = item.get("full_path")
            if not blend_path or not os.path.isfile(blend_path):
                continue
            self.report({'INFO'}, f"Rendering: {item.name}")
            try:
                generate_thumbnail_external(blend_path, settings.thumb_width, settings.thumb_height)
            except Exception as e:
                self.report({'WARNING'}, f"Failed: {item.name} ({e})")
                continue

        self.report({'INFO'}, "All thumbnails rendered.")
        return {'FINISHED'}
