bl_info = {
    "name": "JAM Tools: Export Manager",
    "category": "Mesh",
    "author": "JAM",
    "description": "A collection-based fbx export manager",
    "version": (0, 1),
    "location": "Side Panel",
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