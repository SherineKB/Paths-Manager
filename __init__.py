bl_info = {
    "name": "Paths Manager",
    "description": "Addon to manage images paths",
    "author": "Sherine KACMAZ BELHAINE",
    "version": (4, 2, 2),
    "location": "View3D > Sidebar",
    "category": "3D View",
}

import bpy
from . import core, methode

def register():
    for cls in core.classes:
        bpy.utils.register_class(cls)
    for cls in methode.classes:
        bpy.utils.register_class(cls)
    
    # Add custom properties to the scene
    bpy.types.Scene.old_path = bpy.props.StringProperty(name="Old Path")
    bpy.types.Scene.new_path = bpy.props.StringProperty(name="New Path")
    bpy.types.Scene.select_all = bpy.props.BoolProperty(name="Select All", default=False, update=methode.select_all)
    bpy.types.Scene.image_paths = bpy.props.CollectionProperty(type=core.ImagePathProperty)
    bpy.types.Image.selected = bpy.props.BoolProperty(name="Select", default=False)

    bpy.context.preferences.filepaths.use_relative_paths = False
    # Convert paths to absolute on startup
    methode.absolute_path(bpy.context.scene)

def unregister():
    for cls in reversed(methode.classes):
        bpy.utils.unregister_class(cls)
    for cls in reversed(core.classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.old_path
    del bpy.types.Scene.new_path
    del bpy.types.Scene.select_all
    del bpy.types.Scene.image_paths
    del bpy.types.Image.selected

if __name__ == "__main__":
    register()
