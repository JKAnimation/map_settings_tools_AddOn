bl_info = {
    "name": "Map Setting Tools",
    "blender": (4,3,2),
    "category": "Object",
    "author": "juankanimation",
    "version": (3,0,0),
}

import bpy
import os

# Importar operadores
from .import_fbx_to_collections import OBJECT_OT_import_fbx_to_collections
from .rename_plates import OBJECT_OT_rename_plates
from .apply_fullbuilding_sys import OBJECT_OT_apply_fullbuilding_sys
from .apply_activecollection_sys import OBJECT_OT_apply_activecollection_sys
from .update_fullbuilding_sys_inputs import OBJECT_OT_update_fullbuilding_sys_inputs
from .standard_settings import OBJECT_OT_standard_settings
from .blocking_settings import OBJECT_OT_blocking_settings
from .clean_setdressing_collections import OBJECT_OT_clean_setdressing_collections
from .clean_building_collections import OBJECT_OT_clean_building_collections
from .export_fbx import OBJECT_OT_export_fbx
from .clean_figma_curves import OBJECT_OT_clean_figma_curves
from .export_buildings_fbx import OBJECT_OT_buildings_export_fbx
from .generate_csv_report import OBJECT_OT_generate_csv_report

# Importar operadores de Geometry Nodes
from .load_geometry_nodes import (
    OBJECT_OT_load_landmark_plates,
    OBJECT_OT_load_multisnap,
    OBJECT_OT_load_edge_distribution,
    OBJECT_OT_load_area_distribution,
    OBJECT_OT_PostsWithFlags,
    OBJECT_OT_CleanNearest,
    OBJECT_OT_RoadPaths,
    OBJECT_OT_FlatBorders,
)

# Importar operadores de orden de objetos
from .object_order_tools import (
    OBJECT_UL_custom_list,
    ObjectListItem,
    OBJECT_OT_add_to_list,
    OBJECT_OT_remove_from_list,
    OBJECT_OT_move_item,
    OBJECT_OT_apply_order,
)

# Importar procesador de mallas
from .procesar_mallas import (
    OBJECT_OT_procesar_desde_coleccion,
    ProcesarDuplicadorProps,
)

# NUEVO: importar actualización de colección externa
from .actualizar_coleccion_externa import (
    OBJECT_OT_actualizar_coleccion_externa,
    ActualizarFBXProps,
)

# Importar paneles
from .menu import (
    VIEW3D_PT_map_setting_tools,
    VIEW3D_PT_building__tools,
    VIEW3D_PT_set_dressing_tools,
    VIEW3D_PT_export_tools,
    VIEW3D_PT_collection_list_tools,
    VIEW3D_PT_procesar_mallas,
)

# Registrar propiedades
def register_properties():
    bpy.types.Scene.export_folder = bpy.props.StringProperty(
        name="Export Folder",
        description="Selecciona la carpeta para exportar los archivos FBX",
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
        description="Seleccionar una colección para almacenar instancias"
    )

    bpy.types.Scene.entrances_collection = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Entrances collection",
        description="Seleccionar una colección para montar las entradas de los landmarks"
    )

    bpy.types.Scene.export_csv_path = bpy.props.StringProperty(
        name="Export CSV Path",
        description="Selecciona la carpeta para guardar el archivo CSV",
        default="//",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.my_objects = bpy.props.CollectionProperty(type=ObjectListItem)
    bpy.types.Scene.my_objects_index = bpy.props.IntProperty()

    bpy.types.Scene.procesar_coleccion_props = bpy.props.PointerProperty(type=ProcesarDuplicadorProps)

    # NUEVA propiedad para actualizar FBX desde archivo externo
    bpy.types.Scene.actualizar_fbx_props = bpy.props.PointerProperty(type=ActualizarFBXProps)

def unregister_properties():
    del bpy.types.Scene.create_road_help
    del bpy.types.Scene.export_folder
    del bpy.types.Scene.split_collection
    del bpy.types.Scene.entrances_collection
    del bpy.types.Scene.export_csv_path
    del bpy.types.Scene.my_objects
    del bpy.types.Scene.my_objects_index
    del bpy.types.Scene.procesar_coleccion_props
    del bpy.types.Scene.actualizar_fbx_props

# Lista de clases
classes = (
    OBJECT_OT_rename_plates,
    OBJECT_OT_import_fbx_to_collections,
    OBJECT_OT_standard_settings,
    OBJECT_OT_apply_fullbuilding_sys,
    OBJECT_OT_apply_activecollection_sys,
    OBJECT_OT_update_fullbuilding_sys_inputs,
    OBJECT_OT_blocking_settings,
    VIEW3D_PT_map_setting_tools,
    VIEW3D_PT_building__tools,
    VIEW3D_PT_set_dressing_tools,
    VIEW3D_PT_export_tools,
    VIEW3D_PT_collection_list_tools,
    OBJECT_OT_clean_setdressing_collections,
    OBJECT_OT_clean_building_collections,
    OBJECT_OT_export_fbx,
    OBJECT_OT_clean_figma_curves,
    OBJECT_UL_custom_list,
    ObjectListItem,
    OBJECT_OT_add_to_list,
    OBJECT_OT_remove_from_list,
    OBJECT_OT_move_item,
    OBJECT_OT_apply_order,
    OBJECT_OT_load_landmark_plates,
    OBJECT_OT_load_multisnap,
    OBJECT_OT_load_edge_distribution,
    OBJECT_OT_load_area_distribution,
    OBJECT_OT_PostsWithFlags,
    OBJECT_OT_CleanNearest,
    OBJECT_OT_RoadPaths,
    OBJECT_OT_FlatBorders,
    OBJECT_OT_generate_csv_report,
    OBJECT_OT_buildings_export_fbx,
    OBJECT_OT_procesar_desde_coleccion,
    ProcesarDuplicadorProps,
    OBJECT_OT_actualizar_coleccion_externa,      # NUEVO operador
    ActualizarFBXProps,                          # NUEVO struct de propiedades
    VIEW3D_PT_procesar_mallas,
)

# Función extra del menú (opcional)
def menu_func(self, context):
    self.layout.operator(OBJECT_OT_standard_settings.bl_idname, icon='PLUGIN')
    self.layout.operator(OBJECT_OT_rename_plates.bl_idname, icon='PLUGIN')
    self.layout.operator(OBJECT_OT_update_fullbuilding_sys_inputs.bl_idname, icon='PLUGIN')
    self.layout.operator(OBJECT_OT_blocking_settings.bl_idname, icon='PLUGIN')

# Registro principal
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
