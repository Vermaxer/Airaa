import json
import requests
import logging
from diagram_generator import DiagramGenerator

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:3020/api/v1/prediction/18f444a3-adf2-45be-9237-e81a66851140"

def query(payload):
    logger.debug(f"Sending request to API with payload: {payload}")
    response = requests.post(API_URL, json=payload)
    logger.debug(f"Received response: {response.text}")
    return response.json()



def generate_diagram_prompt(diagram_type, instructions=""):
    prompts = {
        "class": {
            "template": {
                "diagram_type": "class",
                "data": {
                    "classes": {
                        "<ClassName>": {
                            "attributes": ["<attribute1>: <type>", "<attribute2>: <type>"],
                            "methods": ["<method1>(<params>): <return_type>", "<method2>(<params>): <return_type>"]
                        }
                    },
                    "relationships": [
                        {"from": "<ClassName1>", "to": "<ClassName2>", "type": "<relationship_type>", "label": "<relationship_description>"}
                    ]
                }
            },
            "instruction": "Analyze the entire repository and create a comprehensive class diagram. Include all major classes, their attributes, methods, and relationships. Consider inheritance, associations, and dependencies between classes across all modules."
        },
        "sequence": {
            "template": {
                "diagram_type": "sequence",
                "data": {
                    "participants": ["<Participant1>", "<Participant2>"],
                    "messages": [
                        {"from": "<Sender>", "to": "<Receiver>", "content": "<Message>", "note": "<Additional_Info>"}
                    ]
                }
            },
            "instruction": "Create a detailed sequence diagram showing the main interactions between components in the system. Focus on a key process or user story, and include all relevant modules and functions involved."
        },
        "usecase": {
            "template": {
                "diagram_type": "usecase",
                "data": {
                    "actors": ["<Actor1>", "<Actor2>"],
                    "usecases": ["<UseCase1>", "<UseCase2>"],
                    "relationships": [
                        {"from": "<Actor1>", "to": "<UseCase1>", "type": "<RelationshipType>"},
                        {"from": "<UseCase1>", "to": "<UseCase2>", "type": "includes/extends"}
                    ]
                }
            },
            "instruction": "Create a comprehensive use case diagram showing all major actors and use cases in the system. Include relationships between actors and use cases, as well as relationships between use cases (e.g., include, extend)."
        },
        "activity": {
            "template": {
                "diagram_type": "activity",
                "data": {
                    "start": "<StartNode>",
                    "end": "<EndNode>",
                    "activities": ["<Activity1>", "<Activity2>"],
                    "decisions": [
                        {
                            "condition": "<Condition>",
                            "yes": "<YesActivity>",
                            "no": "<NoActivity>"
                        }
                    ],
                    "forks": [
                        {
                            "from": "<SourceActivity>",
                            "to": ["<ParallelActivity1>", "<ParallelActivity2>"]
                        }
                    ],
                    "joins": [
                        {
                            "from": ["<ParallelActivity1>", "<ParallelActivity2>"],
                            "to": "<MergeActivity>"
                        }
                    ]
                }
            },
            "instruction": "Create a detailed activity diagram representing a key process in the system. Include start and end nodes, activities, decision points, forks, and joins to show parallel processing if applicable."
        },
        "component": {
            "template": {
                "diagram_type": "component",
                "data": {
                    "components": [
                        {"name": "<ComponentName>", "type": "<ComponentType>", "description": "<ComponentDescription>"}
                    ],
                    "interfaces": [
                        {"from": "<Component1>", "to": "<Component2>", "type": "<InterfaceType>", "description": "<InterfaceDescription>"}
                    ]
                }
            },
            "instruction": "Create a comprehensive component diagram showing all major components and their interfaces in the system. Include external systems, databases, and services. Provide detailed descriptions for each component and interface."
        },
        "state": {
            "template": {
                "diagram_type": "state",
                "data": {
                    "states": ["<State1>", "<State2>"],
                    "transitions": [
                        {"from": "<State1>", "to": "<State2>", "event": "<Event>", "action": "<Action>", "guard": "<Condition>"}
                    ],
                    "initial": "<InitialState>",
                    "final": "<FinalState>"
                }
            },
            "instruction": "Create a state diagram representing the lifecycle or behavior of a key object or process in the system. Include all relevant states, transitions, events, actions, and guards."
        },
        "object": {
            "template": {
                "diagram_type": "object",
                "data": {
                    "objects": {
                        "<ObjectName>": {
                            "<attribute1>": "<value1>",
                            "<attribute2>": "<value2>"
                        }
                    },
                    "relationships": [
                        {"from": "<Object1>", "to": "<Object2>", "type": "<RelationshipType>", "label": "<RelationshipDescription>"}
                    ]
                }
            },
            "instruction": "Create an object diagram showing instances of key classes in the system. Include attribute values and relationships between objects. Focus on a specific scenario or system state."
        },
        "deployment": {
            "template": {
                "diagram_type": "deployment",
                "data": {
                    "nodes": [
                        {
                            "name": "<NodeName>",
                            "type": "<NodeType>",
                            "components": ["<Component1>", "<Component2>"]
                        }
                    ],
                    "connections": [
                        {"from": "<Node1>", "to": "<Node2>", "protocol": "<Protocol>", "description": "<ConnectionDescription>"}
                    ]
                }
            },
            "instruction": "Create a deployment diagram showing the physical architecture of the system. Include all hardware nodes, software components deployed on each node, and the connections between nodes."
        },
        "timing": {
            "template": {
                "diagram_type": "timing",
                "data": {
                    "actors": ["<Actor1>", "<Actor2>"],
                    "events": [
                        {"actor": "<Actor1>", "state": "<State1>", "time": "<Time1>"},
                        {"actor": "<Actor2>", "state": "<State2>", "time": "<Time2>"}
                    ],
                    "constraints": [
                        {"description": "<ConstraintDescription>", "from": "<Event1>", "to": "<Event2>"}
                    ]
                }
            },
            "instruction": "Create a timing diagram showing the behavior of objects or components over time. Focus on a specific scenario or process, including all relevant actors, state changes, and timing constraints."
        },
        "mindmap": {
            "template": {
                "diagram_type": "mindmap",
                "data": {
                    "name": "<ProjectName>",
                    "children": [
                        {
                            "name": "<MainCategory>",
                            "children": [
                                {"name": "<Subcategory>", "children": [{"name": "<Detail>"}]}
                            ]
                        }
                    ]
                }
            },
            "instruction": "Create a comprehensive mindmap of the project structure, including all major components, modules, and their relationships. Consider the project's architecture, dependencies, and key features. Provide at least three levels of depth for each main category."
        },
        "json": {
            "template": {
                "diagram_type": "json",
                "data": {
                    "<key1>": "<value1>",
                    "<key2>": {
                        "<nestedKey1>": "<nestedValue1>",
                        "<nestedKey2>": ["<arrayItem1>", "<arrayItem2>"]
                    }
                }
            },
            "instruction": "Create a JSON representation of a key aspect of the system. This could be a configuration file, API response, or data model. Ensure the JSON is well-structured and includes nested objects and arrays where appropriate."
        },
        "yaml": {
            "template": {
                "diagram_type": "yaml",
                "data": {
                    "<key1>": "<value1>",
                    "<key2>": ["<item1>", "<item2>"],
                    "<key3>": {
                        "<nestedKey1>": "<nestedValue1>",
                        "<nestedKey2>": ["<nestedItem1>", "<nestedItem2>"]
                    }
                }
            },
            "instruction": "Create a YAML representation of a key aspect of the system. This could be a configuration file, deployment specification, or data model. Ensure the YAML is well-structured and includes nested objects and arrays where appropriate."
        }
    }
    

    if diagram_type not in prompts:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")
    else:
        template = json.dumps(prompts[diagram_type]["template"], indent=2)
        default_instruction = prompts[diagram_type]["instruction"]
        instruction = instructions if instructions else default_instruction
        return f"""
    Analyze the entire repository thoroughly, considering all files, modules, functions, and their relationships.
    Create a {diagram_type} diagram based on this comprehensive analysis.
    Template to follow:
    {template}
    Specific instructions:
    {instruction}
    Ensure the response is a valid JSON object containing 'diagram_type' and 'data' keys, without any additional formatting or code block markers.
    Provide as much detail as possible, using real names of classes, methods, components, etc., from the analyzed repository.
    """



