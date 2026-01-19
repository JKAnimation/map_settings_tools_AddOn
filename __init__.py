bl_info = {
    "name": "Map Setting Tools",
    "blender": (5, 0, 0),
    "category": "Object",
    "author": "juankanimation",
    "version": (4, 0, 0),
}

import bpy
import importlib
import traceback
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, PointerProperty

# Import renamer tool classes
from .renamer_tool import (
    RenamerItem,
    RENAMER_UL_items,
    RENAMER_OT_populate,
    RENAMER_OT_clear,
    RENAMER_OT_find_replace,
    RENAMER_OT_apply_prefix_suffix,
    RENAMER_OT_autofill,
    RENAMER_OT_move_item,
    RENAMER_OT_execute
)

# Lista de nombres de módulos
module_names = [
    "import_fbx_to_collections",
    "rename_plates",
    "apply_fullbuilding_sys",
    "apply_activecollection_sys",
    "update_fullbuilding_sys_inputs",
    "standard_settings",
    "blocking_settings",
    "clean_setdressing_collections",
    "clean_building_collections",
    "export_fbx",
    "clean_figma_curves",
    "export_buildings_fbx",
    "generate_csv_report",
    "load_geometry_nodes",
    "object_order_tools",
    "procesar_mallas",
    "actualizar_coleccion_externa",
    "renamer_tool",
    "menu",
]

# Inicializar diccionario de módulos
modules = {}
classes = []

# Cargar dinámicamente todos los módulos
for module_name in module_names:
    try:
        module = importlib.import_module(f".{module_name}", package=__package__)
        modules[module_name] = module
        importlib.reload(module)
        
        # Recolectar clases
        for item in dir(module):
            item_obj = getattr(module, item)
            if hasattr(item_obj, 'bl_rna') and issubclass(item_obj, (bpy.types.Operator, bpy.types.Panel, bpy.types.PropertyGroup)):
                globals()[item] = item_obj
                if item_obj not in classes:
                    classes.append(item_obj)
                    
    except Exception as e:
        print(f"Error importing {module_name}: {str(e)}")
        traceback.print_exc()

# Asegurar que las clases del renamer estén incluidas
renamer_classes = [
    RenamerItem,
    RENAMER_UL_items,
    RENAMER_OT_populate,
    RENAMER_OT_clear,
    RENAMER_OT_find_replace,
    RENAMER_OT_apply_prefix_suffix,
    RENAMER_OT_autofill,
    RENAMER_OT_move_item,
    RENAMER_OT_execute
]

for cls in renamer_classes:
    if cls not in classes:
        classes.append(cls)

def register_properties():
    # Propiedades base
    if not hasattr(bpy.types.Scene, "export_folder"):
        bpy.types.Scene.export_folder = bpy.props.StringProperty(
            name="Export Folder",
            subtype='DIR_PATH',
            default=""
        )
    
    # Propiedades del renamer
    if not hasattr(bpy.types.Scene, "renamer_items"):
        bpy.types.Scene.renamer_items = bpy.props.CollectionProperty(type=RenamerItem)
        bpy.types.Scene.renamer_active_index = bpy.props.IntProperty()
        bpy.types.Scene.renamer_clear_on_populate = bpy.props.BoolProperty(
            name="Clear on Populate", 
            default=True
        )
        bpy.types.Scene.renamer_find = bpy.props.StringProperty(name="Find")
        bpy.types.Scene.renamer_replace = bpy.props.StringProperty(name="Replace")
        bpy.types.Scene.renamer_prefix = bpy.props.StringProperty(name="Prefix")
        bpy.types.Scene.renamer_suffix = bpy.props.StringProperty(name="Suffix")
        bpy.types.Scene.renamer_auto_underscore = bpy.props.BoolProperty(
            name="Auto Underscore", 
            default=True
        )
        bpy.types.Scene.renamer_preserve_base = bpy.props.BoolProperty(
            name="Preserve Base Name", 
            default=False
        )
        bpy.types.Scene.renamer_base_name = bpy.props.StringProperty(name="Base Name")
        bpy.types.Scene.renamer_start_number = bpy.props.IntProperty(
            name="Start Number", 
            default=1, 
            min=0
        )
        bpy.types.Scene.renamer_zero_padding = bpy.props.IntProperty(
            name="Digits", 
            default=2, 
            min=1, 
            max=5
        )
    
    # Otras propiedades
    if not hasattr(bpy.types.Scene, "split_collection"):
        bpy.types.Scene.split_collection = bpy.props.PointerProperty(
            type=bpy.types.Collection,
            name="Target Collection",
            description="Collection where objects will be moved"
        )
        bpy.types.Scene.apply_activecollection_make_data_single = bpy.props.BoolProperty(
            name="Make Single User",
            default=True,
            description="Make objects single user (duplicate data)"
        )
        bpy.types.Scene.split_geometry = bpy.props.BoolProperty(
            name="Process Only Selected",
            default=False,
            description="Only process selected objects instead of the entire collection"
        )

def unregister_properties():
    # Propiedades base
    base_props = [
        "export_folder", "create_road_help", "split_collection", "entrances_collection",
        "export_csv_path", "my_objects", "my_objects_index", "procesar_coleccion_props",
        "actualizar_fbx_props", "apply_activecollection_make_data_single"
    ]
    
    # Propiedades del renamer
    renamer_props = [
        "renamer_items",
        "renamer_active_index",
        "renamer_clear_on_populate",
        "renamer_find",
        "renamer_replace",
        "renamer_prefix",
        "renamer_suffix",
        "renamer_auto_underscore",
        "renamer_preserve_base",
        "renamer_base_name",
        "renamer_start_number",
        "renamer_zero_padding"
    ]
    
    # Combinar todas las propiedades
    all_props = base_props + renamer_props
    
    # Eliminar propiedades
    for prop_name in all_props:
        if hasattr(bpy.types.Scene, prop_name):
            try:
                delattr(bpy.types.Scene, prop_name)
            except Exception as e:
                print(f"Warning: Could not remove property {prop_name}: {str(e)}")

def register():
    # Registrar clases
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registrando {cls}: {e}")
            traceback.print_exc()
    
    # Registrar propiedades
    register_properties()
    
    print(f"[Map Setting Tools] {len(classes)} clases registradas")

def unregister():
    # Desregistrar propiedades
    unregister_properties()
    
    # Desregistrar clases en orden inverso
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error desregistrando {cls}: {e}")
            traceback.print_exc()
    
    print("[Map Setting Tools] Desregistrado")

if __name__ == "__main__":
    register()