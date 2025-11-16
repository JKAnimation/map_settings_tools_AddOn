import bpy

class OBJECT_OT_clean_setdressing_collections(bpy.types.Operator):
    bl_idname = "object.clean_setdressing_collections"
    bl_label = "Clean Set Dressing Collections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Elimina todos los objetos en las colecciones para exportar y limpia los datos huérfanos"

    @classmethod
    def poll(cls, context):
        # Verificar si la colección activa tiene objetos
        return context.view_layer.active_layer_collection.collection.objects

    def execute(self, context):

        collection = context.scene.split_collection
        if collection is not None:
            # Iterar sobre los objetos en la colección y eliminarlos
            for obj in collection.objects:
                if obj.name.startswith("_") == False:
                    bpy.data.objects.remove(obj, do_unlink=True)
            self.report({'INFO'}, f"Objetos eliminados en la colección {collection.name}")
        else:
            self.report({'WARNING'}, f"La colección {collection.name} no existe")

        # Limpieza de datos huérfanos
        # Buscar y eliminar datos no utilizados manualmente
        def remove_unused_data(data_collection):
            for data_block in data_collection:
                if not data_block.users:
                    data_collection.remove(data_block)

        # Limpiar los datos huérfanos en diferentes tipos de datos
        remove_unused_data(bpy.data.meshes)
        remove_unused_data(bpy.data.materials)
        remove_unused_data(bpy.data.textures)
        remove_unused_data(bpy.data.lights)
        remove_unused_data(bpy.data.cameras)
        remove_unused_data(bpy.data.curves)
        remove_unused_data(bpy.data.images)
        remove_unused_data(bpy.data.node_groups)
        remove_unused_data(bpy.data.particles)
        remove_unused_data(bpy.data.speakers)

        self.report({'INFO'}, "Data limpia de objetos no utilizados.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_clean_setdressing_collections)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_clean_setdressing_collections)

if __name__ == "__main__":
    register()
