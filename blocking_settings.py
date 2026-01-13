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

        # --- CLEAN PREVIOUS RESULTS ---
        self.clear_work_collection()
        terrain_col = self.reset_terrain_collection()

        # --- BLOCKING ---
        if "Blocking" in bpy.data.collections:
            self.process_collection(
                source_collection=bpy.data.collections["Blocking"],
                final_obj_name="Insides_Base",
                final_data_name="Insides",
                terrain_collection=terrain_col
            )

        # --- LEVELS ---
        if "Levels" in bpy.data.collections:
            self.process_collection(
                source_collection=bpy.data.collections["Levels"],
                final_obj_name="RoadHelp",
                final_data_name="RoadMain",
                terrain_collection=terrain_col
            )

        # --- FINAL CLEAN ---
        self.clear_work_collection()

        self.report({'INFO'}, "Blocking and Levels processed successfully")
        return {'FINISHED'}

    # ---------------------------------------------------------
    # CORE PIPELINE
    # ---------------------------------------------------------
    def process_collection(
        self,
        source_collection,
        final_obj_name,
        final_data_name,
        terrain_collection
    ):

        self.remove_final_result(final_obj_name, final_data_name)

        context = bpy.context
        work_col = self.get_work_collection()
        processed = []

        meshes = [o for o in source_collection.all_objects if o.type == 'MESH']
        if not meshes:
            return

        # ----------------------------------
        # DUPLICATE & PROCESS EACH MESH
        # ----------------------------------
        for src in meshes:

            work = src.copy()
            work.data = src.data.copy()
            work_col.objects.link(work)

            bpy.ops.object.select_all(action='DESELECT')
            work.select_set(True)
            context.view_layer.objects.active = work

            # -------- FIRST VERTEX GROUP (FOR GN) --------
            self.create_vertex_group_named(work, src.name)
            context.view_layer.update()

            # -------- MODIFIERS --------
            self.add_decimate(work, 0.1)
            self.add_clean_curves(work)
            self.add_decimate(work, 3)
            self.add_decimate(work, 3)
            self.add_internal_rounder(work)
            self.add_clean_curves(work)
            self.add_weld(work)
            self.add_clean_curves(work)

            # -------- APPLY MODIFIERS --------
            bpy.ops.object.convert(target='MESH')
            context.view_layer.update()

            # 🔥 CRITICAL PART 🔥
            # Old groups are now invalid
            work.vertex_groups.clear()

            # -------- FINAL VERTEX GROUP (FOR JOIN) --------
            self.create_vertex_group_named(work, src.name)

            processed.append(work)

        # ----------------------------------
        # JOIN
        # ----------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for obj in processed:
            obj.select_set(True)

        context.view_layer.objects.active = processed[0]
        bpy.ops.object.join()

        joined = context.view_layer.objects.active
        joined.name = final_obj_name
        joined.data.name = final_data_name

        # ----------------------------------
        # MOVE TO TERRAIN
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
    # COLLECTION MANAGEMENT
    # ---------------------------------------------------------
    def get_work_collection(self):
        name = "__WORK_BLOCKING__"
        if name not in bpy.data.collections:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        return bpy.data.collections[name]

    def clear_work_collection(self):
        col = bpy.data.collections.get("__WORK_BLOCKING__")
        if not col:
            return
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    def reset_terrain_collection(self):
        if "Terrain" in bpy.data.collections:
            col = bpy.data.collections["Terrain"]
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col)

        terrain_col = bpy.data.collections.new("Terrain")
        bpy.context.scene.collection.children.link(terrain_col)
        return terrain_col

    def remove_final_result(self, obj_name, data_name):
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

        data = bpy.data.meshes.get(data_name)
        if data and data.users == 0:
            bpy.data.meshes.remove(data)

    # ---------------------------------------------------------
    # MODIFIERS & HELPERS
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

    def create_vertex_group_named(self, mesh, name):
        vg = mesh.vertex_groups.new(name=name)
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
