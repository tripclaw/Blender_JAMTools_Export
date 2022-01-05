bl_info = {
    "name": "JAM Tools: Export Manager",
    "category": "Import-Export",
    "author": "Jason A Miller",
    "description": "An fbx export manager for collections",
    "version": (1, 0),
    "location": "View3D > Side Panel > JAM",
    "blender": (2, 80, 0),
    "tracker_url": "",
    "wiki_url": "" ,
}

import bpy
   
from . import jamexport
from . import jamexport_uilist
    
def register():    
    jamexport.register()
    jamexport_uilist.register()

def unregister():
    jamexport.unregister()
    jamexport_uilist.unregister()

if __name__ == "__main__":
    register()