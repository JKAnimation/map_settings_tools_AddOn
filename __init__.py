bl_info = {
    "name": "Map Setting Tools",
    "blender": (5, 0, 0),
    "category": "Object",
    "author": "juankanimation",
    "version": (3, 0, 0),
}

import bpy

# Importar operadores
from .standard_settings import OBJECT_OT_standard_settings
from .menu import (
    VIEW3D_PT_map_setting_tools,
    VIEW3D_PT_building__tools,
    VIEW3D_PT_set_dressing_tools,
    VIEW3D_PT_export_tools,
    VIEW3D_PT_collection_list_tools,
    VIEW3D_PT_procesar_mallas,
)

# Registrar propiedades mínimas (solo para este módulo por ahora)
def register_properties():
    bpy.types.Scene.create_road_help = bpy.props.BoolProperty(
        name="Road",
        description="Generar malla RoadHelp",
        default=True
    )

def unregister_properties():
    del bpy.types.Scene.create_road_help

# Lista de clases
classes = (
    OBJECT_OT_standard_settings,
    VIEW3D_PT_map_setting_tools,
    VIEW3D_PT_building__tools,
    VIEW3D_PT_set_dressing_tools,
    VIEW3D_PT_export_tools,
    VIEW3D_PT_collection_list_tools,
    VIEW3D_PT_procesar_mallas,
)

# Registro principal
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()

if __name__ == "__main__":
    register()
