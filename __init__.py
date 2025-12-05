bl_info = {
    "name": "Map Setting Tools",
    "blender": (5, 0, 0),
    "category": "Object",
    "author": "juankanimation",
    "version": (3, 0, 0),
}

import bpy
import os

# -------------------------------------------------------------------------
# Importar módulos
# -------------------------------------------------------------------------

from . import import_fbx_to_collections
from . import rename_plates
from . import apply_fullbuilding_sys
from . import apply_activecollection_sys
from . import update_fullbuilding_sys_inputs
from . import standard_settings
from . import blocking_settings
from . import clean_setdressing_collections
from . import clean_building_collections
from . import export_fbx
from . import clean_figma_curves
from . import export_buildings_fbx
from . import generate_csv_report

# Geometry Nodes
from . import load_geometry_nodes

# Ordenamiento de objetos
from . import object_order_tools

# Procesador de mallas
from . import procesar_mallas

# Actualizar FBX externo
from . import actualizar_coleccion_externa

# Paneles
from . import menu


# -------------------------------------------------------------------------
# Registrar propiedades
# -------------------------------------------------------------------------

def register_properties():
    bpy.types.Scene.export_folder = bpy.props.StringProperty(
        name="Export Folder",
        description="Selecciona la carpeta para exportar",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.create_road_help = bpy.props.BoolProperty(
        name="Road",
        description="Generar malla RoadHelp",
        default=True
    )

    bpy.types.Scene.split_collection = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Split collection",
    )

    bpy.types.Scene.entrances_collection = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Entrances collection",
    )

    bpy.types.Scene.export_csv_path = bpy.props.StringProperty(
        name="Export CSV Path",
        description="Carpeta donde se guardará el CSV",
        default="//",
        subtype='DIR_PATH'
    )

    # Lista de orden manual
    bpy.types.Scene.my_objects = bpy.props.CollectionProperty(
        type=object_order_tools.ObjectListItem
    )
    bpy.types.Scene.my_objects_index = bpy.props.IntProperty()

    # Props de procesar mallas
    bpy.types.Scene.procesar_coleccion_props = bpy.props.PointerProperty(
        type=procesar_mallas.ProcesarDuplicadorProps
    )

    bpy.types.Scene.actualizar_fbx_props = bpy.props.PointerProperty(
        type=actualizar_coleccion_externa.ActualizarFBXProps
    )


def unregister_properties():
    props = (
        "export_folder",
        "create_road_help",
        "split_collection",
        "entrances_collection",
        "export_csv_path",
        "my_objects",
        "my_objects_index",
        "procesar_coleccion_props",
        "actualizar_fbx_props",
    )

    for p in props:
        if hasattr(bpy.types.Scene, p):
            try:
                delattr(bpy.types.Scene, p)
            except:
                pass


# -------------------------------------------------------------------------
# Construir lista global de clases desde cada módulo
# -------------------------------------------------------------------------

classes = []

modules = [
    import_fbx_to_collections,
    rename_plates,
    apply_fullbuilding_sys,
    apply_activecollection_sys,
    update_fullbuilding_sys_inputs,
    standard_settings,
    blocking_settings,
    clean_setdressing_collections,
    clean_building_collections,
    export_fbx,
    clean_figma_curves,
    export_buildings_fbx,
    generate_csv_report,
    load_geometry_nodes,
    object_order_tools,
    procesar_mallas,
    actualizar_coleccion_externa,
    menu,
]

for m in modules:
    if hasattr(m, "classes"):
        classes.extend(m.classes)


# -------------------------------------------------------------------------
# Registro principal
# -------------------------------------------------------------------------

def register():
    # Primero PropertyGroups / UILIsts
    for cls in classes:
        bpy.utils.register_class(cls)

    register_properties()


def unregister():
    unregister_properties()

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass


if __name__ == "__main__":
    register()
