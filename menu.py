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
        layout.operator("object.clean_figma_curves", text="Clean Figma Curves")
        layout.operator("object.standard_settings")
        split = layout.split(factor=0.7)
        col = split.column()
        col.operator("object.blocking_settings")
        col = split.column()
        col.prop(context.scene, "create_road_help")

class VIEW3D_PT_building_tools(bpy.types.Panel):
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
        layout.operator("object.generate_csv_report", text="Generate Report")
        layout.prop(context.scene, "export_csv_path", text="Ruta Exportación")

class VIEW3D_PT_set_dressing_tools(bpy.types.Panel):
    bl_label = "Set dressing Tools"
    bl_idname = "VIEW3D_PT_set_dressing_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("object.apply_activecollection_sys")
        row.operator("object.clean_setdressing_collections")
        layout.prop(context.scene, "split_collection")

        layout.label(text="Node tools")
        row = layout.row(align=True)
        row.operator("object.load_landmark_plates", text="Land Facades", icon='HOME')
        row.operator("object.load_multisnap", text="Z Snap", icon='SNAP_ON')
        row.operator("object.load_edge_distribution", text="Edge Dist", icon='SEQ_LUMA_WAVEFORM')

        row = layout.row(align=True)
        row.operator("object.area_distribution", text="Area Dist")
        row.operator("object.post_flags", text="Post Flags", icon='BOOKMARKS')
        row.operator("object.clean_nearest", text="Clean Nearest", icon='BRUSH_DATA')

        row = layout.row(align=True)
        row.operator("object.road_paths", text="Road Paths", icon='TRACKING')
        row.operator("object.flat_borders", text="Flat Borders", icon='MOD_OUTLINE')

class VIEW3D_PT_export_tools(bpy.types.Panel):
    bl_label = "Export Tools"
    bl_idname = "VIEW3D_PT_export_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):
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
        props = getattr(context.scene, "procesar_coleccion_props", None)

        if props is not None:
            layout.prop(props, "usar_mesh_activa")
            if not getattr(props, "usar_mesh_activa", False):
                layout.prop_search(props, "coleccion_target", bpy.data, "collections", text="Colección")
            layout.operator("object.procesar_desde_coleccion", text="Procesar Geometría")
        else:
            layout.label(text="(Procesar mallas: props no disponibles)")

        layout.separator()

        layout.label(text="Actualizar FBX desde .blend:")
        actualizar_props = getattr(context.scene, "actualizar_fbx_props", None)
        if actualizar_props is not None:
            layout.prop(actualizar_props, "ruta_blend")
            layout.prop(actualizar_props, "nombre_coleccion")
            layout.operator("object.actualizar_coleccion_externa", icon="FILE_REFRESH")
        else:
            layout.label(text="(Actualizar FBX: props no disponibles)")

class VIEW3D_PT_collection_list_tools(bpy.types.Panel):
    bl_label = "Collection list generator"
    bl_idname = "VIEW3D_PT_collection_list_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):
        layout = self.layout

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
