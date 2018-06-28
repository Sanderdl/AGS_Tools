bl_info = {
    "name": "AGS Blender tools",
    "description": "Blender add-on to render sprites to use in Adventure Game Studio",
    "author": "SanderDL",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "3D View > Tools",
    "warning": "The script currently has no checks for duplicate or missing objects.",
    "wiki_url": "https://github.com/Sanderdl/AGS_Tools",
    "tracker_url": "https://github.com/Sanderdl/AGS_Tools/issues",
    "category": "Development"
}

import bpy
import math

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    properties
# ------------------------------------------------------------------------

class RenderSettings(PropertyGroup):

    sidesEnum = EnumProperty(
        name="Sides:",
        description="Number of sides to render",
        items=[ ("4", "4 sides", ""),
                ("8", "8 sides", "")
               ]
        )
        
    path = StringProperty(
        name="",
        description="Folder to save sprites",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')
        
    cameraTarget = StringProperty(
        name="",
        description="Object the camera uses to rotate around the subject",
        default="",
        maxlen=200)

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class AgsRenderOperator(bpy.types.Operator):
    bl_idname = "ags.render"
    bl_label = "Render sprites"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        sides = int(mytool.sidesEnum)
        rotationAngle = 360.0 /sides
        rotDummy = scene.objects[mytool.cameraTarget]
        
        scene.render.alpha_mode = "TRANSPARENT"
        
                   
        for i in range(1, sides + 1):
            
            scene.render.filepath = mytool.path + "side" + str(i) + "_"
            
            bpy.ops.render.render( write_still=True, animation=True )
                       
            rotDummy.rotation_euler = (0,0,math.radians(rotationAngle * i))
            print("side:", i)
            

        rotDummy.rotation_euler = (0,0,0)
        
        return {'FINISHED'}
    
class SetupSceneOperator(bpy.types.Operator):
    bl_idname = "ags.setup"
    bl_label = "Setup Scene"
    
    def execute(self, context):
        
        scene = context.scene
        mytool = scene.my_tool
        
        cam = bpy.data.cameras.new("Camera")                              
        cam_object = bpy.data.objects.new(name="Camera", object_data=cam)
        cam_object.location = (0, -10, 4.5)
        cam_object.rotation_mode = "XYZ"     
        cam_object.rotation_euler = (math.radians(75), 0, 0)
                          
        rotDummy = bpy.data.objects.new( "RotationDummy", None )
        rotDummy.empty_draw_type = 'CUBE'
        rotDummy.location = (0, 0, 1)                          
                         
        light = bpy.data.lamps.new(name="sun", type='SUN')                              
        light.shadow_method = "RAY_SHADOW"
        lamp_object = bpy.data.objects.new(name="sun", object_data=light)
        lamp_object.location = (0, 0, 10)
        
        shadowMat = bpy.data.materials.new("ShadowMaterial")
        shadowMat.use_transparency = True
        shadowMat.alpha = 0.4
        shadowMat.use_only_shadow = True
        
        bpy.ops.mesh.primitive_plane_add(radius=4)
        shadowPlane = scene.objects.active
        shadowPlane.name = "ShadowPlane"
        shadowPlane.data.materials.append(shadowMat)
              
        scene.objects.link(lamp_object)
        scene.objects.link(rotDummy)
        scene.objects.link(cam_object)
        
        cam_object.parent = rotDummy
        crc = cam_object.constraints.new("TRACK_TO")
        crc.target = rotDummy
        crc.track_axis = "TRACK_NEGATIVE_Z"
                        
        return {'FINISHED'}    

# ------------------------------------------------------------------------
#    menus
# ------------------------------------------------------------------------

class BasicMenu(bpy.types.Menu):
    bl_idname = "ags.setup.menu"
    bl_label = "Setup"

    def draw(self, context):
        layout = self.layout

        layout.operator("ags.setup", text="Setup Renderscene")

# ------------------------------------------------------------------------
#    Draw tools in panel
# ------------------------------------------------------------------------

class AgsRenderPanel(Panel):
    bl_idname = "AGS_render_panel"
    bl_label = "AGS rendering"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "Tools"
    bl_context = "objectmode"   

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "sidesEnum", text="Sides")
        layout.prop(mytool, "path", text="Path")
        layout.prop_search(mytool, "cameraTarget", scene, "objects", text="Target")
        
        layout.operator("ags.render", text="Render sprites")
        
        
class AgsSetupPanel(Panel):
    bl_idname = "AGS_setup_panel"
    bl_label = "AGS setup"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "Tools"
    bl_context = "objectmode"   

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.menu("ags.setup.menu", text="Setup menu")        

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=RenderSettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()