import bpy
import math

class OBJECT_OT_clean_figma_curves(bpy.types.Operator):
    bl_idname = "object.clean_figma_curves"
    bl_label = "Clean Figma Curves"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clean curves from Figma and create blocking collection."

    def execute(self, context):
        active_collection = context.collection
        if not active_collection:
            self.report({'ERROR'}, "No active collection")
            return {'CANCELLED'}

        # Filtrar objetos relevantes
        objects_to_keep = [obj for obj in active_collection.objects if obj.name.startswith("R_")]
        objects_to_delete = [obj for obj in active_collection.objects if not obj.name.startswith("R_") and obj.name != "R_Base_Streets"]

        # Eliminar objetos no deseados
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Asegurar que los objetos a conservar aún existan
        objects_to_keep = [obj for obj in objects_to_keep if obj.name in bpy.data.objects]

        # Procesar objetos principales
        transform_and_convert_objects(objects_to_keep)
        apply_decimate_planar()

        # Aplicar “Recenter” si existe R_Center
        if any(obj.name.startswith("R_Center") for obj in active_collection.objects):
            recenter_collection_to_r_center(active_collection)

        create_blocking()

        self.report({'INFO'}, f"Standard settings applied to collection '{active_collection.name}'")
        return {'FINISHED'}


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def transform_and_convert_objects(objects):
    for obj in objects:
        if obj.type == 'CURVE':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            if obj.name not in ["R_TransportPath", "R_WOF"]:
                bpy.ops.object.convert(target='MESH')
        obj.data.name = obj.name
        bpy.context.view_layer.objects.active = obj
        bpy.ops.transform.resize(value=(400, 400, 400))
        bpy.ops.transform.rotate(value=math.pi, orient_axis='Z')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.select_set(False)


def create_blocking():
    blocking_sources = {
        "R_Land": "Special",
        "R_Green": "Green",
        "R_River": "River",
        "R_Street": "Street"
    }
    blocking_collection = bpy.data.collections.get("Blocking")
    if not blocking_collection:
        blocking_collection = bpy.data.collections.new("Blocking")
        bpy.context.scene.collection.children.link(blocking_collection)

    for source_name, new_name in blocking_sources.items():
        obj = bpy.data.objects.get(source_name)
        if obj:
            obj.name = new_name
            obj.data.name = new_name
            for col in obj.users_collection:
                col.objects.unlink(obj)
            blocking_collection.objects.link(obj)


def apply_decimate_planar():
    angle_limit = math.radians(1)
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            dec_mod = obj.modifiers.new(name="DecimatePlanar", type='DECIMATE')
            dec_mod.decimate_type = 'DISSOLVE'
            dec_mod.angle_limit = angle_limit
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.modifier_apply(modifier=dec_mod.name)
            obj.select_set(False)


def recenter_collection_to_r_center(collection):
    context = bpy.context
    center_obj = next((obj for obj in collection.objects if obj.name.startswith("R_Center")), None)
    if not center_obj:
        return

    cursor_original = context.scene.cursor.location.copy()
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = center_obj
    center_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    cursor_loc = center_obj.location.copy()
    context.scene.cursor.location = cursor_loc

    for obj in collection.objects:
        if obj != center_obj:
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    offset = -cursor_loc
    for obj in collection.objects:
        obj.location += offset

    context.scene.cursor.location = cursor_original
    print(f"✅ Colección '{collection.name}' centrada con R_Center en el origen global.")


# ------------------------------------------------------------
# NUEVO: lista de clases que exporta este módulo
# ------------------------------------------------------------

classes = (
    OBJECT_OT_clean_figma_curves,
)
