import bpy
import os

# List all the images and video files
def media():
    return [img for img in bpy.data.images if img.source in {'FILE', 'MOVIE'}]

# Set paths to absolute
def absolute_path(scene):
    for img in bpy.data.images:
        if img.filepath:
            abs_path = bpy.path.abspath(img.filepath)
            img.filepath = abs_path

# Relocate old path to new path
def relocate(images, old_part, new_part):
    found = False
    for img in images:
        path = bpy.path.abspath(img.filepath)
        if old_part in path:
            new_path = path.replace(old_part, new_part)
            img.filepath = new_path
            found = True
    return found

# Select all
def select_all(self, context):
    for img in media():
        img.selected = self.select_all

# OPERATOR - Unlink media
class IMAGE_OT_unlink(bpy.types.Operator):
    bl_idname = "image.unlink"
    bl_label = "Unlink Image"
    bl_options = {'REGISTER', 'UNDO'}

    image_name: bpy.props.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.image_name)
        if image:
            image.filepath = ""  # Supprime le chemin
            bpy.context.preferences.filepaths.use_relative_paths = False  # Mode absolu forcé
            self.report({'INFO'}, f"Image {self.image_name} unlinked")
        else:
            self.report({'ERROR'}, f"Image {self.image_name} not found")
            return {'CANCELLED'}
        return {'FINISHED'}

# OPERATOR - Relocate selected medias
class IMAGE_OT_relocate_selection(bpy.types.Operator):
    bl_idname = "image.relocate_selection"
    bl_label = "Relocate Selected Image Paths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        old_part = scene.old_path
        new_part = scene.new_path

        selected_images = [img for img in media() if img.selected]
        if not selected_images:
            self.report({'WARNING'}, "No images selected")
            return {'CANCELLED'}

        found = relocate(selected_images, old_part, new_part)
        if found:
            self.report({'INFO'}, "Selected paths updated successfully")
        else:
            self.report({'WARNING'}, "No matching paths found in selected images")
        return {'FINISHED'}

# OPERATOR - Relocate all medias
class IMAGE_OT_relocate_all(bpy.types.Operator):
    bl_idname = "image.relocate_all"
    bl_label = "Relocate All Image Paths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        old_part = scene.old_path
        new_part = scene.new_path

        all_images = media()
        found = relocate(all_images, old_part, new_part)
        if found:
            self.report({'INFO'}, "All paths updated successfully")
        else:
            self.report({'WARNING'}, "No matching paths found")
        return {'FINISHED'}

# OPERATOR - Reload all medias
class IMAGE_OT_reload_all(bpy.types.Operator):
    bl_idname = "image.reload_all"
    bl_label = "Reload All"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for img in bpy.data.images:
            if img.source in {'FILE', 'MOVIE'} and img.filepath:
                img.reload()
        self.report({'INFO'}, "Medias Reloaded.")
        return {'FINISHED'}

# Classes
classes = (
    IMAGE_OT_unlink,
    IMAGE_OT_relocate_selection,
    IMAGE_OT_relocate_all,
    IMAGE_OT_reload_all,
)
