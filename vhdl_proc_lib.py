import re
import json 
import sublime
import sublime_plugin

def generate_vhdl_instantiation(json_data, instance_name="identifier_inst"):
    # Parse the JSON data
    
    data = json.loads(json_data)

    # Extract entity name, generics, and ports
    entity_name = data.get("entity_name", "Unnamed_Entity")
    generics = data.get("generics", [])
    ports = data.get("ports", [])

    # Generate VHDL instantiation
    instantiation_lines = []

    sublime.message_dialog(entity_name)
    
    instantiation_lines.append("{0}_inst : entity work.{0}".format(entity_name))


    # Add generics if present
    if generics:
        instantiation_lines.append("generic map (")
        generic_mappings = []
        for generic in generics:
            generic_name = generic["name"]
            generic_mappings.append("    {0} => {0}".format(generic_name))
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

    # Regex to extract entity name
    entity_pattern = r"entity\s+(\w+)\s+is"
    entity_match = re.search(entity_pattern, vhdl_content, re.IGNORECASE)

    if not entity_match:
        return json.dumps({"error": "No entity found in the VHDL file."})

    entity_name = entity_match.group(1).strip()

    # Regex to extract generics block if present
    generic_pattern = r"generic\s*\((.*?)\);"
    generic_match = re.search(generic_pattern, vhdl_content, re.DOTALL | re.IGNORECASE)
    generic_content = generic_match.group(1) if generic_match else ""

    # Regex to extract ports block if present
    port_pattern = r"port\s*\((.*?)\);"
    port_match = re.search(port_pattern, vhdl_content, re.DOTALL | re.IGNORECASE)
    port_content = port_match.group(1) if port_match else ""

    # Extract generics
    generic_info = []
    if generic_content:
        generic_item_pattern = r"(\w+)\s*:\s*([^;]+);?"
        generics = re.findall(generic_item_pattern, generic_content, re.IGNORECASE)
        for name, data_type in generics:
            generic_info.append({
                "name": name.strip(),
                "data_type": data_type.strip()
            })

    # Extract ports
    port_info = []
    if port_content:
        port_item_pattern = r"(\w+)\s*:\s*(in|out)\s+([^;]+);?"
        ports = re.findall(port_item_pattern, port_content, re.IGNORECASE)
        for name, direction, data_type in ports:
            port_info.append({
                "name": name.strip(),
                "direction": direction.strip().lower(),
                "data_type": data_type.strip()
            })

    # Prepare JSON output
    result = {
        "entity_name": entity_name,
        "generics": generic_info,
        "ports": port_info
    }

    return json.dumps(result, indent=4)
