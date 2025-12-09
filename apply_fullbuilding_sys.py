import bpy
from mathutils import Vector
import re

# =========================================================
#               OPERATOR PRINCIPAL
# =========================================================

class OBJECT_OT_apply_fullbuilding_sys(bpy.types.Operator):
    bl_idname = "object.apply_fullbuilding_sys"
    bl_label = "Apply FullBuilding Sys"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Convierte instancias en objetos reales, actualiza nombres, "
        "hace matching por volumen, aplica geometry nodes, y genera "
        "Plates y Letters."
    )

    @classmethod
    def poll(cls, context):
        collection_names = [
            "Buildings_Exp",
            "Facades_Exp",
            "Letters_Exp",
            "Plates_Exp",
            "Bases_Exp",
            "Stairs_Exp",
            "Numbers_Exp"
        ]

        for name in collection_names:
            col = bpy.data.collections.get(name)
            if col and len(col.objects) == 0:
                return True
        return False

    def execute(self, context):
        organize_objects()
        context.view_layer.update()

        detect_walls_inside_buildings()
        context.view_layer.update()

        process_facades()
        context.view_layer.update()

        self.report({'INFO'}, "Sistema FullBuilding aplicado exitosamente.")
        return {'FINISHED'}


# =========================================================
#            FUNCIONES AUXILIARES GENERALES
# =========================================================

def clean_name(name):
    return re.sub(r'\.\d+$', '', name)


def update_object_data(obj, new_name):
    """
    Cambia la data del objeto a una copia única con el nombre adecuado.
    """
    new_name = clean_name(new_name)
    if not obj.data:
        return

    new_data_name = new_name.replace("P_", "S_") + "_Coll"

    existing = bpy.data.meshes.get(new_data_name)
    if existing:
        obj.data = existing
    else:
        obj.data = obj.data.copy()
        obj.data.name = new_data_name


def expand_volume(container, expansion):
    bbox = [container.matrix_world @ Vector(corner) for corner in container.bound_box]
    min_corner = Vector([min(v[i] for v in bbox) for i in range(3)])
    max_corner = Vector([max(v[i] for v in bbox) for i in range(3)])
    return min_corner - expansion, max_corner + expansion


def is_point_inside_volume(container, point, expansion=Vector((0.1, 0.1, 0.1))):
    mn, mx = expand_volume(container, expansion)
    return all(mn[i] <= point[i] <= mx[i] for i in range(3))


def force_refresh(objects, delta=0.001):
    """
    Soluciona problemas de actualización forzando cambios leves.
    """
    for obj in objects:
        old = obj.location.copy()
        obj.location.x += delta
        bpy.context.view_layer.update()
        obj.location = old
        bpy.context.view_layer.update()


def move_objects_to_collection(objects, target_collection):
    for obj in objects:
        if target_collection not in obj.users_collection:
            target_collection.objects.link(obj)

        for col in list(obj.users_collection):
            if col != target_collection:
                col.objects.unlink(obj)


def make_collection_instances_real(collection):
    if not collection or not collection.objects:
        print(f"[make_collection_instances_real] ❌ '{collection.name}' vacía o no existe.")
        return []

    original = {o.name for o in collection.objects}

    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = collection.objects[0]
    bpy.ops.object.duplicates_make_real()

    new_objects = [
        o for o in bpy.context.selected_objects
        if o.name not in original
    ]

    move_objects_to_collection(new_objects, collection)

    for name in original:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    print(f"[make_collection_instances_real] {len(new_objects)} creados en '{collection.name}'")
    return new_objects


# =========================================================
#               PASO 1 – ORGANIZAR OBJETOS
# =========================================================

def organize_objects():
    mapping = {
        "00_Buildings": "Buildings_Exp",
        "01_Facades": "Facades_Exp",
        "02_Numbers": "Numbers_Exp"
    }

    master = bpy.data.collections.get("Master")
    if not master:
        print("No existe colección Master.")
        return

    for obj in master.objects:
        if obj.name in mapping:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.duplicates_make_real()

            dst = bpy.data.collections.get(mapping[obj.name])
            move_objects_to_collection(bpy.context.selected_objects, dst)

    print("Paso 01: Organización completada.")


# =========================================================
#       PASO 2 – MATCH WALL/APT INSIDE BUILDINGS
# =========================================================

def detect_walls_inside_buildings():
    col_build = bpy.data.collections.get("Buildings_Exp")
    col_facad = bpy.data.collections.get("Facades_Exp")

    if not col_build or not col_facad:
        print("Faltan colecciones para matching.")
        return

    buildings = [o for o in col_build.objects if "_Building_" in o.name]
    walls = [o for o in col_facad.objects if "_Wall_" in o.name]
    apts = [o for o in col_facad.objects if "_APT_" in o.name]

    for b in buildings:
        num = b.name.split("_")[3]

        for w in walls:
            if is_point_inside_volume(b, w.location):
                new = clean_name(w.name.replace(w.name.split("_")[3], num))
                w.name = new
                update_object_data(w, new)

        for a in apts:
            if is_point_inside_volume(b, a.location):
                new = clean_name(a.name.replace(a.name.split("_")[4], num))
                a.name = new
                update_object_data(a, new)

    print("Paso 02: Walls/APT actualizados.")


# =========================================================
#           PASO 3 – GENERAR PLATES Y LETTERS
# =========================================================

def process_facades():
    col_f = bpy.data.collections.get("Facades_Exp")
    col_p = bpy.data.collections.get("Plates_Exp")
    col_l = bpy.data.collections.get("Letters_Exp")

    if not col_f or not col_p or not col_l:
        print("Faltan colecciones para Plates y Letters.")
        return

    # Aplicar nodo si falta
    for obj in col_f.objects:
        if "Facades_Plates" not in obj.modifiers:
            m = obj.modifiers.new(name="Facades_Plates", type='NODES')
            m.node_group = bpy.data.node_groups.get("Facades_Plates")

    force_refresh(col_f.objects)
    print("Nodo aplicado en Facades.")

    # ---------------------------------------------------------
    # DUPLICAR PARA PLATES
    # ---------------------------------------------------------
    duplicates_p = []

    for obj in col_f.objects:
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

        duplicates_p.append(dup)

    move_objects_to_collection(duplicates_p, col_p)
    force_refresh(col_f.objects)
    make_collection_instances_real(col_p)

    # ---------------------------------------------------------
    # DUPLICAR PARA LETTERS
    # ---------------------------------------------------------
    duplicates_l = []

    for obj in col_f.objects:
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

        duplicates_l.append(dup)

    move_objects_to_collection(duplicates_l, col_l)
    force_refresh(col_f.objects)
    make_collection_instances_real(col_l)

    # Restaurar el nodo original (Socket_2 = 0)
    for obj in col_f.objects:
        obj.modifiers["Facades_Plates"]["Socket_2"] = 0

    force_refresh(col_f.objects)
    print("Paso 03: Plates y Letters generados.")

