import plantuml
import requests
import json
import yaml
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagramGenerator:
    def __init__(self, plantuml_url='http://www.plantuml.com/plantuml/png/'):
        self.pu = plantuml.PlantUML(url=plantuml_url)

    def generate_diagram(self, json_data, diagram_type):
        logger.debug(f"Generating diagram of type: {diagram_type}")
        logger.debug(f"Input JSON data: {json.dumps(json_data, indent=2)}")
        try:
            plantuml_code = self._generate_plantuml_code(json_data, diagram_type)
            logger.debug(f"Generated PlantUML code:\n{plantuml_code}")
            return self._render_diagram(plantuml_code, diagram_type)
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            raise



    def _generate_plantuml_code(self, json_data, diagram_type):
        if diagram_type == "class":
            return self._generate_class_diagram(json_data)
        elif diagram_type == "sequence":
            return self._generate_sequence_diagram(json_data)
        elif diagram_type == "usecase":
            return self._generate_usecase_diagram(json_data)
        elif diagram_type == "activity":
            return self._generate_activity_diagram(json_data)
        elif diagram_type == "component":
            return self._generate_component_diagram(json_data)
        elif diagram_type == "state":
            return self._generate_state_diagram(json_data)
        elif diagram_type == "object":
            return self._generate_object_diagram(json_data)
        elif diagram_type == "deployment":
            return self._generate_deployment_diagram(json_data)
        elif diagram_type == "timing":
            return self._generate_timing_diagram(json_data)
        elif diagram_type == "mindmap":
            return self._generate_mindmap(json_data)
        elif diagram_type == "json":
            return self._generate_json_diagram(json_data)
        elif diagram_type == "yaml":
            return self._generate_yaml_diagram(json_data)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

    def _generate_class_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for class_name, class_info in json_data['classes'].items():
            plantuml_code += f"class {class_name} {{\n"
            for attr in class_info.get('attributes', []):
                plantuml_code += f"  {attr}\n"
            for method in class_info.get('methods', []):
                plantuml_code += f"  {method}\n"
            plantuml_code += "}\n"
        for relationship in json_data.get('relationships', []):
            plantuml_code += f"{relationship['from']} --> {relationship['to']}: {relationship.get('label', '')}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_sequence_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for message in json_data['messages']:
            plantuml_code += f"{message['from']} -> {message['to']}: {message['content']}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_usecase_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for actor in json_data.get('actors', []):
            plantuml_code += f"actor {actor}\n"
        for usecase in json_data.get('usecases', []):
            plantuml_code += f"usecase ({usecase})\n"
        for relationship in json_data.get('relationships', []):
            plantuml_code += f"{relationship['from']} --> ({relationship['to']})\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_activity_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        plantuml_code += f"start\n"
        
        for item in json_data.get('flow', []):
            if isinstance(item, str):
                plantuml_code += f":{item};\n"
            elif isinstance(item, dict):
                if 'decision' in item:
                    plantuml_code += f"if ({item['decision']}) then (yes)\n"
                    plantuml_code += f"  :{item['yes']};\n"
                    plantuml_code += f"else (no)\n"
                    plantuml_code += f"  :{item['no']};\n"
                    plantuml_code += f"endif\n"
        
        plantuml_code += f"stop\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_component_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for component in json_data.get('components', []):
            plantuml_code += f"[{component}]\n"
        for interface in json_data.get('interfaces', []):
            plantuml_code += f"[{interface['from']}] --> [{interface['to']}] : {interface['label']}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_state_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for state in json_data.get('states', []):
            plantuml_code += f"state {state}\n"
        for transition in json_data.get('transitions', []):
            plantuml_code += f"{transition['from']} --> {transition['to']} : {transition['label']}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_object_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for obj_name, obj_info in json_data['objects'].items():
            plantuml_code += f"object {obj_name} {{\n"
            for attr, value in obj_info.items():
                plantuml_code += f"  {attr} = {value}\n"
            plantuml_code += "}\n"
        for relationship in json_data.get('relationships', []):
            plantuml_code += f"{relationship['from']} --> {relationship['to']}: {relationship.get('label', '')}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_deployment_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for node in json_data.get('nodes', []):
            plantuml_code += f"node {node['name']} {{\n"
            for component in node.get('components', []):
                plantuml_code += f"  [{component}]\n"
            plantuml_code += "}\n"
        for connection in json_data.get('connections', []):
            plantuml_code += f"{connection['from']} --> {connection['to']}: {connection.get('label', '')}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_timing_diagram(self, json_data):
        plantuml_code = "@startuml\n"
        for actor in json_data['actors']:
            plantuml_code += f"actor {actor}\n"
        for event in json_data['events']:
            plantuml_code += f"{event['actor']} is {event['state']} {event['time']}\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def _generate_mindmap(self, json_data):
        plantuml_code = "@startmindmap\n"
        plantuml_code += self._generate_mindmap_nodes(json_data, 0)
        plantuml_code += "@endmindmap"
        return plantuml_code

    def _generate_mindmap_nodes(self, node, level):
        indent = "  " * level
        plantuml_code = f"{indent}* {node['name']}\n"
        for child in node.get('children', []):
            plantuml_code += self._generate_mindmap_nodes(child, level + 1)
        return plantuml_code

    def _generate_json_diagram(self, json_data):
        plantuml_code = "@startjson\n"
        plantuml_code += json.dumps(json_data, indent=2)
        plantuml_code += "\n@endjson"
        return plantuml_code

    def _generate_yaml_diagram(self, json_data):
        plantuml_code = "@startyaml\n"
        plantuml_code += yaml.dump(json_data)
        plantuml_code += "\n@endyaml"
        return plantuml_code

    def _render_diagram(self, plantuml_code, diagram_type):
        filename = f"{diagram_type}_diagram.png"
        
        logger.debug(f"Rendering diagram: {diagram_type}")
        
        try:
            # Get the result from PlantUML
            result = self.pu.processes(plantuml_code)
            
            # Check if the result is raw image data or a URL
            try:
                # Try to decode as UTF-8 (URL)
                image_url = result.decode('utf-8')
                logger.debug(f"PlantUML returned URL: {image_url}")
                # If it's a URL, we need to download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                else:
                    raise Exception(f"Failed to download image. Status code: {response.status_code}")
            except UnicodeDecodeError:
                # If we can't decode as UTF-8, assume it's raw image data
                logger.debug("PlantUML returned raw image data")
                image_data = result

            # Write the image data to a file
            with open(filename, 'wb') as file:
                file.write(image_data)
            
            logger.debug(f"Diagram saved as: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error rendering diagram: {str(e)}")
            raise