bl_info = {
    "name": "Path Changer",
    "author": "Edward Agwi",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3d > Tool",
    "description": "Change the path in various locations after updating blender to a new version",
    "warning": "",
    "doc_url": "",
    "category": "Tool",
}

import bpy


class PathChanger(bpy.types.Panel):
    bl_label = "Path Changer"
    bl_idname = "Tool_PT_PathChangerMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    

    def draw(self, context):
        C = context
        layout = self.layout
        scene = C.scene


        row = layout.row()
        layout.prop(scene, "userInput_path", text= "Blender Version")
        row = layout.row()
        row.operator("operator.change_path")



class PathChangerOPS(bpy.types.Operator):
    bl_label = "Change Paths"
    bl_idname = "operator.change_path"

    def execute(self, context):
        C = context
        scene = C.scene
        D = bpy.data

        pathVersionLong = scene.userInput_path
        pathVersionShort = pathVersionLong[:3]



        nodeTreeWorld =  scene.world.node_tree
        imageNode = nodeTreeWorld.nodes.get("Environment Texture")
        nodeTreeComp = scene.node_tree



        if imageNode and imageNode.type == "TEX_ENVIRONMENT":

            newImageNodePath = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/{pathVersionShort}/datafiles/studiolights/world/paul_lobe_haus_1k.hdr"
            imageNode.image = D.images.load(newImageNodePath)
        else:
            print("Image Texture node not found")


        fileOutputNodeA = nodeTreeComp.nodes.get("File Output")
        fileOutputNodeB = nodeTreeComp.nodes.get("File Output.001")


        if fileOutputNodeA and fileOutputNodeA.type == "OUTPUT_FILE":
            fileOutputNodeA.base_path = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/portable/output/"
        else: print(f"File Output Node '{fileOutputNodeA}' could be not found")

        if fileOutputNodeB and fileOutputNodeB.type == "OUTPUT_FILE":
            fileOutputNodeB.base_path = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/portable/output/"
        else: print(f"File Output Node '{fileOutputNodeB}' could be not found")




        filePaths = C.preferences.filepaths


        filePaths.render_output_directory = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/portable/output/"
        filePaths.asset_libraries[0].path = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/portable/config/AssetBrowser/"
        filePaths.asset_libraries[3].path = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/{pathVersionShort}/datafiles/presets/PSA/"
        filePaths.script_directories[0].directory = f"C:/Program Files/Blender/blender-{pathVersionLong}-windows-x64/portable/config/Scripts/"
        bpy.ops.wm.save_userpref()

        return{"FINISHED"}
    





def register():

    blenderVersion = bpy.app.version_string

    def regStringProperty(propertyName: str, propName: str, propDesc: str, propDefault: str) -> None:
           
            #make a dynamic variable which can be set into bpy.types.Scene 
        setattr(bpy.types.Scene, propertyName, bpy.props.StringProperty(
            name=propName if propName else propertyName,
            description=propDesc if propDesc else f"{propertyName}",
            default= propDefault if propDefault else "",
        ))

    bpy.utils.register_class(PathChanger)
    bpy.utils.register_class(PathChangerOPS)
    regStringProperty("userInput_path", "Blender Version", "Type the full Blender Version into the Textfield. For example 4.3.0", blenderVersion)



def unregister():
      
    bpy.utils.unregister_class(PathChanger)
    bpy.utils.unregister_class(PathChangerOPS)
    del bpy.types.Scene.userInput_path



if __name__ == "__main__":
    register()