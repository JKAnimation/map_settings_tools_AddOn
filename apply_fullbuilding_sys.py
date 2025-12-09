import bpy
from mathutils import Vector
import re

class OBJECT_OT_apply_fullbuilding_sys(bpy.types.Operator):
    bl_idname = "object.apply_fullbuilding_sys"
    bl_label = "Apply FullBuilding Sys"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales y los organiza en colecciones"

    @classmethod
    def poll(cls, context):
        collection_names = ["Buildings_Exp", "Facades_Exp", "Letters_Exp", "Plates_Exp", "Bases_Exp", "Stairs_Exp", "Numbers_Exp"]
        for name in collection_names:
            collection = bpy.data.collections.get(name)
            if collection and len(collection.objects) == 0:
                return True
        return False

    def execute(self, context):
        organize_objects()
        context.view_layer.update()
        detect_walls_inside_buildings()
        context.view_layer.update()
        process_facades()
        context.view_layer.update()
        self.report({'INFO'}, "Sistema aplicado exitosamente.")
        return {'FINISHED'}

# Funciones auxiliares

def make_collection_instances_real(collection):
    """Convierte las instancias de una colección en objetos reales y elimina los originales."""
    if not collection or not collection.objects:
        print(f"[make_collection_instances_real] ❌ La colección '{collection.name}' está vacía o no existe.")
        return []

    # Guardar los objetos originales antes de hacer reales
    original_names = {obj.name for obj in collection.objects}

    # Des-seleccionar todo
    bpy.ops.object.select_all(action='DESELECT')

    # Seleccionar y activar uno de los objetos originales
    for obj in collection.objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = collection.objects[0]

    # Hacer instancias reales
    bpy.ops.object.duplicates_make_real()

    # Identificar los nuevos objetos reales (los que antes no estaban en la colección)
    new_objects = [obj for obj in bpy.context.selected_objects if obj.name not in original_names]

    # Mover nuevos objetos a la misma colección, por si acaso
    move_objects_to_collection(new_objects, collection)

    # Eliminar los objetos originales
    for name in original_names:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    print(f"[make_collection_instances_real] ✅ {len(new_objects)} objetos creados y originales eliminados en '{collection.name}'")
    return new_objects


def expand_volume(container, expansion):
    bbox_corners = [Vector(container.matrix_world @ Vector(corner)) for corner in container.bound_box]
    min_corner = Vector([min(corner[i] for corner in bbox_corners) for i in range(3)])
    max_corner = Vector([max(corner[i] for corner in bbox_corners) for i in range(3)])
    return min_corner - expansion, max_corner + expansion

def is_point_inside_volume(container, point, expansion=Vector((0.1, 0.1, 0.1))):
    expanded_min, expanded_max = expand_volume(container, expansion)
    return all(expanded_min[i] <= point[i] <= expanded_max[i] for i in range(3))

def clean_name(name):
    return re.sub(r'\.\d+$', '', name)

def update_object_data(obj, new_name):
    """Actualiza la data compartida del objeto asegurando que use la correcta."""
    new_name = clean_name(new_name)
    if obj.data:
        new_data_name = new_name.replace("P_","S_") +"_Coll"
        
        # Verificar si la nueva data ya existe
        existing_data = bpy.data.meshes.get(new_data_name)
        if existing_data:
            obj.data = existing_data  # Usar la data existente
        else:
            # Crear una nueva copia de la data actual con el nuevo nombre
            obj.data = obj.data.copy()
            obj.data.name = new_data_name

def force_refresh_objects(objects, delta=0.001):
    for obj in objects:
        original_loc = obj.location.copy()
        obj.location.x += delta
        bpy.context.view_layer.update()
        obj.location = original_loc
        bpy.context.view_layer.update()


# Paso 1: Organizar edificios y fachadas

def organize_objects():
    collections = {
        "00_Buildings": "Buildings_Exp",
        "01_Facades": "Facades_Exp",
        "02_Numbers": "Numbers_Exp"
    }
    master_collection = bpy.data.collections.get("Master")
    if not master_collection:
        return
    for obj in master_collection.objects:
        if obj.name in collections:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.duplicates_make_real()
            move_objects_to_collection(bpy.context.selected_objects, bpy.data.collections.get(collections[obj.name]))

    print('Paso 01 finalizado')


# Paso 2: Detectar y actualizar entradas

