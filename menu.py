import bpy

class VIEW3D_PT_map_setting_tools(bpy.types.Panel):
    bl_label = "Standard setting tools"
    bl_idname = "VIEW3D_PT_map_setting_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.standard_settings")
        split = layout.split(factor=0.7, align=True)
        col = split.column()
        col.prop(context.scene, "create_road_help")

class VIEW3D_PT_building__tools(bpy.types.Panel):
    bl_label = "Building Tools"
    bl_idname = "VIEW3D_PT_building_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        # Placeholder, manteniendo el panel
        layout.label(text="Panel activo para Blender 5.0")

class VIEW3D_PT_set_dressing_tools(bpy.types.Panel):
    bl_label = "Set dressing Tools"
    bl_idname = "VIEW3D_PT_set_dressing_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Panel activo para Blender 5.0")

class VIEW3D_PT_export_tools(bpy.types.Panel):
    bl_label = "Export Tools"
    bl_idname = "VIEW3D_PT_export_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Panel activo para Blender 5.0")

class VIEW3D_PT_procesar_mallas(bpy.types.Panel):
    bl_label = "Cutting tools"
    bl_idname = "VIEW3D_PT_procesar_mallas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Panel activo para Blender 5.0")

class VIEW3D_PT_collection_list_tools(bpy.types.Panel):
    bl_label = "Collection list generator"
    bl_idname = "VIEW3D_PT_collection_list_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Map Setting Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Panel activo para Blender 5.0")
