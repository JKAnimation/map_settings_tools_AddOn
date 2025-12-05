import bpy
import os

class OBJECT_OT_import_fbx_to_collections(bpy.types.Operator):
    bl_idname = "object.import_fbx_to_collections"
    bl_label = "Import FBX to Collections"
    bl_description = "Importa archivos FBX organizándolos en colecciones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import_path = context.scene.import_folder

        if not os.path.exists(import_path):
            self.report({'ERROR'}, "La carpeta seleccionada no existe")
            return {'CANCELLED'}

        fbx_files = [f for f in os.listdir(import_path) if f.lower().endswith('.fbx')]

        if not fbx_files:
            self.report({'WARNING'}, "No hay archivos FBX en la carpeta seleccionada")
            return {'CANCELLED'}

        for file in fbx_files:
            fbx_path = os.path.join(import_path, file)
            filename_no_ext = os.path.splitext(file)[0]

            # Crear una colección nueva con el nombre del archivo
            new_collection = bpy.data.collections.new(name=filename_no_ext)
            context.scene.collection.children.link(new_collection)

            # Importar FBX
            bpy.ops.import_scene.fbx(filepath=fbx_path)

            # Obtener objetos seleccionados tras la importación
            imported_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

            for obj in imported_objects:
                # Eliminar de colecciones anteriores
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                # Agregar a nueva colección
                new_collection.objects.link(obj)

        self.report({'INFO'}, f"{len(fbx_files)} archivos FBX importados correctamente")
        return {'FINISHED'}
    
    # ------------------------------------------------------------
# NUEVO: lista de clases que exporta este módulo
# ------------------------------------------------------------
classes = (
    OBJECT_OT_import_fbx_to_collections,
)

