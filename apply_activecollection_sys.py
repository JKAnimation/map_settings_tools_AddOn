import bpy
from bpy.props import BoolProperty

class OBJECT_OT_apply_activecollection_sys(bpy.types.Operator):
    bl_idname = "object.apply_activecollection_sys"
    bl_label = "Split C-C"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convierte instancias en objetos reales de la colección activa en la colección objetivo"
    
    make_single_user: BoolProperty(
        name="Make Data Single",
        description="Make each mesh object single user before processing",
        default=False
    )
    
    split_geometry: BoolProperty(
        name="Split Geometry",
        description="Split only selected objects instead of the entire collection",
        default=False
    )

    @classmethod
    def poll(cls, context):
        layer_col = context.view_layer.active_layer_collection
        return layer_col and layer_col.collection.objects

    def execute(self, context):
        # Desactivar modificadores Realize
        disable_realize_modifiers()

        # Nombre de la colección donde se guardarán las instancias reales
        exp_collection_name = context.scene.split_collection.name

        # Crear o obtener la colección de destino
        if exp_collection_name not in bpy.data.collections:
            exp_collection = bpy.data.collections.new(exp_collection_name)
            context.scene.collection.children.link(exp_collection)
        else:
            exp_collection = bpy.data.collections[exp_collection_name]

        # Obtener colección activa
        active_collection = context.view_layer.active_layer_collection.collection
        
        # Aplicar Make Single User si está habilitado
        if self.make_single_user:
            if self.split_geometry and context.selected_objects:
                self.make_single_user_objects_list(context.selected_objects)
            else:
                self.make_single_user_objects(active_collection)
                
            # Si solo es split geometry, terminamos aquí
            if self.split_geometry:
                enable_realize_modifiers()
                self.report({'INFO'}, "Objetos seleccionados convertidos a single user")
                return {'FINISHED'}

        # Si no es solo split geometry, continuar con el proceso normal
        objects_to_process = context.selected_objects if (self.split_geometry and context.selected_objects) else active_collection.objects

        # Procesar cada objeto
        for obj in objects_to_process:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Convertir instancias a objetos reales
            bpy.ops.object.duplicates_make_real()

            # Objetos generados = seleccionados tras duplicates_make_real()
            generated_objects = context.selected_objects

            for new_obj in generated_objects:
                if not new_obj.name.startswith("_"):
                    # Si el objeto ya está en la colección de destino, no hacer nada
                    if new_obj.name not in exp_collection.objects:
                        exp_collection.objects.link(new_obj)
                        active_collection.objects.unlink(new_obj)
                        self.report({'INFO'}, f"Objeto {new_obj.name} movido a {exp_collection_name}")

            bpy.ops.object.select_all(action='DESELECT')

        # Reactivar modificadores Realize
        enable_realize_modifiers()

        self.report({'INFO'}, "Proceso completado correctamente.")
        return {'FINISHED'}
        
    def make_single_user_objects(self, collection):
        """Make each mesh object single user and apply transforms."""
        if not collection:
            print("Error: No hay una colección activa")
            return
            
        processed_count = 0
        print(f"Procesando colección: {collection.name}")
        
        # Deseleccionar todo primero
        bpy.ops.object.select_all(action='DESELECT')
        
        # Seleccionar todos los objetos MESH en la colección
        mesh_objects = [obj for obj in collection.objects if obj.type == 'MESH' and obj.data]
        
        for obj in mesh_objects:
            obj.select_set(True)
        
        if mesh_objects:
            # Hacer single user de los datos
            bpy.ops.object.make_single_user(
                type='SELECTED_OBJECTS', 
                object=True, 
                obdata=True, 
                material=False, 
                texture=False, 
                animation=False
            )
            
            # Resetear escala
            bpy.ops.object.scale_clear()
            
            print(f"  - Single user aplicado a {len(mesh_objects)} objetos")
            processed_count = len(mesh_objects)
            
            # Deseleccionar todo al final
            bpy.ops.object.select_all(action='DESELECT')
            
        print(f"Completado: {processed_count} objetos procesados en '{collection.name}'")
        return processed_count
        
    def make_single_user_objects_list(self, objects_list):
        """Make each mesh object in the list single user and apply transforms."""
        if not objects_list:
            return
            
        processed_count = 0
        print(f"Procesando {len(objects_list)} objetos seleccionados")
        
        # Deseleccionar todo primero
        bpy.ops.object.select_all(action='DESELECT')
        
        # Seleccionar solo los objetos MESH de la lista
        mesh_objects = [obj for obj in objects_list if obj.type == 'MESH' and obj.data]
        
        for obj in mesh_objects:
            obj.select_set(True)
        
        if mesh_objects:
            # Hacer single user de los datos
            bpy.ops.object.make_single_user(
                type='SELECTED_OBJECTS', 
                object=True, 
                obdata=True, 
                material=False, 
                texture=False, 
                animation=False
            )
            
            # Resetear escala
            bpy.ops.object.scale_clear()
            
            print(f"  - Single user aplicado a {len(mesh_objects)} objetos")
            processed_count = len(mesh_objects)
            
            # Deseleccionar todo al final
            bpy.ops.object.select_all(action='DESELECT')
            
        print(f"Completado: {processed_count} objetos procesados")
        return processed_count

def disable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = False
                print(f"[INFO] Realize desactivado en {obj.name}")

    bpy.context.view_layer.update()

def enable_realize_modifiers():
    active_collection = bpy.context.view_layer.active_layer_collection.collection

    for obj in active_collection.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Realize":
                mod.show_viewport = True
                print(f"[INFO] Realize activado en {obj.name}")

    bpy.context.view_layer.update()