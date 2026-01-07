import bpy
import math


# ------------------------------------------------------------
# OPERADOR
# ------------------------------------------------------------

class OBJECT_OT_clean_figma_curves(bpy.types.Operator):
    bl_idname = "object.clean_figma_curves"
    bl_label = "Clean Figma Curves"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clean curves from Figma and create blocking / levels collections."

    def execute(self, context):
        active_collection = context.collection
        if not active_collection:
            self.report({'ERROR'}, "No active collection")
            return {'CANCELLED'}

        # --------------------------------------------------
        # FILTRAR OBJETOS
        # --------------------------------------------------

        objects_to_keep = [obj for obj in active_collection.objects if obj.name.startswith("R_")]
        objects_to_delete = [
            obj for obj in active_collection.objects
            if not obj.name.startswith("R_") and obj.name != "R_Base_Streets"
        ]

        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        objects_to_keep = [obj for obj in objects_to_keep if obj.name in bpy.data.objects]

        # --------------------------------------------------
        # PROCESOS BASE (NO SE TOCAN)
        # --------------------------------------------------

        transform_and_convert_objects(objects_to_keep)
        apply_decimate_planar()

        if any(obj.name.startswith("R_Center") for obj in active_collection.objects):
            recenter_collection_to_r_center(active_collection)

        # --------------------------------------------------
        # BACKUP DE R_EXTERNAL (ANTES DE RENOMBRAR)
        # --------------------------------------------------

        external_backup = None
        external_obj = bpy.data.objects.get("R_External")

        if external_obj:
            external_backup = external_obj.copy()
            external_backup.data = external_obj.data.copy()

        # --------------------------------------------------
        # BLOCKING
        # --------------------------------------------------

        blocking_sources = {
            "R_Land": "Special",
            "R_Green": "Green",
            "R_River": "River",
            "R_Street": "Street",
            "R_External": "Ext"
        }

        create_named_collection_from_sources(
            source_map=blocking_sources,
            target_collection_name="Blocking",
            duplicate_sources=None,
            require_any=True
        )

        # --------------------------------------------------
        # LEVELS
        # --------------------------------------------------

        level_sources = {
            "R_Lvl1": "Lvl1",
            "R_Lvl2": "Lvl2",
            "R_Lvl3": "Lvl3",
        }

        create_named_collection_from_sources(
            source_map=level_sources,
            target_collection_name="Levels",
            duplicate_sources={"__EXTERNAL_BACKUP__": "Lvl0"},
            require_any=True,
            external_backup=external_backup
        )

        self.report({'INFO'}, f"Clean Figma Curves finished for '{active_collection.name}'")
        return {'FINISHED'}


# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------

def remove_collection_and_data(collection_name):
    col = bpy.data.collections.get(collection_name)
    if not col:
        return

    for obj in list(col.objects):
        mesh_data = obj.data if obj.type == 'MESH' else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh_data and mesh_data.users == 0:
            bpy.data.meshes.remove(mesh_data)

    bpy.data.collections.remove(col)


def transform_and_convert_objects(objects):
    for obj in objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        if obj.type == 'CURVE' and obj.name not in {"R_TransportPath", "R_WOF"}:
            bpy.ops.object.convert(target='MESH')

        obj.data.name = obj.name

        bpy.ops.transform.resize(value=(400, 400, 400))
        bpy.ops.transform.rotate(value=math.pi, orient_axis='Z')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        obj.select_set(False)


def apply_decimate_planar():
    angle_limit = math.radians(1)
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            mod = obj.modifiers.new("DecimatePlanar", 'DECIMATE')
            mod.decimate_type = 'DISSOLVE'
            mod.angle_limit = angle_limit

            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.modifier_apply(modifier=mod.name)
            obj.select_set(False)


def recenter_collection_to_r_center(collection):
    center_obj = next((o for o in collection.objects if o.name.startswith("R_Center")), None)
    if not center_obj:
        return

    cursor = bpy.context.scene.cursor
    original_cursor = cursor.location.copy()

    bpy.context.view_layer.objects.active = center_obj
    center_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    cursor.location = center_obj.location.copy()

    for obj in collection.objects:
        if obj != center_obj:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.select_set(False)

    offset = -cursor.location
    for obj in collection.objects:
        obj.location += offset

    cursor.location = original_cursor


def create_named_collection_from_sources(
    source_map,
    target_collection_name,
    duplicate_sources=None,
    require_any=True,
    external_backup=None
):
    found_sources = [
        obj for name in source_map
        if (obj := bpy.data.objects.get(name))
    ]

    if require_any and not found_sources:
        return

    remove_collection_and_data(target_collection_name)

    new_col = bpy.data.collections.new(target_collection_name)
    bpy.context.scene.collection.children.link(new_col)

    # --------------------------------------------------
    # MOVER / CONVERTIR
    # --------------------------------------------------

    for source_name, new_name in source_map.items():
        obj = bpy.data.objects.get(source_name)
        if not obj:
            continue

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        if obj.type == 'CURVE':
            bpy.ops.object.convert(target='MESH')

        obj.name = new_name
        obj.data.name = new_name

        for col in list(obj.users_collection):
            col.objects.unlink(obj)

        new_col.objects.link(obj)
        obj.select_set(False)

    # --------------------------------------------------
    # DUPLICADOS
    # --------------------------------------------------

    if duplicate_sources:
        for src_name, dup_name in duplicate_sources.items():

            if src_name == "__EXTERNAL_BACKUP__":
                src = external_backup
            else:
                src = bpy.data.objects.get(src_name)

            if not src:
                continue

            dup = src.copy()
            dup.data = src.data.copy()
            dup.name = dup_name
            dup.data.name = dup_name

            new_col.objects.link(dup)


# ------------------------------------------------------------
# REGISTRO
# ------------------------------------------------------------

classes = (
    OBJECT_OT_clean_figma_curves,
)
