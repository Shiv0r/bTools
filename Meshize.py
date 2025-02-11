bl_info = {
    "name" : "Meshize",
    "author" : "Edward Agwi",
    "Version" : (1, 0),
    "blender" : (4, 2, 0),
    "location" : "View3d > Tool",
    "Warning" : "",
    "wiki_url" : "",
    "category"  : "Add Mesh",
    }


import bpy
import time
import mathutils
from bpy.types import Context


D = bpy.data
O = bpy.ops
T = bpy.types



class Tool_PT_Meshize(bpy.types.Panel):
    bl_label = "Meshize"
    bl_idname = "Tool_PT_MeshizeMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meshize"
    


    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        userInput_remesh = scene.userInput_remesh


        row = layout.row()
        row.label(text= "Get meshes from geo-nodes")
        row = layout.row()
        row.operator("operator.get_mesh")
        layout.separator()
        layout.separator()
        row = layout.row()
        row.label(text= "Finalize Meshes", icon="ERROR")
        row = layout.row()
        row.label(text= "Type the mesh names in the right text input")
        layout.prop(scene, "userInput_veg", text="Vegetation")
        layout.prop(scene, "userInput_flower", text="Flower")
        layout.prop(scene, "userInput_wall", text="Wall")
        layout.separator()
        row = layout.row()
        row.label(text= "Ivy Face Density")
        layout.prop(userInput_remesh, "targetFaces")
        row = layout.row()
        row.operator("operator.mesh_finalize")
    


class SetQuadriflowTargetFaces(bpy.types.PropertyGroup):
    targetFaces: bpy.props.IntProperty(
        name="Target Faces",
        description="Face density of the ivy mesh after remesh",
        default=10000,
        min=1000,
        max=40000,
    ) # type: ignore

     
      
class GetMesh(bpy.types.Operator):
    bl_label = "GetMesh"
    bl_idname = "operator.get_mesh"


    def execute(self, context,):

            #Get the active object and the obj operator
        C = context
        objSelect = C.view_layer.objects.active
        objOPS = O.object

        O.outliner.orphans_purge()

        if objSelect is not None:
             #Select the object
            objSelect.select_set(True)


            #duplicate the object and stay in the same position
        objOPS.duplicate_move()

            #convert the object to mesh to get rid of the modifers
        objOPS.convert(target= "MESH")
        
            #Get duplicated object
        objDupe = bpy.context.active_object
            #Deselect everything

        objOPS.select_all(action= "DESELECT")
            #Select duplicated object
        objDupe.select_set(True)

       
        
        if objDupe and objDupe.type == "MESH":
                #Get the Mesh data
            mesh = objDupe.data

                #Keep track of used mat
            usedMaterialIndicies = set()

                #Check which material indicies are used by the faces
            for poly in mesh.polygons:
                usedMaterialIndicies.add(poly.material_index)

                #Reverse iterate through material slots to dafely remove unused mat
            for slotIndex in range(len(objDupe.material_slots) -1, -1, -1):

                #If the material index is not in the usedMaterialIndicies remove it from the list
                if slotIndex not in usedMaterialIndicies:
                    objDupe.active_material_index = slotIndex
                    objOPS.material_slot_remove()
            print(f"Removed unsued mat from {objDupe.name}")
        else:
            print(f"Please select a mesh object.") 


        if objDupe and objDupe.type == "MESH":
                #Set mode to edit mode, seperate object via mat assigned, go back to object mode
            objOPS.mode_set(mode="EDIT")
            mesh = bpy.ops.mesh
            mesh.separate(type="MATERIAL")
            objOPS.mode_set(mode="OBJECT")
        else:
            print(f"Check if {objDupe} is a mesh type.")


            #Creates a collection
        collection = bpy.data.collections.new("BrickWall")
        bpy.context.scene.collection.children.link(collection)
        collTarget = bpy.context.scene.collection.children.get("BrickWall")


            #Get the selected objects
        objsSelect = bpy.context.selected_objects

            #Check if there are selected objects
        if objsSelect:
            for obj in objsSelect:
                    #Ensure the object type is appropriate (only MESH objects here)
                if obj.type == "MESH":
                        #Get the materials of the current object
                    mat = obj.data.materials
            
                        #Check if the object has materials
                    if mat:
                            #Get the first material name
                        matName = mat[0].name
                
                            #Rename the object to the material name
                        obj.name = matName
                        print(f"Renamed object '{obj.name}' to material name '{matName}'.")
                    else:
                        print(f"Object '{obj.name}' has no materials assigned.")


                        #Unlink objects from current collection
                    for coll in obj.users_collection:
                        coll.objects.unlink(obj)
                        #Link objects to the target collection
                    collTarget.objects.link(obj)

                else:
                    print("No objects selected.")             
                
        return{"FINISHED"}



