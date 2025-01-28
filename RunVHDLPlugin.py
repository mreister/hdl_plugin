import sublime
import sublime_plugin
import subprocess
#import os 
from .vhdl_proc_lib import * 
import re
import json



class RunVhdlScriptCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if view is None:
            sublime.error_message("No active file.")
            return

        file_path = view.file_name()
        if not file_path or not file_path.endswith(".vhd"):
            sublime.error_message("This command can only be used with VHDL files.")
            return

        # Path to your Python script
        python_script = "vhdl_extract.py"

        try:
            # Run the Python script with the file as an argument
            port_data_generics_json = extract_vhdl_generics_and_ports(file_path)
            sublime.message_dialog(port_data_generics_json)
            vhdl_code = generate_vhdl_instantiation(port_data_generics_json)
            sublime.set_clipboard(vhdl_code)
            
            
        except Exception as e:
            sublime.error_message("An error occurred: " + str(e))