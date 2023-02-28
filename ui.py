from bpy.types import Panel
import bmesh
from . import report
import bpy

class View3DPrintPanel:
    bl_category = "D-Checker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}


class VIEW3D_PT_print3d_analyze(View3DPrintPanel, Panel):
    bl_label = "D-Checker"

    _type_to_icon = {
        bmesh.types.BMVert: 'VERTEXSEL',
        bmesh.types.BMEdge: 'EDGESEL',
        bmesh.types.BMFace: 'FACESEL',
    }

    def draw_report(self, context):
        layout = self.layout
        info = report.info()
        
        if info:
            is_edit = context.edit_object is not None

            layout.label(text="Result")
            box = layout.box()
            col = box.column()

            for i, (text, data) in enumerate(info):
                if is_edit and data and data[1]:
                    bm_type, _bm_array = data
                    col.operator("mesh.print3d_select_report", text=text, icon=self._type_to_icon[bm_type],).index = i
                else:
                    col.label(text=text)
        
    def draw(self, context):
        layout = self.layout

        layout.label(text="Checks")
        layout.operator("mesh.print3d_check_all", text="Check All")

        self.draw_report(context)