class MeshFinalize(bpy.types.Operator):
    bl_label = "Finalize Mesh"
    bl_idname = "operator.mesh_finalize"


    def execute(self, context):
        scene = context.scene

        C = context
        objIvy = scene.userInput_veg
        objFlower = scene.userInput_flower
        objWall = scene.userInput_wall
        qfTargetFace = C.scene.userInput_remesh.targetFaces

        def scaleUV(scale=None, index=None, x=0.5, y=0.5):
                #get UV channel via Index
            uvLayer = C.object.data.uv_layers[index]

            if uvLayer is not None:
                scaleFactor = scale
                uvCenter = mathutils.Vector((x,y))

                for uvLoop in uvLayer.data:
                    uv = uvLoop.uv

                    uv -= uvCenter
                    uv *= scaleFactor
                    uv += uvCenter
                print(f"UV's have succesful scaled with the factor of {scale}, index = {index}")
            else:
                print(f"UV index not found. Create channels till the right index amount is reached.")
                    

        def transUV(x=None, y=None, index=None):
            uvLayer = bpy.context.active_object.data.uv_layers[index]

            if uvLayer is not None:
                transVector = (x, y)

                for uvLoop in uvLayer.data:
                    uv = uvLoop.uv

                    uv.x += transVector[0]
                    uv.y += transVector[1]
                
                print(f"UV index {index}, translated by {transVector}")
            else:
                print(f"UV index not found. Create channels till the right index amount is reached.")



        if objIvy and objIvy.type == "MESH":
            
            objIvyData = bpy.data.objects[getattr(objIvy, "name")]
            modifer = objIvyData.modifiers.new(name="Voxel Remesh", type="REMESH")
 
            O.object.select_all(action="DESELECT") 
            objIvy.select_set(True)
            C.view_layer.objects.active = objIvy
            modifer.mode = "VOXEL"
            modifer.voxel_size = 0.1
            modifer.adaptivity = 0.0
            O.object.modifier_apply(modifier="Voxel Remesh")

            O.object.quadriflow_remesh(target_faces=qfTargetFace)
            time.sleep(2.0)
            O.object.shade_smooth()

                #all faces expanding in UV 1-0
            O.object.mode_set(mode="EDIT")
            O.mesh.select_all()
            O.mesh.mark_seam(clear=False)
            O.uv.unwrap(method="ANGLE_BASED", margin=0.001)
            O.uv.reset()
            O.mesh.uv_texture_add()
            C.active_object.data.uv_layers[0].name = "Ivy"
            C.active_object.data.uv_layers[1].name = "Flower"
            

            O.object.mode_set(mode="OBJECT")
            scaleUV(scale=0.05, index=1)
            transUV(x= -0.45, y= -0.45, index=1)
            O.object.select_all(action="DESELECT")  
        else:
            None

        if objFlower and objFlower.type == "MESH":
            
            objSource = bpy.data.objects[getattr(objIvy, "name")]
            obj = bpy.data.objects[getattr(objFlower, "name")]
            modifer = obj.modifiers.new(name="Data Transfer", type="DATA_TRANSFER")

            objFlower.select_set(True)
            C.view_layer.objects.active = objFlower
            O.mesh.uv_texture_add()
            C.active_object.data.uv_layers[0].name = "Ivy"
            C.active_object.data.uv_layers[1].name = "Flower"
            scaleUV(scale=0.05, index=0)
            transUV(x= -0.45, y= -0.45, index=0)

            modifer.use_loop_data = True
            modifer.data_types_loops = {"CUSTOM_NORMAL"}
            modifer.loop_mapping = "POLYINTERP_NEAREST"
            modifer.object = objSource
            O.object.modifier_apply(modifier="Data Transfer")
            objIvy.select_set(True)
            objFlower.select_set(True)
            C.view_layer.objects.active = objIvy
            O.object.join()
            
                # removes Flower Material Slot
            if len(objIvy.data.materials) > 1:
                objIvy.data.materials.pop(index=1)
        else:
            None
        
        if objWall and objWall.type == "MESH":
            objWall.select_set(True)
            objIvy.select_set(True)
            C.view_layer.objects.active = objWall
            O.object.parent_set(type="OBJECT", keep_transform=True)

        else:
            None

        
        O.outliner.orphans_purge()            


        return {"FINISHED"}



def register(): 

    def regPointerProperty(propertyName, propName=None, propDesc=None, typeName=None):
           
            #make a dynamic variable which can be set into bpy.types.Scene 
        setattr(bpy.types.Scene, propertyName, bpy.props.PointerProperty(
            type=typeName if typeName else bpy.types.Object,
            name=propName if propName else propertyName,
            description=propDesc if propDesc else f"{propertyName}"
        ))

            



    bpy.utils.register_class(Tool_PT_Meshize)
    bpy.utils.register_class(GetMesh)
    bpy.utils.register_class(MeshFinalize)
    regPointerProperty("userInput_veg", "Vegetation", "Get the moss or ivy mesh")
    regPointerProperty("userInput_flower", "Flower", "Get the flower mesh")
    regPointerProperty("userInput_wall", "Wall", "Get the wall mesh")
    bpy.utils.register_class(SetQuadriflowTargetFaces)
    regPointerProperty("userInput_remesh", typeName=SetQuadriflowTargetFaces)
    



def unregister():    
    bpy.utils.unregister_class(Tool_PT_Meshize)
    bpy.utils.unregister_class(GetMesh)
    bpy.utils.unregister_class(MeshFinalize)
    del bpy.types.Scene.userInput_ivy
    del bpy.types.Scene.userInput_flower
    del bpy.types.Scene.userInput_brick
    bpy.utils.unregister_class(SetQuadriflowTargetFaces)
    del bpy.types.Scene.userInput_remesh

if __name__ == "__main__":
    register()

