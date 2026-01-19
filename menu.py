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
        layout.operator("object.blocking_settings")


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
    bl_label = "Set Dressing Tools"
    bl_idname = "VIEW3D_PT_set_dressing_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Main operator with clean button
        box = layout.box()
        row = box.row(align=True)
        row.operator("object.apply_activecollection_sys", text="Split Collection")
        row.operator("object.clean_setdressing_collections", text="", icon='TRASH')
        
        # Collection selection
        box.prop(scene, "split_collection", text="Target")
        
        # Options
        col = box.column(align=True)
        col.prop(scene, "apply_activecollection_make_data_single", text="Make Single User")
        col.prop(scene, "split_geometry", text="Process Only Selected")

        # Node tools section
        box = layout.box()
        box.label(text="Node Tools")
        
        # First row of node tools
        row = box.row(align=True)
        row.operator("object.load_landmark_plates", text="Land Facades", icon='HOME')
        row.operator("object.load_multisnap", text="Z Snap", icon='SNAP_ON')
        row.operator("object.load_edge_distribution", text="Edge Dist", icon='SEQ_LUMA_WAVEFORM')

        # Second row of node tools
        row = box.row(align=True)
        row.operator("object.area_distribution", text="Area Dist")
        row.operator("object.post_flags", text="Post Flags", icon='BOOKMARKS')
        row.operator("object.clean_nearest", text="Clean", icon='BRUSH_DATA')

        # Third row of node tools
        row = box.row(align=True)
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

class VIEW3D_PT_renamer_tools(bpy.types.Panel):
    bl_label = "Renamer Tool"
    bl_idname = "VIEW3D_PT_renamer_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 1. Populate Section
        box = layout.box()
        row = box.row(align=True)
        row.operator("renamer.populate", text="Update Selection", icon='FILE_REFRESH')
        row.operator("renamer.populate_collection", text="Add from Collection", icon='COLLECTION_NEW')
        box.prop(scene, "renamer_clear_on_populate", text="Clear List First")
        
        # 2. Objects List Section
        box = layout.box()
        box.label(text="Objects to Rename:")
        
        # List of objects
        if scene.renamer_items:
            box.template_list(
                "RENAMER_UL_items", "",
                scene, "renamer_items",
                scene, "renamer_active_index",
                rows=4
            )
            
            # List controls
            row = box.row(align=True)
            row.operator("renamer.move_item", text="", icon='TRIA_UP').direction = 'UP'
            row.operator("renamer.move_item", text="", icon='TRIA_DOWN').direction = 'DOWN'
            row.separator()
            row.operator("renamer.clear", text="Clear List", icon='TRASH')
        else:
            box.label(text="No objects in list", icon='INFO')
            box.operator("renamer.populate", text="Add Selected", icon='ADD')

        # 3. Renaming Tools Section
        layout.label(text="Prefix/Suffix Tools:", icon='SORTALPHA')
        
        # Prefix/Suffix in a single row
        row = layout.row(align=True)
        row.prop(scene, "renamer_prefix", text="")
        row.prop(scene, "renamer_suffix", text="")
        
        # Toggle options
        row = layout.row(align=True)
        row.prop(scene, "renamer_auto_underscore", 
                text="Auto _", 
                toggle=True, 
                icon='CON_TRANSLIKE')
        row.prop(scene, "renamer_preserve_base", 
                text="Keep Base", 
                toggle=True, 
                icon='LINKED')
        
        # Apply button
        layout.operator("renamer.apply_prefix_suffix", 
                      text="Apply Prefix/Suffix", 
                      icon='SORTALPHA')

        # Find & Replace section
        layout.separator()
        layout.label(text="Find & Replace:", icon='FIND_TEXT')
        
        # Find/Replace fields
        row = layout.row(align=True)
        row.prop(scene, "renamer_find", text="")
        row.prop(scene, "renamer_replace", text="")
        
        # Replace buttons
        row = layout.row(align=True)
        row.operator("renamer.find_replace", 
                   text="Replace All", 
                   icon='FIND_AND_REPLACE')
        row.operator("renamer.find_replace", 
                   text="Selected", 
                   icon='SELECT_SET').selected_only = True

        # Auto-numbering section
        layout.separator()
        layout.label(text="Auto-numbering:", icon='LINENUMBERS_ON')
        
        # Base name field
        layout.prop(scene, "renamer_base_name", text="")
        
        # Numbering options
        row = layout.row(align=True)
        row.label(text="Start:")
        row.prop(scene, "renamer_start_number", text="")
        row.separator()
        row.label(text="Digits:")
        row.prop(scene, "renamer_zero_padding", text="")
        
        # Auto-fill Button
        row = layout.row()
        op = row.operator("renamer.autofill", 
                         text="Auto-fill Names", 
                         icon='SORTALPHA')
        
        # Debug info (only in debug mode)
        if bpy.app.debug:
            debug = layout.column(align=True)
            debug.label(text="Debug:")
            debug.label(text=f"Base: '{scene.renamer_base_name}'")
            debug.label(text=f"Start: {scene.renamer_start_number}")
            debug.label(text=f"Digits: {scene.renamer_zero_padding}")
            debug.label(text=f"Items: {len(scene.renamer_items)}")

        # Apply All Changes
        layout.separator()
        row = layout.row()
        op = row.operator("renamer.execute", 
                         text="Apply All Changes", 
                         icon='CHECKMARK')
        op.apply_all = True