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
            o.type == 'MESH' and o.name == "Insides_Base"
            for o in context.scene.objects
        )

    def execute(self, context):

        create_road_help = getattr(context.scene, "create_road_help", False)

        addon_dir = os.path.dirname(__file__)
        blend_path = os.path.join(addon_dir, "Map_basics.blend")

        self.load_node_group(blend_path, "Internal rounder")
        self.load_node_group(blend_path, "Clean_Curves")

        collection = context.view_layer.active_layer_collection.collection
        meshes = [o for o in collection.all_objects if o.type == 'MESH']

        if not meshes:
            self.report({'ERROR'}, "No meshes found")
            return {'CANCELLED'}

        # -------------------------------------------------
        # PROCESS EACH MESH
        # -------------------------------------------------

        for mesh in meshes:
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            context.view_layer.objects.active = mesh

            # ✅ Vertex group BEFORE modifiers
            self.create_vertex_group_for_mesh(mesh)

            self.add_decimate(mesh, 0.1)
            self.add_clean_curves(mesh)
            self.add_decimate(mesh, 3)
            self.add_decimate(mesh, 3)

            self.add_internal_rounder(mesh)
            self.add_clean_curves(mesh)

            self.add_weld(mesh)

            bpy.ops.object.convert(target='MESH')
            bpy.context.view_layer.update()

            # (opcional pero seguro)
            self.create_vertex_group_for_mesh(mesh)

        # -------------------------------------------------
        # JOIN
        # -------------------------------------------------

        bpy.ops.object.select_all(action='DESELECT')
        for m in meshes:
            m.select_set(True)

        context.view_layer.objects.active = meshes[0]
        bpy.ops.object.join()

        joined = context.view_layer.objects.active
        joined.name = "Insides_Base"
        joined.data.name = "Insides"

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        self.add_color_attribute(joined)

        if create_road_help:
            self.add_road_help_plane(joined)

        self.report({'INFO'}, "Blocking Settings finished correctly")
        return {'FINISHED'}

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------

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

    def add_internal_rounder(self, mesh):
        mod = mesh.modifiers.new("Internal rounder", 'NODES')
        mod.node_group = bpy.data.node_groups["Internal rounder"]

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

    # -------------------------------------------------
    # EXTRAS
    # -------------------------------------------------

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
        plane.scale = (size_x, size_y, 1)

        bpy.ops.object.transform_apply(location=True, scale=True)
        self.add_color_attribute(plane)
