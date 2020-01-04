bl_info = {
    "name": "JAM Tools",
    "category": "Mesh",
    "author": "JAM",
    "description": "export",
    "version": (0, 1),
    "location": "Side Panel",
    "blender": (2, 80, 0),
    "tracker_url": "",
    "wiki_url": "" ,
}

import bpy

#if "bpy" in locals():
    #import importlib
    #if "jamexport" in locals():
        #importlib.reload(jamexport)
#else:
    #from . import jamexport
    
from . import jamexport
    
def register():    
    jamexport.register()

def unregister():
    jamexport.unregister()

if __name__ == "__main__":
    register()