import re
import json
import requests
import logging
from diagram_generator import DiagramGenerator

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:3020/api/v1/prediction/18f444a3-adf2-45be-9237-e81a66851140"

# Load the prompts from the JSON file
with open('diagram_prompts.json', 'r') as f:
    DIAGRAM_PROMPTS = json.load(f)

def query(payload):
    logger.debug(f"Sending request to API with payload: {payload}")
    response = requests.post(API_URL, json=payload)
    logger.debug(f"Received response: {response.text}")
    return response.json()

def create_diagram(diagram_type, instructions=""):
    logger.info(f"Creating diagram of type: {diagram_type}")
    
    if diagram_type not in DIAGRAM_PROMPTS:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    prompt = DIAGRAM_PROMPTS[diagram_type]["prompt"]
    if instructions:
        prompt += f"\n\nAdditional instructions: {instructions}"
    
    # Query the RAG bot
    logger.debug("Querying RAG bot")
    response = query({"question": prompt})
    
    # Extract the PlantUML code from the response
    try:
        if isinstance(response, dict) and 'text' in response:
            plantuml_code = response["text"].strip()
        else:
            plantuml_code = str(response).strip()

        # Remove markdown code block markers if present
        plantuml_code = re.sub(r'^```\w*\n|```$', '', plantuml_code, flags=re.MULTILINE)

        # Enhance the UML code
        enhance_prompt = DIAGRAM_PROMPTS["enhance_uml"]["prompt"].format(original_code=plantuml_code)
        enhanced_response = query({"question": enhance_prompt})
        
        if isinstance(enhanced_response, dict) and 'text' in enhanced_response:
            enhanced_plantuml_code = enhanced_response["text"].strip()
        else:
            enhanced_plantuml_code = str(enhanced_response).strip()

        # Remove markdown code block markers if present
        enhanced_plantuml_code = re.sub(r'^```\w*\n|```$', '', enhanced_plantuml_code, flags=re.MULTILINE)

        logger.debug(f"Enhanced PlantUML code:\n{enhanced_plantuml_code}")
        
        # Create the diagram
        logger.debug("Creating diagram using DiagramGenerator")
        generator = DiagramGenerator()
        logger.debug(f"Calling generate_diagram with type: {diagram_type}")
        diagram_filename = generator.generate_diagram(enhanced_plantuml_code, diagram_type)
        logger.info(f"Diagram created: {diagram_filename}")
        return diagram_filename
    
    except Exception as e:
        logger.error(f"Error in create_diagram: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception args: {e.args}")
        return None
if __name__ == "__main__":
    diagram_types = [
         "usecase", "activity"
    ]
    
    for diagram_type in diagram_types:
        logger.info(f"Processing diagram type: {diagram_type}")
        try:
            filename = create_diagram(diagram_type)
            if filename:
                logger.info(f"{diagram_type.capitalize()} diagram generated: {filename}")
            else:
                logger.error(f"Failed to generate {diagram_type} diagram")
        except Exception as e:
            logger.error(f"Unexpected error processing {diagram_type} diagram: {str(e)}")