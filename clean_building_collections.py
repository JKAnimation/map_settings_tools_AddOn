import bpy

class OBJECT_OT_clean_building_collections(bpy.types.Operator):
    bl_idname = "object.clean_building_collections"
    bl_label = "Clean Building Collections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Elimina objetos en las colecciones de exportación y limpia datos huérfanos"

    collection_names = [
        "Buildings_Exp", "Facades_Exp", "Letters_Exp",
        "Plates_Exp", "Bases_Exp", "Stairs_Exp", "Numbers_Exp"
    ]

    @classmethod
    def poll(cls, context):
        return any(
            (col := bpy.data.collections.get(name)) and len(col.objects) > 0
            for name in cls.collection_names
        )

    def execute(self, context):
        # Limpiar objetos en colecciones
        for name in self.collection_names:
            col = bpy.data.collections.get(name)
            if col:
                for obj in list(col.objects):
                    bpy.data.objects.remove(obj, do_unlink=True)
                self.report({'INFO'}, f"Objetos eliminados en {name}")
            else:
                self.report({'WARNING'}, f"La colección {name} no existe")

        # Limpiar datos huérfanos de forma segura
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


# ------------------------------------------------------------------------
#  NUEVO: lista de clases que exporta este módulo para __init__.py
# ------------------------------------------------------------------------

classes = (
    OBJECT_OT_clean_building_collections,
)
