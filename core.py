import bpy
import os
from . import methode  # Le module methode fournit les fonctions utilitaires

# Properties group used to store name and path
class ImagePathProperty(bpy.types.PropertyGroup):
    image_name: bpy.props.StringProperty(name="Image Name")
    image_path: bpy.props.StringProperty(name="Image Path")

# Principal panel - media list, checkboxes, ...
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

        images = methode.media()  # Appel à la fonction utilitaire intégrée dans methode.py
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

# Subpanel - Relocate all paths
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

# Classes
classes = (
    ImagePathProperty,
    PathsManager,
    RelocatePanel,
)
