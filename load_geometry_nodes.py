import bpy

# Operador para cargar Landmark_Plates
class OBJECT_OT_load_landmark_plates(bpy.types.Operator):
    bl_idname = "object.load_landmark_plates"
    bl_label = "Landmark Facades"
    bl_description = "Genera fachadas segùn un edge de geometrìa en el orden de la colecciòn seleccionada"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "Landmark_Plates"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

# Operador para cargar Multisnap
class OBJECT_OT_load_multisnap(bpy.types.Operator):
    bl_idname = "object.load_multisnap"
    bl_label = "Z Snap"
    bl_description = "Hace snap en el eje 'Z' de instancias o vertices sobre una mesh seleccionada "
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "Multisnap"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

# Operador para cargar Edge_distribution
class OBJECT_OT_load_edge_distribution(bpy.types.Operator):
    bl_idname = "object.load_edge_distribution"
    bl_label = "Edge Distribution"
    bl_description = "Distribuye objetos en la linea definida por los vertices de la mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "Edge_distribution"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}


# Operador para cargar Area_distribution
class OBJECT_OT_load_area_distribution(bpy.types.Operator):
    bl_idname = "object.area_distribution"
    bl_label = "Area Distribution"
    bl_description = "Distribuye objetos de una colecciòn en el area definida por la mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "Area_Distribution"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

# Operador para cargar PostWithFlags
class OBJECT_OT_PostsWithFlags(bpy.types.Operator):
    bl_idname = "object.post_flags"
    bl_label = "Post flagged"
    bl_description = "Distribuye banderines entre vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "PostsWithFlags"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

# Operador para cargar PostWithFlags
class OBJECT_OT_CleanNearest(bpy.types.Operator):
    bl_idname = "object.clean_nearest"
    bl_label = "Clean Nearest"
    bl_description = "Elimina instancias cercanas a una mesh definida"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "CleanNearest"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

# Operador para cargar Road Paths
class OBJECT_OT_RoadPaths(bpy.types.Operator):
    bl_idname = "object.road_paths"
    bl_label = "Road Paths"
    bl_description = "Crea caminos basados en una mesh low"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "Road Paths"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups.append(node_group_name)
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}

class OBJECT_OT_FlatBorders(bpy.types.Operator):
    bl_idname = "object.flat_borders"
    bl_label = "Flat Borders"
    bl_description = "Crea caminos basados en una mesh low"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group_name = "FlatBorders"
        node_group_path = "I:/Unidades compartidas/EDITABLES ALPHAVERSE/TOOLS/BlenderScripts/addons/map_settings_tools_AddOn/Map_basics.blend"

        # Obtener el objeto activo
        obj = context.object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No hay un objeto seleccionado o el objeto no es de tipo Mesh")
            return {'CANCELLED'}
        
        # Cargar el archivo .blend que contiene el grupo de nodos
        self.report({'INFO'}, "Cargando archivo .blend...")
        with bpy.data.libraries.load(node_group_path, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]
                self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' cargado.")
            else:
                self.report({'ERROR'}, f"El grupo de nodos '{node_group_name}' no se encontró en el archivo.")
                return {'CANCELLED'}
        
        # Verificar si ya hay un modificador de nodos
        existing_modifier = next((mod for mod in obj.modifiers if mod.type == 'NODES'), None)
        if existing_modifier:
            modifier = existing_modifier
        else:
            modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
        
        # Asignar el Geometry Node al objeto seleccionado
        modifier.node_group = bpy.data.node_groups[node_group_name]
        
        self.report({'INFO'}, f"Grupo de nodos '{node_group_name}' asignado a {obj.name}.")
        return {'FINISHED'}



