# linux_cadtrace_Freecad_plugin

Plugin for tracing images for Freecad

Requirements 

FreeCad Appimage

sudo apt install potrace imagemagick

opencv-python ezdxf pillow svgpathtools   should be installed by the macro itself

Place the files into: /your_home_directory/.local/share/FreeCAD/Macro/ then run the CadTraceMacro.FCMacro file.

The FreeCad macro installs the dependencies, then it invokes the image open dialog, then it traces the image into dxf file, after that it invokes dxf import dialog into a new document with the traced image.

Tested with Freecad 1.0.0

