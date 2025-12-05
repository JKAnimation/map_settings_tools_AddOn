import bpy
import os

class OBJECT_OT_blocking_settings(bpy.types.Operator):
    bl_idname = "object.blocking_settings"
    bl_label = "Blocking Settings"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = (
        "Convierte las mesh de áreas de Figma a una mesh con curvas internas "
        "en Blender y agrega un plano de ayuda."
    )

    @classmethod
    def poll(cls, context):
        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name == "Insides_Base":
                return False
        return True

    def execute(self, context):
        if not hasattr(context.scene, 'create_road_help'):
            self.report({'ERROR'}, "Property 'create_road_help' not found in scene")
            return {'CANCELLED'}

        create_road_help = context.scene.create_road_help

        addon_directory = os.path.dirname(__file__)
        blend_file_path = os.path.join(addon_directory, "Map_basics.blend")

        if not os.path.isfile(blend_file_path):
            self.report({'ERROR'}, f"Blend file '{blend_file_path}' not found")
            return {'CANCELLED'}

        self.apply_modifiers_and_join_meshes(blend_file_path, create_road_help)
        
        return {'FINISHED'}

    def apply_modifiers_and_join_meshes(self, blend_file_path, create_road_help):
        self.report({'INFO'}, "Starting the script...")

        # Internal rounder
        if "Internal rounder" not in bpy.data.node_groups:
            self.report({'INFO'}, "Loading Internal rounder node group...")
            bpy.ops.wm.append(
                filepath=os.path.join(blend_file_path, "NodeTree", "Internal rounder"),
                directory=os.path.join(blend_file_path, "NodeTree"),
                filename="Internal rounder"
            )
        else:
            self.report({'INFO'}, "Internal rounder node group already loaded")

        # Clean Curves
        if "Clean_Curves" not in bpy.data.node_groups:
            self.report({'INFO'}, "Loading Clean_Curves node group...")
            bpy.ops.wm.append(
                filepath=os.path.join(blend_file_path, "NodeTree"),
                directory=os.path.join(blend_file_path, "NodeTree"),
                filename="Clean_Curves"
            )
        else:
            self.report({'INFO'}, "Clean_Curves node group already loaded")

        active_collection = bpy.context.view_layer.active_layer_collection.collection
        if not active_collection:
            self.report({'ERROR'}, "No active collection found")
            return

        if active_collection.name not in bpy.data.collections:
            self.report({'ERROR'}, f"Collection '{active_collection.name}' has been removed")
            return

        collection_name = active_collection.name
        self.report({'INFO'}, f"Selected collection: {collection_name}")

        context = bpy.context
        original_objects = context.view_layer.objects[:]

        meshes = [obj for obj in active_collection.all_objects if obj.type == 'MESH']
        if not meshes:
            self.report({'ERROR'}, "No meshes found in the selected collection")
            return

        # Procesar cada mesh
        for mesh in meshes:
            self.report({'INFO'}, f"Processing mesh: {mesh.name}")
            context.view_layer.objects.active = mesh
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            
            # ----------------------------
            # Tu lógica ORIGINAL intacta
            # ----------------------------

            # 1 — Decimate (pasada fina)
            decimate_modifier = mesh.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.decimate_type = 'DISSOLVE'
            decimate_modifier.angle_limit = .1 * (3.14159 / 180)
            self.report({'INFO'}, f"Added Decimate modifier to {mesh.name}")

            # 2 — Clean Curves
            clean_curves_modifier = mesh.modifiers.new(name="Clean_Curves", type='NODES')
            clean_curves_modifier.node_group = bpy.data.node_groups.get("Clean_Curves")
            clean_curves_modifier.node_group.use_fake_user = True
            self.report({'INFO'}, f"Added Clean_Curves GN modifier to {mesh.name}")
            
            # 3 — Internal Rounder
            internal_rounder_modifier = mesh.modifiers.new(name="Internal rounder", type='NODES')
            internal_rounder_modifier.node_group = bpy.data.node_groups.get("Internal rounder")
            internal_rounder_modifier.node_group.use_fake_user = True
            self.report({'INFO'}, f"Added Internal rounder GN modifier to {mesh.name}")

            # 4 — Decimate fuerte (1)
            decimate_modifier = mesh.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.decimate_type = 'DISSOLVE'
            decimate_modifier.angle_limit = 3 * (3.14159 / 180)
            self.report({'INFO'}, f"Added Decimate modifier to {mesh.name}")

            # 5 — Decimate fuerte (2)
            decimate_modifier = mesh.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.decimate_type = 'DISSOLVE'
            decimate_modifier.angle_limit = 3 * (3.14159 / 180)
            self.report({'INFO'}, f"Added Decimate modifier to {mesh.name}")

            # 6 — Weld
            weld_modifier = mesh.modifiers.new(name="Weld", type='WELD')
            weld_modifier.merge_threshold = 1
            self.report({'INFO'}, f"Added Weld modifier to {mesh.name}")

            # 7 — Clean curves final
            clean_curves_modifier = mesh.modifiers.new(name="Clean_Curves", type='NODES')
            clean_curves_modifier.node_group = bpy.data.node_groups.get("Clean_Curves")
            clean_curves_modifier.node_group.use_fake_user = True
            self.report({'INFO'}, f"Added Clean_Curves GN modifier to {mesh.name}")

            # 8 — Convertir
            bpy.ops.object.convert(target='MESH')
            self.report({'INFO'}, f"Applied all modifiers to {mesh.name}")

            bpy.context.view_layer.update()

            # 9 — Crear grupo de vértices
            self.create_vertex_group_for_mesh(mesh)

        bpy.context.view_layer.update()

        # Unir todo
        context.view_layer.objects.active = meshes[0]
        for mesh in meshes:
            mesh.select_set(True)
        bpy.ops.object.join()
        self.report({'INFO'}, "Joined all meshes")

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        joined_mesh = context.view_layer.objects.active
        joined_mesh.name = "Insides_Base"
        joined_mesh.data.name = "Insides"
        self.report({'INFO'}, f"Renamed joined mesh to {collection_name}")

        # Atributo de color
        self.add_color_attribute(joined_mesh)
        self.report({'INFO'}, f"Added 'Green_C' color attribute to {joined_mesh.name}")

        if create_road_help:
            self.add_road_help_plane(joined_mesh)

        bpy.ops.object.select_all(action='DESELECT')
        joined_mesh.select_set(True)
        context.view_layer.objects.active = joined_mesh
        self.report({'INFO'}, "Script finished successfully")

    def create_vertex_group_for_mesh(self, mesh):
        vertex_group = mesh.vertex_groups.new(name=mesh.name)
        vertex_indices = [v.index for v in mesh.data.vertices]
        vertex_group.add(vertex_indices, 1.0, 'REPLACE')
        self.report({'INFO'}, f"Vertex group created for mesh: {mesh.name}")

    def add_road_help_plane(self, mesh):
        min_x, min_y, min_z = mesh.bound_box[0]
        max_x, max_y, max_z = mesh.bound_box[6]

        min_x -= 24
        max_x += 24
        min_y -= 24
        max_y += 24

        x_size = max_x - min_x
        y_size = max_y - min_y

        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=(min_x + (x_size/2), min_y + (y_size/2), 0)
        )
        road_help_plane = bpy.context.object
        road_help_plane.name = "RoadHelp"
        road_help_plane.data.name = "RoadMain"

        road_help_plane.scale = (x_size, y_size, 1)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

        self.add_color_attribute(road_help_plane)

        if "UVCam" not in road_help_plane.data.uv_layers:
            road_help_plane.data.uv_layers.new(name="UVCam")

        if "UVMap" not in road_help_plane.data.uv_layers:
            road_help_plane.data.uv_layers.new(name="UVMap")

        if "UVCam" not in mesh.data.uv_layers:
            mesh.data.uv_layers.new(name="UVCam")

        if "UVMap" not in mesh.data.uv_layers:
            mesh.data.uv_layers.new(name="UVMap")

        self.report({'INFO'}, "Added RoadHelp plane")

    def add_color_attribute(self, obj):
        if obj.type == 'MESH':
            mesh = obj.data
            if "Green_C" not in mesh.color_attributes:
                color_attr = mesh.color_attributes.new(
                    name="Green_C",
                    type='FLOAT_COLOR',
                    domain='POINT'
                )
                for c in color_attr.data:
                    c.color = (0.0, 1.0, 0.0, 1.0)
                self.report({'INFO'}, f"Color attribute 'Green_C' created")
            else:
                self.report({'INFO'}, f"Color attribute 'Green_C' already exists")


# ---------------------------------------------------------
#  NUEVO: lista de clases que exporta este módulo
# ---------------------------------------------------------

classes = (
    OBJECT_OT_blocking_settings,
)
