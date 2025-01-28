import sublime
import sublime_plugin
import subprocess
#import os 
#from vhdl_proc_lib import * 
import re
import json

def generate_vhdl_instantiation(json_data, instance_name="identifier_inst"):
    # Parse the JSON data
    
    data = json.loads(json_data)

    # Extract entity name, generics, and ports
    entity_name = data.get("entity_name", "Unnamed_Entity")
    generics = data.get("generics", [])
    ports = data.get("ports", [])

    # Generate VHDL instantiation
    instantiation_lines = []
    print(entity_name)
    sublime.message_dialog(entity_name)
    
    instantiation_lines.append("{0}_inst : entity work.{0}".format(entity_name))


    # Add generics if present
    if generics:
        instantiation_lines.append("generic map (")
        generic_mappings = []
        for generic in generics:
            generic_name = generic["name"]
            generic_mappings.append("    {0} => {0}",format(generic_name))
        instantiation_lines.append(",\n".join(generic_mappings))
        instantiation_lines.append(")")
    
    # Add ports
    instantiation_lines.append("port map (")
    port_mappings = []
    for port in ports:
        port_name = port["name"]
        port_type = port["data_type"]
        port_mappings.append("    {0} => {0} -- {1}".format(port_name,port_type))
    instantiation_lines.append(",\n".join(port_mappings))
    instantiation_lines.append(");")

    # Combine all lines into a single string
    vhdl_instantiation = "\n".join(instantiation_lines)
    
    #vhdl_instantiation = ""
    return vhdl_instantiation

def extract_vhdl_generics_and_ports(vhdl_file_path):
    # Read the VHDL file
    with open(vhdl_file_path, 'r') as file:
        vhdl_content = file.read()

    # Regex to extract entity section
    entity_pattern = r"entity\s+(\w+)\s+is.*?generic\s*\((.*?)\);.*?port\s*\((.*?)\);"  # Capture entity, generics, and ports
    entity_match = re.search(entity_pattern, vhdl_content, re.DOTALL | re.IGNORECASE)

    if not entity_match:
        return json.dumps({"error": "No entity found in the VHDL file."})

    entity_name = entity_match.group(1).strip()
    generic_content = entity_match.group(2)
    port_content = entity_match.group(3)

    # Regex to extract generic names and types
    generic_pattern = r"(\w+)\s*:\s*([^;]+);?"
    generics = re.findall(generic_pattern, generic_content, re.IGNORECASE)

    # Regex to extract port names, directions, and data types
    port_pattern = r"(\w+)\s*:\s*(in|out)\s+([^;]+);?"
    ports = re.findall(port_pattern, port_content, re.IGNORECASE)

    # Prepare JSON output
    generic_info = []
    for name, data_type in generics:
        generic_info.append({
            "name": name.strip(),
            "data_type": data_type.strip()
        })

    port_info = []
    for name, direction, data_type in ports:
        port_info.append({
            "name": name.strip(),
            "direction": direction.strip().lower(),
            "data_type": data_type.strip()
        })

    result = {
        "entity_name": entity_name,
        "generics": generic_info,
        "ports": port_info
    }

    return json.dumps(result, indent=4)

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
            vhdl_code = generate_vhdl_instantiation(port_data_generics_json)
            sublime.set_clipboard(vhdl_code)
            sublime.message_dialog("Text Copied to Clipboard")
            
        except Exception as e:
            sublime.error_message("An error occurred: " + str(e))