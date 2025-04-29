import bpy
import os

bl_info = {
    "name": "Paths Manager",
    "description": "Addon to manage images paths",
    "author": "Sherine KACMAZ BELHAINE",
    "version": (4, 2, 2),
    "location": "View3D > Sidebar",
    "category": "3D View",
}

# List all the images and video files
def media():
    return [img for img in bpy.data.images if img.source in {'FILE', 'MOVIE'}]

# Set paths to absolute
def absolute_path(scene):
    for img in bpy.data.images:
        if img.filepath:
            absolute_path = bpy.path.abspath(img.filepath)
            img.filepath = absolute_path

# Relocate old path to new path
def relocate(images, old_part, new_part):
    found = False  # Variable pour vérifier si une modification a eu lieu
    for img in images:
        path = bpy.path.abspath(img.filepath)
        if old_part in path:
            new_path = path.replace(old_part, new_part)
            img.filepath = new_path
            found = True  # Une image a été modifiée
    return found  # Retourne True si au moins un changement a eu lieu, sinon False


# Select all
def select_all(self, context):
    for img in media():
        img.selected = self.select_all

# Properties group used to store name and path
class ImagePathProperty(bpy.types.PropertyGroup):
    image_name: bpy.props.StringProperty(name="Image Name")
    image_path: bpy.props.StringProperty(name="Image Path")

# OPERATOR - Unlink media
class IMAGE_OT_unlink(bpy.types.Operator):
    bl_idname = "image.unlink"
    bl_label = "Unlink Image"
    bl_options = {'REGISTER', 'UNDO'}

    image_name: bpy.props.StringProperty()
    
    def execute(self, context):
        image = bpy.data.images.get(self.image_name)
        if image:
            image.filepath = ""  # Supprimer le chemin
            bpy.context.preferences.filepaths.use_relative_paths = False  # Forcer le mode absolu
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
    """Relocalise toutes les images, indépendamment de la sélection."""
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
    """Recharge toutes les images en appelant la méthode reload() sur chacune."""
    bl_idname = "image.reload_all"
    bl_label = "Reload All Medias"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for img in bpy.data.images:
            if img.source in {'FILE', 'MOVIE'} and img.filepath:
                img.reload()
        self.report({'INFO'}, "Medias Reloaded.")
        return {'FINISHED'}

# PANEL - media list, checkboxes, ...
class PathsManager(bpy.types.Panel):
    bl_category = "Paths Manager"
    bl_label = "Media Paths"
    bl_idname = "VIEW3D_PT_paths_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "select_all", text="Select All")
        layout.operator("image.reload_all", text="Reload All Medias", icon="FILE_REFRESH")

        images = media()
        if not images:
            layout.label(text="No external media found")
        else:
            for img in images:
                box = layout.box()
                row = box.row()
                row.prop(img, "selected", text="")  # Checkbox de sélection
                abs_path = bpy.path.abspath(img.filepath)
                file_exists = os.path.exists(abs_path)
                icon = "ERROR" if not file_exists else "CHECKMARK"
                row.label(text="", icon=icon)
                row.alert = not file_exists
                row.prop(img, "filepath", text=f"{img.name}")
                op = row.operator("image.unlink", text="", icon="UNLINKED")
                op.image_name = img.name

# SUBPANEL - Relocate all paths
class RelocatePanel(bpy.types.Panel):
    bl_category = "Paths Manager"
    bl_label = "Relocate Path"
    bl_idname = "VIEW3D_PT_relocate_path"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_paths_manager"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        col.prop(scene, "old_path")
        col.prop(scene, "new_path")
        row = col.row()
        row.operator("image.relocate_selection", text="Relocate Selection")
        row.operator("image.relocate_all", text="Relocate All")
# All classes
classes = [
    IMAGE_OT_unlink,
    IMAGE_OT_relocate_selection,
    IMAGE_OT_relocate_all,
    IMAGE_OT_reload_all,
    ImagePathProperty,
    PathsManager,
    RelocatePanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add custom properties to the scene    
    bpy.types.Scene.old_path = bpy.props.StringProperty(name="Old Path")
    bpy.types.Scene.new_path = bpy.props.StringProperty(name="New Path")
    bpy.types.Scene.select_all = bpy.props.BoolProperty(name="Select All", default=False, update=select_all)
    bpy.types.Scene.image_paths = bpy.props.CollectionProperty(type=ImagePathProperty)
    bpy.types.Image.selected = bpy.props.BoolProperty(name="Select", default=False)

    bpy.context.preferences.filepaths.use_relative_paths = False
    absolute_path(bpy.context.scene)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.old_path
    del bpy.types.Scene.new_path
    del bpy.types.Scene.select_all
    del bpy.types.Scene.image_paths
    del bpy.types.Image.selected

if __name__ == "__main__":
    register()