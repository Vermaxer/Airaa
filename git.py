import requests
import base64
import os
import logging
from github import Github
from uml import generate_diagram_prompt, create_diagram

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub authentication
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    logger.warning("GITHUB_TOKEN not set in environment variables")

def get_repo_contents(repo_url, path="", token=None):
    """Fetch repository contents using GitHub API"""
    logger.info(f"Fetching repo contents for {repo_url}, path: {path}")
    try:
        owner, repo = repo_url.split('github.com/')[-1].split('.git')[0].split('/')
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {'Authorization': f'token {token or GITHUB_TOKEN}'} if token or GITHUB_TOKEN else {}
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        logger.debug(f"Successfully fetched repo contents for {path}")
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching repo contents: {str(e)}")
        raise

def get_file_content(file_url, token=None):
    """Fetch file content from GitHub"""
    logger.info(f"Fetching file content from {file_url}")
    try:
        headers = {'Authorization': f'token {token or GITHUB_TOKEN}'} if token or GITHUB_TOKEN else {}
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()
        
        # Check if the content is JSON
        try:
            json_content = response.json()
            if 'content' in json_content:
                content = base64.b64decode(json_content['content']).decode('utf-8')
            else:
                content = json_content
        except ValueError:
            # If it's not JSON, just return the text content
            content = response.text
        
        logger.debug(f"Successfully fetched file content")
        return content
    except Exception as e:
        logger.error(f"Error fetching file content: {str(e)}")
        raise

def analyze_repo(repo_url, token=None):
    """Analyze repository and prepare data for documentation generation"""
    logger.info(f"Analyzing repository: {repo_url}")
    try:
        contents = get_repo_contents(repo_url, token=token)
        
        repo_data = {
            'structure': generate_tree_structure(contents, repo_url, token),
            'readme': None,
            'license': None,
            'main_files': [],
            'config_files': []
        }

        for item in contents:
            if item['name'].lower() == 'readme.md':
                repo_data['readme'] = get_file_content(item['download_url'], token)
            elif item['name'].lower() == 'license':
                repo_data['license'] = get_file_content(item['download_url'], token)
            elif item['name'].endswith(('.py', '.js', '.java', '.cpp')):
                content = get_file_content(item['download_url'], token)
                repo_data['main_files'].append({'name': item['name'], 'content': content})
            elif item['name'] in ('requirements.txt', 'package.json', 'config.yml'):
                content = get_file_content(item['download_url'], token)
                repo_data['config_files'].append({'name': item['name'], 'content': content})

        logger.debug("Repository analysis completed successfully")
        return repo_data
    except Exception as e:
        logger.error(f"Error analyzing repository: {str(e)}")
        raise

def generate_tree_structure(contents, repo_url, token, level=0):
    """Generate a tree structure of the repository"""
    logger.info(f"Generating tree structure for {repo_url}")
    try:
        tree = ""
        for item in contents:
            prefix = "  " * level
            if item['type'] == 'dir':
                tree += f"{prefix}- {item['name']}/\n"
                sub_contents = get_repo_contents(repo_url, item['path'], token)
                tree += generate_tree_structure(sub_contents, repo_url, token, level + 1)
            else:
                tree += f"{prefix}- {item['name']}\n"
        logger.debug("Tree structure generated successfully")
        return tree
    except Exception as e:
        logger.error(f"Error generating tree structure: {str(e)}")
        raise

def create_documentation_prompt(repo_data):
    """Create a prompt for documentation generation based on repo analysis"""
    logger.info("Creating documentation prompt")
    prompt = f"""
Generate comprehensive documentation for the following GitHub repository:

Repository Structure:
{repo_data['structure']}

Existing README content:
{repo_data['readme']}

License Information:
{repo_data['license']}

Main code files:
{', '.join(file['name'] for file in repo_data['main_files'])}

Configuration files:
{', '.join(file['name'] for file in repo_data['config_files'])}

Based on this information, please provide:

1. Project Title and Description
2. Key Features
3. Technologies Used
4. Installation Instructions
5. Usage Guide
6. API Documentation (if applicable)
7. Configuration
8. Main Components/Modules Overview
   - Describe the main functions and purpose of each key module
9. Project Structure Explanation
10. Contributing Guidelines
11. License Information
12. Contact Information or Support

Ensure the documentation is detailed, well-structured, and follows best practices for technical documentation.
"""
    logger.debug("Documentation prompt created successfully")
    return prompt

def send_query(prompt):
    """Send query to RAG model API"""
    logger.info("Sending query to RAG model API")
    try:
        url = "http://localhost:3020/api/v1/prediction/81923407-56cb-4d94-b351-ff05efd2d66b"
        response = requests.post(url, json={"question": prompt})
        response.raise_for_status()
        logger.debug("Query sent successfully")
        return response.json()["text"]
    except Exception as e:
        logger.error(f"Error sending query to RAG model API: {str(e)}")
        raise

def generate_documentation(repo_url, include_diagrams=False, github_token=None):
    """Generate documentation based on repository analysis"""
    logger.info(f"Generating documentation for {repo_url}")
    try:
        token = github_token or GITHUB_TOKEN
        if not token:
            raise ValueError("GitHub token is required for repository analysis")
        
        repo_data = analyze_repo(repo_url, token)
        documentation_prompt = create_documentation_prompt(repo_data)
        
        documentation = send_query(documentation_prompt)
        
        if include_diagrams:
            logger.info("Generating diagrams")
            diagram_types = ["class", "component", "sequence"]
            for diagram_type in diagram_types:
                diagram_prompt = generate_diagram_prompt(diagram_type, repo_data)
                diagram_content = send_query(diagram_prompt)
                diagram_filename = create_diagram(diagram_type, diagram_content)
                if diagram_filename:
                    documentation += f"\n\n## {diagram_type.capitalize()} Diagram\n"
                    documentation += f"![{diagram_type.capitalize()} Diagram]({diagram_filename})\n"
        
        logger.debug("Documentation generated successfully")
        return documentation
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        raise
# GitHub authentication


def push_to_github(repo_url, content, github_token):
    """Push generated documentation to GitHub"""
    logger.info(f"push_to_github function called with repo_url: {repo_url}")
    try:
        g = Github(github_token)
        owner, repo_name = repo_url.split('github.com/')[-1].split('.git')[0].split('/')
        logger.info(f"Accessing repo: {owner}/{repo_name}")
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        try:
            logger.info("Attempting to get existing README.md")
            file = repo.get_contents("README.md")
            logger.info("Updating existing README.md")
            repo.update_file("README.md", "Update README via AIra", content, file.sha)
            logger.info("README.md updated successfully")
        except Exception as e:
            logger.info(f"README.md not found, creating new file. Error: {str(e)}")
            repo.create_file("README.md", "Create README via AIra", content)
            logger.info("README.md created successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error pushing to GitHub: {str(e)}")
        logger.exception("Full traceback:")
        return False