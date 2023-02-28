import math

import bpy
from bpy.types import Operator
from bpy.props import (
    IntProperty,
    FloatProperty,
)
import bmesh

from . import report


def clean_float(value: float, precision: int = 0) -> str:

    text = f"{value:.{precision}f}"
    index = text.rfind(".")

    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail

    return text


def get_unit(unit_system: str, unit: str) -> tuple[float, str]:

    units = {
        "METRIC": {
            "KILOMETERS": (1000.0, "km"),
            "METERS": (1.0, "m"),
            "CENTIMETERS": (0.01, "cm"),
            "MILLIMETERS": (0.001, "mm"),
            "MICROMETERS": (0.000001, "µm"),
        },
        "IMPERIAL": {
            "MILES": (1609.344, "mi"),
            "FEET": (0.3048, "\'"),
            "INCHES": (0.0254, "\""),
            "THOU": (0.0000254, "thou"),
        },
    }

    try:
        return units[unit_system][unit]
    except KeyError:
        fallback_unit = "CENTIMETERS" if unit_system == "METRIC" else "INCHES"
        return units[unit_system][fallback_unit]

def execute_check(self, context):
    obj = context.active_object

    info = []
    self.main_check(obj, info)
    report.update(*info)

    multiple_obj_warning(self, context)

    return {'FINISHED'}

def multiple_obj_warning(self, context):
    if len(context.selected_objects) > 1:
        self.report({"INFO"}, "Multiple selected objects. Only the active one will be evaluated")

class MESH_OT_print3d_check_solid(Operator):
    bl_idname = "mesh.print3d_check_solid"
    bl_label = "3D-Print Check Solid"
    
    @staticmethod
    def main_check(obj, info):
        import array
        from . import mesh_helpers

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)

        edges_non_manifold = array.array('i', (i for i, ele in enumerate(bm.edges) if not ele.is_manifold))

        info.append((f"Non Manifold Edge: {len(edges_non_manifold)}", (bmesh.types.BMEdge, edges_non_manifold)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class MESH_OT_print3d_check_intersections(Operator):
    bl_idname = "mesh.print3d_check_intersect"
    bl_label = "3D-Print Check Intersections"
    
    @staticmethod
    def main_check(obj, info):
        from . import mesh_helpers

        faces_intersect = mesh_helpers.bmesh_check_self_intersect_object(obj)
        info.append((f"Intersect Face: {len(faces_intersect)}", (bmesh.types.BMFace, faces_intersect)))

    def execute(self, context):
        return execute_check(self, context)


class MESH_OT_print3d_check_degenerate(Operator):
    bl_idname = "mesh.print3d_check_degenerate"
    bl_label = "3D-Print Check Degenerate"
    
    @staticmethod
    def main_check(obj, info):
        import array
        from . import mesh_helpers

        scene = bpy.context.scene
        print_3d = scene.print_3d
        threshold = print_3d.threshold_zero

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)

        faces_zero = array.array('i', (i for i, ele in enumerate(bm.faces) if ele.calc_area() <= threshold))
        edges_zero = array.array('i', (i for i, ele in enumerate(bm.edges) if ele.calc_length() <= threshold))

        info.append((f"Zero Faces: {len(faces_zero)}", (bmesh.types.BMFace, faces_zero)))
        info.append((f"Zero Edges: {len(edges_zero)}", (bmesh.types.BMEdge, edges_zero)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class MESH_OT_print3d_check_distorted(Operator):
    bl_idname = "mesh.print3d_check_distort"
    bl_label = "3D-Print Check Distorted Faces"
    
    @staticmethod
    def main_check(obj, info):
        import array
        from . import mesh_helpers

        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_distort = print_3d.angle_distort

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=True, triangulate=False)
        bm.normal_update()

        faces_distort = array.array(
            'i',
            (i for i, ele in enumerate(bm.faces) if mesh_helpers.face_is_distorted(ele, angle_distort))
        )

        info.append((f"Non-Flat Faces: {len(faces_distort)}", (bmesh.types.BMFace, faces_distort)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class MESH_OT_print3d_check_thick(Operator):
    bl_idname = "mesh.print3d_check_thick"
    bl_label = "3D-Print Check Thickness"
    
    @staticmethod
    def main_check(obj, info):
        from . import mesh_helpers

        scene = bpy.context.scene
        print_3d = scene.print_3d

        faces_error = mesh_helpers.bmesh_check_thick_object(obj, print_3d.thickness_min)
        info.append((f"Thin Faces: {len(faces_error)}", (bmesh.types.BMFace, faces_error)))

    def execute(self, context):
        return execute_check(self, context)


class MESH_OT_print3d_check_sharp(Operator):
    bl_idname = "mesh.print3d_check_sharp"
    bl_label = "3D-Print Check Sharp"
    
    @staticmethod
    def main_check(obj, info):
        from . import mesh_helpers

        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_sharp = print_3d.angle_sharp

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=True, triangulate=False)
        bm.normal_update()

        edges_sharp = [
            ele.index for ele in bm.edges
            if ele.is_manifold and ele.calc_face_angle_signed() > angle_sharp
        ]

        info.append((f"Sharp Edge: {len(edges_sharp)}", (bmesh.types.BMEdge, edges_sharp)))
        bm.free()

    def execute(self, context):
        return execute_check(self, context)



class MESH_OT_print3d_check_all(Operator):
    bl_idname = "mesh.print3d_check_all"
    bl_label = "3D-Print Check All"

    check_cls = (
        MESH_OT_print3d_check_solid,
        MESH_OT_print3d_check_intersections,
        MESH_OT_print3d_check_degenerate,
        MESH_OT_print3d_check_distorted,
        MESH_OT_print3d_check_thick,
        MESH_OT_print3d_check_sharp,
    )

    def execute(self, context):
        obj = context.active_object

        info = []
        for cls in self.check_cls:
            cls.main_check(obj, info)

        report.update(*info)

        multiple_obj_warning(self, context)

        return {'FINISHED'}


class MESH_OT_print3d_select_report(Operator):
    bl_idname = "mesh.print3d_select_report"
    bl_label = "3D-Print Select Report"
    bl_options = {'INTERNAL'}

    index: IntProperty()

    _type_to_mode = {
        bmesh.types.BMVert: 'VERT',
        bmesh.types.BMEdge: 'EDGE',
        bmesh.types.BMFace: 'FACE',
    }

    _type_to_attr = {
        bmesh.types.BMVert: "verts",
        bmesh.types.BMEdge: "edges",
        bmesh.types.BMFace: "faces",
    }

    def execute(self, context):
        obj = context.edit_object
        info = report.info()
        _text, data = info[self.index]
        bm_type, bm_array = data

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type=self._type_to_mode[bm_type])

        bm = bmesh.from_edit_mesh(obj.data)
        elems = getattr(bm, MESH_OT_print3d_select_report._type_to_attr[bm_type])[:]

        try:
            for i in bm_array:
                elems[i].select_set(True)
        except:
            self.report({'WARNING'}, "Report is out of date, re-run check")

        return {'FINISHED'}


