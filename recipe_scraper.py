import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Any, TypeVar, Callable, Union
from urllib.parse import urlparse
import re
import logging
import json
import random
import time
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

def log_operation(operation_name: str) -> Callable:
    """Decorator to log the input and output of operations."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger.debug(f"{operation_name} input: args={args[1:]}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"{operation_name} output: {result}")
            return result
        return wrapper
    return decorator

def clean_text(text: str) -> str:
    """Clean text by removing parentheses content and extra whitespace."""
    cleaned = text.strip()
    
    if '(' in cleaned and ')' in cleaned:
        # First remove double parentheses
        cleaned = re.sub(r'\(\([^\)]*\)\)', '', cleaned).strip()
        # Then remove single parentheses
        cleaned = re.sub(r'\([^\)]*\)', '', cleaned).strip()
        
    return cleaned.strip()

def remove_multipliers(text: str) -> str:
    """Remove multiplier patterns like 1x, 2x, etc."""
    return ' '.join(
        part for part in text.split()
        if not (part.endswith('x') and any(c.isdigit() for c in part))
    ).strip()

def clean_and_deduplicate(items: List[str], item_type: str = "item") -> List[str]:
    """Clean a list of items and remove duplicates while preserving order."""
    seen = set()
    cleaned_items = []
    
    for item in items:
        cleaned = clean_text(item)
        cleaned = remove_multipliers(cleaned)
        
        if cleaned:  # Only process non-empty items
            item_lower = cleaned.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                cleaned_items.append(cleaned)
                logger.debug(f"Added cleaned {item_type}: '{cleaned}'")
    
    logger.debug(f"Found {len(cleaned_items)} unique {item_type}s")
    return cleaned_items

def split_text_to_list(text: Union[str, List[str]], separator: str = '\n') -> List[str]:
    """Convert text to list, handling both string and list inputs."""
    if isinstance(text, str):
        return [item.strip() for item in text.split(separator) if item.strip()]
    elif isinstance(text, list):
        return [item.strip() for item in text if item.strip()]
    return []

class RecipeScrapingService:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def scrape_recipe(self, url: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Scrape recipe information from a given URL.
        Returns a tuple of (recipe_data, error_message).
        recipe_data contains title, ingredients, and instructions if successful.
        """
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return None, "Invalid URL. Please include http:// or https://"

            # Parse URL to check validity
            try:
                parsed_url = urlparse(url)
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    return None, "Invalid URL format. Please check the URL and try again."
            except Exception as e:
                logger.error(f"URL parsing error: {str(e)}")
                return None, "Invalid URL format. Please check the URL and try again."

            # Make request with timeout and random user agent
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            try:
                response = self.session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                logger.warning(f"SSL verification failed for {url}, attempting without verification")
                response = self.session.get(url, headers=headers, timeout=15, verify=False)
                response.raise_for_status()
            
            # Check content type and encoding
            content_type = response.headers.get('Content-Type', '').lower()
            if not any(t in content_type for t in ['text/html', 'application/xhtml', 'application/xml']):
                return None, "URL does not point to a webpage"

            # Try to detect encoding correctly
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')
            
            logger.info(f"Starting recipe extraction from {url}")
            
            # Initialize recipe data containers
            title = ""
            ingredients = []
            instructions = []
            
            # Try to extract from JSON-LD first
            recipe_ld = self._extract_json_ld(soup)
            if recipe_ld:
                logger.info("Successfully extracted recipe from JSON-LD data")
                return recipe_ld, None
            
            # Fallback to HTML parsing
            logger.info("JSON-LD extraction failed, trying HTML parsing")
            
            # Try to extract title from the webpage
            title = self._extract_title(soup)
            if title:
                logger.info(f"Found recipe title: {title}")
            else:
                logger.warning("Failed to extract recipe title")
            
            # Try to find ingredients first in microdata
            ingredients = self._extract_microdata_ingredients(soup)
            if ingredients:
                logger.info(f"Found {len(ingredients)} ingredients from microdata")
            else:
                logger.info("Trying HTML parsing for ingredients")
                ingredients = self._extract_ingredients(soup)
                if ingredients:
                    logger.info(f"Found {len(ingredients)} ingredients from HTML")
            
            # Try to find instructions first in microdata
            instructions = self._extract_microdata_instructions(soup)
            if instructions:
                logger.info(f"Found {len(instructions)} instructions from microdata")
            else:
                logger.info("Trying HTML parsing for instructions")
                instructions = self._extract_instructions(soup)
                if instructions:
                    logger.info(f"Found {len(instructions)} instructions from HTML")
            
            # Enhanced validation with detailed error messages
            error_messages = []
            if not title:
                error_messages.append("Could not find recipe title")
            if not ingredients:
                error_messages.append("Could not find recipe ingredients")
            if not instructions:
                error_messages.append("Could not find recipe instructions")
                
            if error_messages:
                error_msg = "Failed to extract recipe: " + "; ".join(error_messages)
                logger.error(error_msg)
                return None, error_msg
            
            recipe_data = {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'source_url': url
            }
            
            return recipe_data, None

        except requests.Timeout:
            return None, "Request timed out. Please try again."
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return None, "Could not access the webpage. Please check the URL and try again."
        except Exception as e:
            logger.error(f"Unexpected error scraping recipe from {url}: {str(e)}")
            return None, "An unexpected error occurred while processing the recipe."

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract recipe data from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            logger.info(f"Found {len(scripts)} JSON-LD scripts")
            
            for script in scripts:
                if not script.string:
                    logger.debug("Empty JSON-LD script, skipping")
                    continue
                
                try:
                    data = json.loads(script.string)
                    recipes = []
                    
                    # Handle different JSON-LD formats
                    if isinstance(data, dict):
                        if data.get('@type') == 'Recipe':
                            recipes = [data]
                        elif '@graph' in data:
                            recipes = [item for item in data['@graph'] 
                                     if item.get('@type') == 'Recipe']
                        elif isinstance(data.get('mainEntity'), dict):
                            entity = data['mainEntity']
                            if entity.get('@type') == 'Recipe':
                                recipes = [entity]
                    elif isinstance(data, list):
                        recipes = [item for item in data if item.get('@type') == 'Recipe']

                    if not recipes:
                        logger.debug("No recipe found in JSON-LD")
                        continue

                    logger.info(f"Found {len(recipes)} recipes in JSON-LD")
                    recipe = recipes[0]  # Take the first recipe
                    
                    # Extract ingredients
                    ingredients = recipe.get('recipeIngredient', [])
                    if not ingredients and 'ingredients' in recipe:
                        ingredients = recipe.get('ingredients', [])
                        
                    # Ensure ingredients is a list
                    if isinstance(ingredients, str):
                        ingredients = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
                    
                    # Extract instructions
                    instructions = []
                    raw_instructions = recipe.get('recipeInstructions', [])
                    
                    if isinstance(raw_instructions, str):
                        instructions = [step.strip() for step in raw_instructions.split('\n')
                                     if step.strip()]
                    elif isinstance(raw_instructions, list):
                        for instruction in raw_instructions:
                            if isinstance(instruction, str):
                                instructions.append(instruction)
                            elif isinstance(instruction, dict):
                                text = instruction.get('text', '')
                                if text:
                                    instructions.append(text)
                    
                    if ingredients and instructions:
                        recipe_data = {
                            'title': recipe.get('name', ''),
                            'ingredients': ingredients,
                            'instructions': instructions,
                            'source_url': recipe.get('url', '')
                        }
                        logger.info("Successfully extracted recipe from JSON-LD")
                        return recipe_data
                except json.JSONDecodeError as decode_error:
                    logger.debug(f"Invalid JSON in script: {str(decode_error)}")
                except Exception as script_error:
                    logger.debug(f"Error processing JSON-LD script: {str(script_error)}")
            
            logger.debug("No valid recipe found in any JSON-LD script")
            return None
            
        except Exception as extraction_error:
            logger.error(f"Error in JSON-LD extraction: {str(extraction_error)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract recipe title using common patterns"""
        # Try different common patterns for recipe titles
        title_candidates = [
            soup.find('h1', {'class': ['recipe-title', 'entry-title', 'title', 'heading-title']}),
            soup.find('h1', itemprop='name'),
            soup.find(['h1', 'h2'], class_=lambda x: x and any(word in x.lower() 
                for word in ['recipe', 'title', 'heading', 'name'])),
            soup.find(class_=lambda x: x and 'recipe' in x.lower() and 'title' in x.lower()),
            soup.find('h1')  # Fallback to first h1
        ]
        
        for candidate in title_candidates:
            if candidate and candidate.text.strip():
                return candidate.text.strip()
        
        return ''

    def _extract_microdata_ingredients(self, soup: BeautifulSoup) -> List[str]:
        """Extract ingredients using microdata attributes"""
        ingredients = []
        for element in soup.find_all(True, {'itemtype': 'http://schema.org/Recipe'}):
            ingredient_elements = element.find_all(True, {'itemprop': 'recipeIngredient'})
            if ingredient_elements:
                ingredients.extend([i.text.strip() for i in ingredient_elements if i.text.strip()])
        return ingredients

    def _extract_microdata_instructions(self, soup: BeautifulSoup) -> List[str]:
        """Extract instructions using microdata attributes"""
        instructions = []
        for element in soup.find_all(True, {'itemtype': 'http://schema.org/Recipe'}):
            instruction_elements = element.find_all(True, {'itemprop': 'recipeInstructions'})
            if instruction_elements:
                instructions.extend([i.text.strip() for i in instruction_elements if i.text.strip()])
        return instructions

    def _looks_like_ingredient(self, text: str) -> bool:
        """Check if text looks like an ingredient line"""
        text = text.lower().strip()
        
        # Common ingredient patterns
        patterns = [
            r'\d+\s*(?:cup|tbsp|tsp|oz|gram|g|pound|lb|ml|l|pinch|dash|to taste)',  # measurements
            r'salt|pepper|sugar|flour|oil|butter|water|milk',  # common ingredients
            r'\d+\s*(?:large|medium|small)',  # size descriptors
            r'chopped|minced|diced|sliced|grated|crushed',  # preparation methods
        ]
        
        return any(re.search(pattern, text) for pattern in patterns)

    @log_operation("extract_ingredients")
    def _extract_ingredients(self, soup: BeautifulSoup) -> List[str]:
        """Extract ingredients list using common patterns"""
        ingredients = []
        
        # Define ingredient pattern searches
        pattern_searches = [
            # Class-based patterns
            lambda: soup.find_all(['li', 'div', 'span', 'p'], 
                class_=lambda x: x and any(word in x.lower() for word in 
                    ['ingredient', 'ingredients-item', 'ingredient-list'])),
            
            # Attribute-based patterns
            lambda: soup.find_all(['li', 'div', 'span'], 
                itemprop=['recipeIngredient', 'ingredients']),
            
            # Data attribute patterns
            lambda: soup.find_all(attrs={'data-ingredient': True}),
            lambda: soup.find_all(attrs={'data-recipe-ingredient': True}),
            
            # List items within ingredient sections
            lambda: soup.find_all('li', class_=lambda x: x and 'ingredient' in x.lower()),
            
            # Fallback: Look for ingredient-like content in structured lists
            lambda: [item for item in soup.find_all('li')
                    if self._looks_like_ingredient(item.text)]
        ]
        
        # Try each pattern until we find ingredients
        for pattern_search in pattern_searches:
            try:
                items = pattern_search()
                if items:
                    found_ingredients = [item.text.strip() for item in items if item.text.strip()]
                    # Validate found ingredients
                    if found_ingredients and any(self._looks_like_ingredient(ing) for ing in found_ingredients):
                        ingredients = found_ingredients
                        break
            except Exception as e:
                logger.debug(f"Error in ingredient pattern search: {str(e)}")
                continue
        
        # Clean and validate the ingredients
        cleaned_ingredients = clean_and_deduplicate(ingredients, "ingredient")
        return [ing for ing in cleaned_ingredients if self._looks_like_ingredient(ing)]

    @log_operation("clean_ingredients")
    @log_operation("clean_ingredients")
    def _clean_ingredients(self, ingredients: List[str]) -> List[str]:
        """Clean and format the ingredients list."""
        # Use our helper function to clean and deduplicate ingredients
        cleaned = clean_and_deduplicate(ingredients, "ingredient")
        
        # Remove any advertisement text and special characters
        cleaned = [
            ing.replace('ADVERTISEMENT', '')
               .replace('Advertisement', '')
               .replace('▢', '')  # Remove recipe checkboxes
               .replace('×', 'x')  # Normalize multiplication symbol
               .replace('⅓', '1/3')  # Convert unicode fractions
               .replace('⅔', '2/3')
               .replace('¼', '1/4')
               .replace('½', '1/2')
               .replace('¾', '3/4')
               .replace('  ', ' ')  # Remove double spaces
               .strip()
            for ing in cleaned
        ]
        
        return [ing for ing in cleaned if ing]  # Filter out any empty strings

    @log_operation("clean_instruction")
    def _clean_instruction(self, text: str) -> str:
        """Clean up instruction text"""
        # First clean up any HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove step numbers at the start
        text = re.sub(r'^(?:Step\s*)?[0-9]+[.):]\s*', '', text, flags=re.I)
        
        # Use our helper functions to clean the text
        cleaned = clean_text(text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove very short "instructions" that are likely headers
        if len(text) < 10:
            return ''
        
        return text

    def _extract_instructions(self, soup: BeautifulSoup) -> List[str]:
        """Extract cooking instructions using common patterns"""
        instructions = []
        
        # Look for common instruction patterns
        pattern_searches = [
            # Class-based patterns
            lambda: soup.find_all(['li', 'div', 'p'], 
                class_=lambda x: x and any(word in x.lower() for word in 
                    ['instruction', 'directions', 'steps', 'method', 'preparation'])),
            
            # Attribute-based patterns
            lambda: soup.find_all(['li', 'div', 'p'], 
                itemprop=['recipeInstructions', 'instructions', 'step', 'preparationStep']),
            
            # Data attribute patterns
            lambda: soup.find_all(attrs={'data-instruction': True}),
            lambda: soup.find_all(attrs={'data-recipe-instruction': True}),
            
            # Ordered list items within method sections
            lambda: soup.find_all('ol li'),
            
            # Find recipe method section and get its paragraphs
            lambda: soup.find(class_=lambda x: x and 'method' in str(x).lower()).find_all('p') 
                if soup.find(class_=lambda x: x and 'method' in str(x).lower()) else [],
            
            # Fallback: Look for paragraphs that look like instructions
            lambda: [p for p in soup.find_all('p') 
                    if len(p.text.strip()) > 50 and  # Longer text likely instructions
                    re.search(r'^[0-9]+[.)]\s|step\s+[0-9]+', p.text.strip(), re.I)]  # Numbered steps
        ]
        
        # Try each pattern until we find instructions
        for pattern_search in pattern_searches:
            try:
                items = pattern_search()
                if items:
                    instructions = [self._clean_instruction(item.text) for item in items]
                    instructions = [i for i in instructions if i]  # Remove empty strings
                    if instructions:
                        logger.info(f"Found {len(instructions)} instructions using pattern: {pattern_search.__name__ if hasattr(pattern_search, '__name__') else 'anonymous'}")
                        break
            except Exception as e:
                logger.debug(f"Error in instruction pattern search: {str(e)}")
                continue
                
        return instructions

    @log_operation("format_recipe")
    def format_recipe(self, recipe_data: Dict) -> Dict:
        """Format the recipe data for storage and display"""
        try:
            # Extract and clean ingredients and instructions
            ingredients = split_text_to_list(recipe_data.get('ingredients', []))
            instructions = split_text_to_list(recipe_data.get('instructions', []))
            
            # Clean and deduplicate ingredients and instructions
            unique_ingredients = clean_and_deduplicate(ingredients, "ingredient")
            unique_instructions = clean_and_deduplicate(instructions, "instruction")
            
            # Format the recipe data
            formatted_data = {
                'title': clean_text(recipe_data.get('title', '')),
                'ingredients': '\n'.join(unique_ingredients),
                'instructions': '\n'.join(unique_instructions),
                'source_url': recipe_data.get('source_url', '')
            }
            
            # Validate formatted data
            if not formatted_data['title']:
                raise ValueError("Recipe title is missing")
            if not formatted_data['ingredients'].strip():
                raise ValueError("Recipe ingredients are missing")
            if not formatted_data['instructions'].strip():
                raise ValueError("Recipe instructions are missing")
            
            logger.info(f"Formatted recipe: {len(unique_ingredients)} ingredients, {len(unique_instructions)} instructions")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting recipe data: {str(e)}")
            logger.debug(f"Recipe data received: {recipe_data}")
            raise ValueError(f"Failed to format recipe: {str(e)}")