def detect_walls_inside_buildings():
    buildings_collection = bpy.data.collections.get("Buildings_Exp")
    facades_collection = bpy.data.collections.get("Facades_Exp")
    
    if not buildings_collection:
        print("No se encontró la colección 'Buildings_Exp'.")
        return
    if not facades_collection:
        print("No se encontró la colección 'Facades_Exp'.")
        return
    
    buildings = [obj for obj in buildings_collection.objects if "_Building_" in obj.name]
    walls = [obj for obj in facades_collection.objects if "_Wall_" in obj.name]
    apts = [obj for obj in facades_collection.objects if "_APT_" in obj.name]
    
    for building in buildings:
        building_number = building.name.split("_")[3]
        for wall in walls:
            if is_point_inside_volume(building, wall.location):
                new_name = clean_name(wall.name.replace(wall.name.split("_")[3], building_number))
                wall.name = new_name
                update_object_data(wall, new_name)
        for apt in apts:
            if is_point_inside_volume(building, apt.location):
                new_name = clean_name(apt.name.replace(apt.name.split("_")[4], building_number))
                apt.name = new_name
                update_object_data(apt, new_name)
    
    print('Paso 02 finalizado')

# Paso 3: Aplicar nodo y hacer reales las instancias

def process_facades():
    facades_collection = bpy.data.collections.get("Facades_Exp")
    plates_collection = bpy.data.collections.get("Plates_Exp")
    letters_collection = bpy.data.collections.get("Letters_Exp")
    if not facades_collection or not plates_collection or not letters_collection:
        return

    # Asignar el nodo a las fachadas si no lo tienen
    for obj in facades_collection.objects:
        if "Facades_Plates" not in obj.modifiers:
            mod = obj.modifiers.new(name="Facades_Plates", type='NODES')
            mod.node_group = bpy.data.node_groups.get("Facades_Plates")

    bpy.context.view_layer.update()
    force_refresh_objects(facades_collection.objects)

    print('Nodo asignado y actualizado en facades')

    # Duplicar objetos para Plates (con misma data y modificadores)
    duplicated_plates = []
    for obj in facades_collection.objects:
        obj.modifiers["Facades_Plates"]["Socket_2"] = 1

        dup = bpy.data.objects.new(obj.name + "_plate", obj.data)
        dup.location = obj.location.copy()
        dup.rotation_euler = obj.rotation_euler.copy()
        dup.scale = obj.scale.copy()
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.name == "Facades_Plates":
                new_mod = dup.modifiers.new(name=mod.name, type='NODES')
                new_mod.node_group = mod.node_group
                for key in mod.keys():
                    if key.startswith("Socket_"):
                        new_mod[key] = mod[key]
        duplicated_plates.append(dup)

    move_objects_to_collection(duplicated_plates, plates_collection)
    force_refresh_objects(facades_collection.objects)
    make_collection_instances_real(plates_collection)

    # Duplicar objetos para Letters (con misma data)
    duplicated_letters = []
    for obj in facades_collection.objects:
        obj.modifiers["Facades_Plates"]["Socket_2"] = 2

        dup = bpy.data.objects.new(obj.name + "_letter", obj.data)
        dup.location = obj.location.copy()
        dup.rotation_euler = obj.rotation_euler.copy()
        dup.scale = obj.scale.copy()
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.name == "Facades_Plates":
                new_mod = dup.modifiers.new(name=mod.name, type='NODES')
                new_mod.node_group = mod.node_group
                for key in mod.keys():
                    if key.startswith("Socket_"):
                        new_mod[key] = mod[key]
        duplicated_letters.append(dup)

    move_objects_to_collection(duplicated_letters, letters_collection)
    force_refresh_objects(facades_collection.objects)
    make_collection_instances_real(letters_collection)

    # Restaurar modificador en las originales
    for obj in facades_collection.objects:
        obj.modifiers["Facades_Plates"]["Socket_2"] = 0
    bpy.context.view_layer.update()
    force_refresh_objects(facades_collection.objects)
    print('Facades actualizados')




def move_objects_to_collection(objects, target_collection):
    for obj in objects:
        # Asegurar que esté enlazado a la colección destino
        if target_collection not in obj.users_collection:
            target_collection.objects.link(obj)
        # Eliminarlo de otras colecciones si es necesario
        for col in obj.users_collection:
            if col != target_collection:
                col.objects.unlink(obj)





def register():
    bpy.utils.register_class(OBJECT_OT_apply_fullbuilding_sys)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_apply_fullbuilding_sys)

if __name__ == "__main__":
    register()
