import bpy
import os
import math


class OBJECT_OT_blocking_settings(bpy.types.Operator):
    bl_idname = "object.blocking_settings"
    bl_label = "Blocking Settings"
    bl_options = {'REGISTER', 'UNDO'}

    # -------------------------------------------------
    # POLL
    # -------------------------------------------------
    @classmethod
    def poll(cls, context):
        return "Blocking" in bpy.data.collections

    # -------------------------------------------------
    # EXECUTE
    # -------------------------------------------------
    def execute(self, context):

        addon_dir = os.path.dirname(__file__)
        blend_path = os.path.join(addon_dir, "Map_basics.blend")

        self.load_node_group(blend_path, "Internal rounder")
        self.load_node_group(blend_path, "Clean_Curves")
        self.load_node_group(blend_path, "Levels_Terrain")

        # -------------------------------------------------
        # RESET TERRAIN COLLECTION
        # -------------------------------------------------
        terrain_col = self.reset_terrain_collection()

        # -------------------------------------------------
        # BLOCKING
        # -------------------------------------------------
        if "Blocking" in bpy.data.collections:
            self.process_collection(
                collection=bpy.data.collections["Blocking"],
                final_obj_name="Insides_Base",
                final_data_name="Insides",
                terrain_collection=terrain_col
            )

        # -------------------------------------------------
        # LEVELS
        # -------------------------------------------------
        if "Levels" in bpy.data.collections:
            self.process_collection(
                collection=bpy.data.collections["Levels"],
                final_obj_name="RoadHelp",
                final_data_name="RoadMain",
                terrain_collection=terrain_col
            )

        # -------------------------------------------------
        # RESTORE ORIGINAL NAMES (NO .001)
        # -------------------------------------------------
        self.restore_backup_names(
            [
                bpy.data.collections.get("Blocking"),
                bpy.data.collections.get("Levels")
            ]
        )

        self.report({'INFO'}, "Blocking and Levels processed successfully")
        return {'FINISHED'}

    # ---------------------------------------------------------
    # CORE PIPELINE
    # ---------------------------------------------------------
    def process_collection(
        self,
        collection,
        final_obj_name,
        final_data_name,
        terrain_collection
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

            # -------- BACKUP --------
            backup = mesh.copy()
            backup.data = mesh.data.copy()
            backup["ORIGINAL_NAME"] = mesh.name
            collection.objects.link(backup)

            # Vertex Group BEFORE modifiers
            self.create_vertex_group_for_mesh(mesh)
            context.view_layer.update()

            self.add_decimate(mesh, 0.1)
            self.add_clean_curves(mesh)
            self.add_decimate(mesh, 3)
            self.add_decimate(mesh, 3)
            self.add_internal_rounder(mesh)
            self.add_clean_curves(mesh)
            self.add_weld(mesh)
            self.add_clean_curves(mesh)

            bpy.ops.object.convert(target='MESH')
            context.view_layer.update()

            # Safe re-creation
            self.create_vertex_group_for_mesh(mesh)

            processed.append(mesh)

        # ----------------------------------
        # JOIN
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
        # MOVE JOINED TO TERRAIN
        # ----------------------------------
        for col in joined.users_collection:
            col.objects.unlink(joined)
        terrain_collection.objects.link(joined)

        # ----------------------------------
        # LEVELS TERRAIN
        # ----------------------------------
        if final_obj_name == "RoadHelp":
            self.add_levels_terrain(joined)
            context.view_layer.update()

            bpy.ops.object.select_all(action='DESELECT')
            joined.select_set(True)
            context.view_layer.objects.active = joined
            bpy.ops.object.convert(target='MESH')

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        self.add_color_attribute(joined)

    # ---------------------------------------------------------
    # TERRAIN COLLECTION
    # ---------------------------------------------------------
    def reset_terrain_collection(self):
        if "Terrain" in bpy.data.collections:
            col = bpy.data.collections["Terrain"]
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

        terrain_col = bpy.data.collections.new("Terrain")
        bpy.context.scene.collection.children.link(terrain_col)
        return terrain_col

    # ---------------------------------------------------------
    # RESTORE NAMES
    # ---------------------------------------------------------
    def restore_backup_names(self, collections):
        for col in collections:
            if not col:
                continue
            for obj in col.objects:
                if "ORIGINAL_NAME" in obj:
                    obj.name = obj["ORIGINAL_NAME"]
                    del obj["ORIGINAL_NAME"]

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
