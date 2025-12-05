import bpy

class OBJECT_OT_clean_setdressing_collections(bpy.types.Operator):
    bl_idname = "object.clean_setdressing_collections"
    bl_label = "Clean Set Dressing Collections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Elimina objetos en la colección de Set Dressing y limpia datos huérfanos"

    @classmethod
    def poll(cls, context):
        return bool(context.view_layer.active_layer_collection.collection.objects)

    def execute(self, context):
        collection = getattr(context.scene, "split_collection", None)
        if collection:
            for obj in list(collection.objects):
                if not obj.name.startswith("_"):
                    bpy.data.objects.remove(obj, do_unlink=True)
            self.report({'INFO'}, f"Objetos eliminados en la colección {collection.name}")
        else:
            self.report({'WARNING'}, "La colección no existe")

        # Limpiar datos huérfanos
        data_types = [
            bpy.data.meshes, bpy.data.materials, bpy.data.textures,
            bpy.data.lights, bpy.data.cameras, bpy.data.curves,
            bpy.data.images, bpy.data.node_groups, bpy.data.particles,
            bpy.data.speakers
        ]
        for data_collection in data_types:
            for data_block in list(data_collection):
                if not data_block.users:
                    data_collection.remove(data_block)

        self.report({'INFO'}, "Datos huérfanos eliminados correctamente")
        return {'FINISHED'}


# ------------------------------------------------------------
# NUEVO: lista de clases que exporta este módulo
# ------------------------------------------------------------

classes = (
    OBJECT_OT_clean_setdressing_collections,
)
