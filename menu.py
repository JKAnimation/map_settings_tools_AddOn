import bpy

class VIEW3D_PT_map_setting_tools(bpy.types.Panel):
    bl_label = "Standard setting tools"
    bl_idname = "VIEW3D_PT_map_setting_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout

        # Opciones originales
        layout.operator("object.clean_figma_curves", text="Clean Figma Curves")  # Nuevo botón
        layout.operator("object.standard_settings")
        split = layout.split(factor=0.7)
        col = split.column()
        col.operator("object.blocking_settings")
        col = split.column()
        col.prop(context.scene, "create_road_help")  # Añadimos la propiedad al panel

class VIEW3D_PT_building__tools(bpy.types.Panel):
    bl_label = "Building Tools"
    bl_idname = "VIEW3D_PT_building_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("object.apply_fullbuilding_sys")
        row.operator("object.clean_building_collections")
        layout.operator("object.update_fullbuilding_sys_inputs")
        layout.operator("object.rename_plates")
        layout.prop(context.scene, "entrances_collection")
        layout.operator("object.generate_csv_report", text="Generate Report")  # Nuevo botón
        layout.prop(context.scene, "export_csv_path", text="Ruta Exportación")





class VIEW3D_PT_export_tools(bpy.types.Panel):
    bl_label = "Export Tools"
    bl_idname = "VIEW3D_PT_export_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):  # Añadir la función draw
        layout = self.layout

        layout.prop(context.scene, "export_folder")
        layout.operator("object.export_fbx", text="Export Collection FBX")
        layout.operator("object.buildings_export_fbx", text="Buildings Export FBX")
        layout.operator("object.import_fbx_to_collections", icon="IMPORT")





class VIEW3D_PT_procesar_mallas(bpy.types.Panel):
    bl_label = "Cutting tools"
    bl_idname = "VIEW3D_PT_procesar_mallas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.procesar_coleccion_props

        layout.prop(props, "usar_mesh_activa")
        if not props.usar_mesh_activa:
            layout.prop_search(props, "coleccion_target", bpy.data, "collections", text="Colección")
        layout.operator("object.procesar_desde_coleccion", text="Procesar Geometría")


        layout.separator()


        layout.label(text="Actualizar FBX desde .blend:")
        layout.prop(context.scene.actualizar_fbx_props, "ruta_blend")
        layout.prop(context.scene.actualizar_fbx_props, "nombre_coleccion")
        layout.operator("object.actualizar_coleccion_externa", icon="FILE_REFRESH")


class VIEW3D_PT_collection_list_tools(bpy.types.Panel):
    bl_label = "Collection list generator"
    bl_idname = "VIEW3D_PT_collection_list_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):  # Añadir la función draw
        layout = self.layout

        # Nuevo Layout - Ordenar y Duplicar Objetos
        layout.label(text="Collection List")
        split = layout.split(factor=0.7)
        col = split.column()
        col.operator("object.add_to_list", text="Add Object")
        col.operator("object.remove_from_list", text="Remove Object")
        col = split.column()
        col.operator("object.move_item", text="Move Up").direction = 'UP'
        col.operator("object.move_item", text="Move Down").direction = 'DOWN'
        
        layout.template_list("OBJECT_UL_custom_list", "", context.scene, "my_objects", context.scene, "my_objects_index")
        layout.operator("object.apply_order", text="Apply Order and Duplicate")


