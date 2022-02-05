import bpy
import bmesh
from . walkers import bmesh_face_loop_walker


class MESH_OT_MultiFaceLoopSelect(bpy.types.Operator):
    bl_idname = "mesh.multi_faceloop_select"
    bl_label = "Select Multiple Face Loops"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description  = 'Select multiple faceloops by selecting faces. The selected faces determine the direction of the loops'

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return self.select_faceloops(context)

    def select_faceloops(self, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)

        selected_faces = {e for e in bm.faces if e.select}
        faces_to_deselect = set()
        change_loop_direction = False
        changed_loop_direction = False
        for selected_face in selected_faces:
            faces_to_select = set()

            loop = selected_face.loops[0] 
            try:
                for face in bmesh_face_loop_walker(loop.edge):
                    if face is None:
                        continue
                    bm_face = bm.faces[face]
                    
                    bm_face.select = True

                    if bm_face not in selected_faces:
                        faces_to_select.add(bm_face)
                        
                    if bm_face in selected_faces and bm_face != selected_face:
                        change_loop_direction = True
                        changed_loop_direction = True
                        faces_to_deselect.update(faces_to_select)
                        break
            except AttributeError:
                # We started on a boundary edge use the opposite edge on the face
                for face in bmesh_face_loop_walker(loop.link_loop_next.link_loop_next.edge):
                    if face is None:
                        continue
                    bm_face = bm.faces[face]
                    
                    bm_face.select = True

                    if bm_face not in selected_faces:
                        faces_to_select.add(bm_face)
                        
                    if bm_face in selected_faces and bm_face != selected_face:
                        change_loop_direction = True
                        changed_loop_direction = True
                        faces_to_deselect.update(faces_to_select)
                        break

            if change_loop_direction:
                loop = loop.link_loop_next
                try:
                    for face in bmesh_face_loop_walker(loop.edge):
                            if face is None:
                                continue
                            bm_face = bm.faces[face]
                            bm_face.select = True
                    change_loop_direction = False
                except AttributeError:
                    # We started on a boundary edge use the opposite edge on the face
                    for face in bmesh_face_loop_walker(loop.link_loop_next.link_loop_next.edge):
                            if face is None:
                                continue
                            bm_face = bm.faces[face]
                            bm_face.select = True
                    change_loop_direction = False

        if changed_loop_direction:
            for face in faces_to_deselect:
                face.select = False

        bmesh.update_edit_mesh(mesh, destructive=False)
        return {'FINISHED'}