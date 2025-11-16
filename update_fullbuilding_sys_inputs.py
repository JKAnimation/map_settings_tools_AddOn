import bpy

class OBJECT_OT_update_fullbuilding_sys_inputs(bpy.types.Operator):
    bl_idname = "object.update_fullbuilding_sys_inputs"
    bl_label = "Update FullBuilding Sys Inputs"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description= "Actualiza los valores de todos los FullBuildingSys, según el objeto seleccionado"


    @classmethod
    def poll(cls, context):
        # Verifica si hay un objeto activo
        if context.object is None:
            return False
        
        # Verifica si el objeto tiene modificadores
        if not context.object.modifiers:
            return False

        # Verifica si el objeto tiene un modificador llamado "FullBuildings_Sys"
        for mod in context.object.modifiers:
            if mod.name == "FullBuildings_Sys":
                return True
        
        return False


    def execute(self, context):
        selected_obj = context.object
        
        if selected_obj is None or "FullBuildings_Sys" not in selected_obj.modifiers:
            self.report({'ERROR'}, "El objeto seleccionado no tiene el modificador 'FullBuildings_Sys'.")
            return {'CANCELLED'}
        
        # Obtener los valores del modificador del objeto seleccionado
        modifier_values = {
            "Socket_3": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_3"),
            "Socket_4": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_4"),
            "Socket_7": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_7"),
            "Socket_8": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_8"),
            "Socket_9": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_9"),
            "Socket_10": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_10"),
            "Socket_18": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_18"),
            "Socket_19": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_19"),
            "Socket_20": selected_obj.modifiers["FullBuildings_Sys"].get("Socket_20")
            
        }
        
        # Actualizar los inputs en otros objetos que tienen el mismo modificador
        for obj in bpy.data.objects:
            if "FullBuildings_Sys" in obj.modifiers:
                modifier = obj.modifiers["FullBuildings_Sys"]
                for key, value in modifier_values.items():
                    if value is not None:
                        modifier[key] = value
                    else:
                        self.report({'WARNING'}, f"Input '{key}' no encontrado en el objeto seleccionado.")
                        return {'CANCELLED'}
        
        # Forzar la actualización de la vista
        bpy.context.view_layer.update()

        self.report({'INFO'}, "Inputs actualizados correctamente.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_update_fullbuilding_sys_inputs)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_update_fullbuilding_sys_inputs)

if __name__ == "__main__":
    register()
