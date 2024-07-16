import plantuml
import requests
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagramGenerator:
    def __init__(self, plantuml_url='http://www.plantuml.com/plantuml/'):
        self.pu = plantuml.PlantUML(url=plantuml_url)

    def generate_diagram(self, plantuml_code, diagram_type):
        logger.debug(f"Generating diagram of type: {diagram_type}")
        logger.debug(f"PlantUML code:\n{plantuml_code}")
        try:
            return self._render_diagram(plantuml_code, diagram_type)
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            raise

    def _render_diagram(self, plantuml_code, diagram_type):
        filename = f"{diagram_type}_diagram.png"
        
        logger.debug(f"Rendering diagram: {diagram_type}")
        
        try:
            url = self.pu.get_url(plantuml_code)
            logger.debug(f"Generated URL: {url}")
            
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Diagram saved as: {filename}")
                return filename
            else:
                raise Exception(f"Failed to download image. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error rendering diagram: {str(e)}")
            raise