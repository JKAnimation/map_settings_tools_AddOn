import bpy
import os
import math


class OBJECT_OT_blocking_settings(bpy.types.Operator):
    bl_idname = "object.blocking_settings"
    bl_label = "Blocking Settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return not any(
            o.type == 'MESH' and o.name in {"Insides_Base", "Levels_Help"}
            for o in context.scene.objects
        )

    def execute(self, context):

        create_road_help = getattr(context.scene, "create_road_help", False)

        addon_dir = os.path.dirname(__file__)
        blend_path = os.path.join(addon_dir, "Map_basics.blend")

        self.load_node_group(blend_path, "Internal rounder")
        self.load_node_group(blend_path, "Clean_Curves")
        self.load_node_group(blend_path, "Levels_Terrain")

        # -------------------------------------------------
        # BLOCKING
        # -------------------------------------------------
        if "Blocking" in bpy.data.collections:
            self.process_collection(
                collection=bpy.data.collections["Blocking"],
                final_obj_name="Insides_Base",
                final_data_name="Insides",
                create_road_help=create_road_help
            )

        # -------------------------------------------------
        # LEVELS
        # -------------------------------------------------
        if "Levels" in bpy.data.collections:
            self.process_collection(
                collection=bpy.data.collections["Levels"],
                final_obj_name="RoadHelp",
                final_data_name="RoadMain",
                create_road_help=False
            )

        self.report({'INFO'}, "Blocking and Levels processed successfully")
        return {'FINISHED'}

    # ---------------------------------------------------------
    # CORE PIPELINE (REUTILIZABLE)
    # ---------------------------------------------------------

    def process_collection(
        self,
        collection,
        final_obj_name,
        final_data_name,
        create_road_help
    ):

        meshes = [o for o in collection.all_objects if o.type == 'MESH']
        if not meshes:
            return

        context = bpy.context
        processed = []

        # ----------------------------------
        # PROCESS EACH MESH
        # ----------------------------------
        for mesh in meshes:
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            context.view_layer.objects.active = mesh

            # Vertex Group BEFORE modifiers
            self.create_vertex_group_for_mesh(mesh)

            bpy.context.view_layer.update()

            self.add_decimate(mesh, 0.1)
            self.add_clean_curves(mesh)
            self.add_decimate(mesh, 3)
            self.add_decimate(mesh, 3)
            self.add_internal_rounder(mesh)
            self.add_clean_curves(mesh)
            self.add_weld(mesh)
            self.add_clean_curves(mesh)

            bpy.ops.object.convert(target='MESH')

            bpy.context.view_layer.update()

            # Safe re-creation (GN already collapsed)
            self.create_vertex_group_for_mesh(mesh)

            processed.append(mesh)

        # ----------------------------------
        # JOIN (SIEMPRE)
        # ----------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for m in processed:
            m.select_set(True)

        context.view_layer.objects.active = processed[0]
        bpy.ops.object.join()

        joined = context.view_layer.objects.active
        joined.name = final_obj_name
        joined.data.name = final_data_name

        # ----------------------------------
        # LEVELS TERRAIN (solo para Levels)
        # ----------------------------------
        if final_obj_name == "RoadHelp":
            self.add_levels_terrain(joined)

            bpy.context.view_layer.update()

            # Aplicar el GN (vertex groups ya no importan)
            bpy.ops.object.select_all(action='DESELECT')
            joined.select_set(True)
            context.view_layer.objects.active = joined
            bpy.ops.object.convert(target='MESH')


        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        self.add_color_attribute(joined)

        if create_road_help:
            self.add_road_help_plane(joined)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def load_node_group(self, blend_path, name):
        if name not in bpy.data.node_groups:
            bpy.ops.wm.append(
                filepath=os.path.join(blend_path, "NodeTree", name),
                directory=os.path.join(blend_path, "NodeTree"),
                filename=name
            )

    def add_decimate(self, mesh, angle):
        mod = mesh.modifiers.new("Decimate", 'DECIMATE')
        mod.decimate_type = 'DISSOLVE'
        mod.angle_limit = angle * math.pi / 180

    def add_clean_curves(self, mesh):
        mod = mesh.modifiers.new("Clean_Curves", 'NODES')
        mod.node_group = bpy.data.node_groups["Clean_Curves"]
        mod.node_group.use_fake_user = True

    def add_internal_rounder(self, mesh):
        mod = mesh.modifiers.new("Internal rounder", 'NODES')
        mod.node_group = bpy.data.node_groups["Internal rounder"]
        mod.node_group.use_fake_user = True

    def add_levels_terrain(self, mesh):
        mod = mesh.modifiers.new("Levels_Terrain", 'NODES')
        mod.node_group = bpy.data.node_groups["Levels_Terrain"]
        mod.node_group.use_fake_user = True

    def add_weld(self, mesh):
        mod = mesh.modifiers.new("Weld", 'WELD')
        mod.merge_threshold = 0.07

    def create_vertex_group_for_mesh(self, mesh):
        if mesh.name not in mesh.vertex_groups:
            vg = mesh.vertex_groups.new(name=mesh.name)
        else:
            vg = mesh.vertex_groups[mesh.name]

        indices = [v.index for v in mesh.data.vertices]
        vg.add(indices, 1.0, 'REPLACE')

    # ---------------------------------------------------------
    # EXTRAS
    # ---------------------------------------------------------

    def add_color_attribute(self, obj):
        mesh = obj.data
        if "Green_C" not in mesh.color_attributes:
            attr = mesh.color_attributes.new(
                name="Green_C",
                type='FLOAT_COLOR',
                domain='POINT'
            )
            for c in attr.data:
                c.color = (0, 1, 0, 1)

    def add_road_help_plane(self, mesh):

        min_x, min_y, _ = mesh.bound_box[0]
        max_x, max_y, _ = mesh.bound_box[6]

        margin = 24
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin

        size_x = max_x - min_x
        size_y = max_y - min_y

        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=(min_x + size_x / 2, min_y + size_y / 2, 0)
        )

        plane = bpy.context.object
        plane.name = "RoadHelp"
        plane.data.name = "RoadMain"
        plane.scale = (size_x, size_y, 1)

        bpy.ops.object.transform_apply(location=True, scale=True)
        self.add_color_attribute(plane)
