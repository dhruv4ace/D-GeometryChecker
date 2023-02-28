bl_info = {
    "name": "D-Checker",
    "author": "Dhruv Sharma",
    "blender": (3, 0, 0),
    "location": "3D View > Sidebar",
    "description": "Advance Geometry checker",
    "doc_url": "",
    "category": "D",
}


if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(operators)
    if "mesh_helpers" in locals():
        importlib.reload(mesh_helpers)
    if "export" in locals():
        importlib.reload(export)
else:
    import math

    import bpy
    from bpy.types import PropertyGroup
    from bpy.props import (
        FloatProperty,
        PointerProperty,
    )

    from . import (
        ui,
        operators,
    )


class SceneProperties(PropertyGroup):
    
    thickness_min: FloatProperty(
        name="Thickness",
        description="Minimum thickness",
        subtype='DISTANCE',
        default=0.001,  
        min=0.0,
        max=10.0,
    )
    threshold_zero: FloatProperty(
        name="Threshold",
        description="Limit for checking zero area/length",
        default=0.0001,
        precision=5,
        min=0.0,
        max=0.2,
    )
    angle_distort: FloatProperty(
        name="Angle",
        description="Limit for checking distorted faces",
        subtype='ANGLE',
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(180.0),
    )
    angle_sharp: FloatProperty(
        name="Angle",
        subtype='ANGLE',
        default=math.radians(160.0),
        min=0.0,
        max=math.radians(180.0),
    )
    angle_overhang: FloatProperty(
        name="Angle",
        subtype='ANGLE',
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(90.0),
    )


classes = (
    SceneProperties,

    ui.VIEW3D_PT_print3d_analyze,

    operators.MESH_OT_print3d_check_degenerate,
    operators.MESH_OT_print3d_check_distorted,
    operators.MESH_OT_print3d_check_solid,
    operators.MESH_OT_print3d_check_intersections,
    operators.MESH_OT_print3d_check_thick,
    operators.MESH_OT_print3d_check_sharp,
    operators.MESH_OT_print3d_check_all,
    
    operators.MESH_OT_print3d_select_report, 
)

 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.print_3d = PointerProperty(type=SceneProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.print_3d
