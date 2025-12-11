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

# -------------------------------------------------------------------
# Lista de nombres de módulos que usa tu menú (añade/quita si hace falta)
# -------------------------------------------------------------------
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
    # geometry nodes module (varios operadores dentro)
    "load_geometry_nodes",
    # orden / UI list
    "object_order_tools",
    # procesar mallas
    "procesar_mallas",
    # actualizar FBX externo
    "actualizar_coleccion_externa",
    # paneles
    "menu",
]

# -------------------------------------------------------------------
# Intentar importar todos los módulos; si falla, seguir (mostrar error)
# -------------------------------------------------------------------
modules = {}
for name in module_names:
    try:
        modules[name] = importlib.import_module(f".{name}", package=__package__)
    except Exception:
        print(f"[MapSettingTools] ERROR importando módulo '{name}':\n{traceback.format_exc()}")

# -------------------------------------------------------------------
# Colección dinámica de clases a registrar
# - Buscamos en cada módulo clases que sean subclass de tipos Blender:
#   Operator, Panel, PropertyGroup, UIList
# -------------------------------------------------------------------
classes = []

_bl_types = (bpy.types.Operator, bpy.types.Panel, bpy.types.PropertyGroup, bpy.types.UIList)

for mod_name, mod in modules.items():
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        try:
            if isinstance(attr, type):
                # evitar registrar clases internas o clases ajenas
                if issubclass(attr, _bl_types) and attr.__module__ == mod.__name__:
                    classes.append(attr)
        except Exception:
            # issubclass puede fallar si attr no es clase; ignorar
            pass

# El módulo 'menu' puede definir Panels con nombres distintos; nos aseguramos de incluirlos también
# (están recogidos por el bucle anterior si existen)

# -------------------------------------------------------------------
# Registrar propiedades de Scene (solo si existen dependencias)
# -------------------------------------------------------------------
def register_properties():
    # propiedades simples (si no existen ya)
    if not hasattr(bpy.types.Scene, "export_folder"):
        bpy.types.Scene.export_folder = bpy.props.StringProperty(
            name="Export Folder", description="Selecciona la carpeta para exportar los archivos FBX", subtype='DIR_PATH'
        )

    if not hasattr(bpy.types.Scene, "create_road_help"):
        bpy.types.Scene.create_road_help = bpy.props.BoolProperty(
            name="Road", description="Generar malla RoadHelp", default=True
        )

    # split_collection y entrances_collection son Pointer a Collection (siempre válidos)
    if not hasattr(bpy.types.Scene, "split_collection"):
        bpy.types.Scene.split_collection = bpy.props.PointerProperty(
            type=bpy.types.Collection, name="Split collection", description="Seleccionar una colección para almacenar instancias"
        )

    if not hasattr(bpy.types.Scene, "entrances_collection"):
        bpy.types.Scene.entrances_collection = bpy.props.PointerProperty(
            type=bpy.types.Collection, name="Entrances collection", description="Seleccionar una colección para montar las entradas de los landmarks"
        )

    if not hasattr(bpy.types.Scene, "export_csv_path"):
        bpy.types.Scene.export_csv_path = bpy.props.StringProperty(
            name="Export CSV Path", default="//", subtype='DIR_PATH'
        )

    # Props que dependen de módulos externos: object_order_tools.ObjectListItem
    obj_order_mod = modules.get("object_order_tools")
    if obj_order_mod and hasattr(bpy.types.Scene, "my_objects") is False:
        try:
            bpy.types.Scene.my_objects = bpy.props.CollectionProperty(type=getattr(obj_order_mod, "ObjectListItem"))
            bpy.types.Scene.my_objects_index = bpy.props.IntProperty()
        except Exception:
            print("[MapSettingTools] Warning: no se pudo crear Scene.my_objects (ObjectListItem no disponible)")

    # Procesar mallas props
    procesar_mod = modules.get("procesar_mallas")
    if procesar_mod and hasattr(bpy.types.Scene, "procesar_coleccion_props") is False:
        if hasattr(procesar_mod, "ProcesarDuplicadorProps"):
            try:
                bpy.types.Scene.procesar_coleccion_props = bpy.props.PointerProperty(type=getattr(procesar_mod, "ProcesarDuplicadorProps"))
            except Exception:
                print("[MapSettingTools] Warning: no se pudo crear procesar_coleccion_props")

    # Actualizar FBX externo props
    actual_mod = modules.get("actualizar_coleccion_externa")
    if actual_mod and hasattr(bpy.types.Scene, "actualizar_fbx_props") is False:
        if hasattr(actual_mod, "ActualizarFBXProps"):
            try:
                bpy.types.Scene.actualizar_fbx_props = bpy.props.PointerProperty(type=getattr(actual_mod, "ActualizarFBXProps"))
            except Exception:
                print("[MapSettingTools] Warning: no se pudo crear actualizar_fbx_props")


def unregister_properties():
    for p in (
        "export_folder", "create_road_help", "split_collection", "entrances_collection",
        "export_csv_path", "my_objects", "my_objects_index", "procesar_coleccion_props",
        "actualizar_fbx_props"
    ):
        if hasattr(bpy.types.Scene, p):
            try:
                delattr(bpy.types.Scene, p)
            except Exception:
                pass

# -------------------------------------------------------------------
# Registro principal
# -------------------------------------------------------------------
def register():
    # registrar clases en el orden encontrado
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            print(f"[MapSettingTools] ERROR registrando {cls}:")
            traceback.print_exc()

    # propiedades
    register_properties()

    print("[MapSettingTools] registrado. Clases registradas:", len(classes))


def unregister():
    unregister_properties()

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            print(f"[MapSettingTools] ERROR desregistrando {cls}:")
            traceback.print_exc()

    print("[MapSettingTools] desregistrado.")


if __name__ == "__main__":
    register()
