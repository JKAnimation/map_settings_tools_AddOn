import bpy
import os

class OBJECT_OT_import_fbx_to_collections(bpy.types.Operator):
    bl_idname = "object.import_fbx_to_collections"
    bl_label = "Import FBX to Collections"
    bl_description = "Importa archivos FBX organizándolos en colecciones"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default='*.fbx', options={'HIDDEN'})
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        imported_objects = []

        for file in self.files:
            fbx_path = os.path.join(self.directory, file.name)
            filename_no_ext = os.path.splitext(file.name)[0]

            # Crear una colección nueva con el nombre del archivo
            new_collection = bpy.data.collections.new(name=filename_no_ext)
            context.scene.collection.children.link(new_collection)

            # Importar FBX
            bpy.ops.import_scene.fbx(filepath=fbx_path)

            # Detectar nuevos objetos importados
            current_import = []
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    current_import.append(obj)

                    # Hacer única la data si está compartida
                    if obj.data.users > 1:
                        obj.data = obj.data.copy()

                    # Reubicar en la nueva colección
                    for coll in obj.users_collection:
                        coll.objects.unlink(obj)
                    new_collection.objects.link(obj)

                    # Aplicar rotación y escala (mantener posición)
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    obj.select_set(False)

            imported_objects.extend(current_import)

        return {'FINISHED'}