def create_diagram(diagram_type, instructions=""):
    logger.info(f"Creating diagram of type: {diagram_type}")
    prompt = generate_diagram_prompt(diagram_type, instructions)
    
    # Query the RAG bot
    logger.debug("Querying RAG bot")
    response = query({"question": prompt})
    
    # Extract the JSON from the response
    try:
        # Check if the response is a dictionary with a 'text' key
        if isinstance(response, dict) and 'text' in response:
            json_text = response["text"].strip()
        else:
            json_text = str(response).strip()

        # Remove code block markers if present
        if json_text.startswith("```") and json_text.endswith("```"):
            json_text = json_text.split("\n", 1)[1].rsplit("\n", 1)[0]

        diagram_data = json.loads(json_text)
        logger.debug(f"Parsed JSON from RAG bot response: {json.dumps(diagram_data, indent=2)}")
        
        # Validate the parsed JSON structure
        if 'diagram_type' not in diagram_data or 'data' not in diagram_data:
            raise ValueError("Invalid JSON structure: missing 'diagram_type' or 'data' keys")
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing RAG bot response: {str(e)}")
        logger.debug(f"Raw response text: {response}")
        return None

    # Create the diagram
    try:
        logger.debug("Creating diagram using DiagramGenerator")
        generator = DiagramGenerator()
        diagram_filename = generator.generate_diagram(diagram_data["data"], diagram_type)
        logger.info(f"Diagram created: {diagram_filename}")
        return diagram_filename
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    diagram_types = [
        "class", "sequence", "usecase", "activity", "component", 
        "state"
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