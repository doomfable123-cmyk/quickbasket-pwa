from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from recipe_scraper import RecipeScrapingService
from models import init_db, get_session, Recipe
from datetime import datetime
import os
import secrets
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure secret key
recipe_scraper = RecipeScrapingService()

# Add cache control for development to prevent browser caching issues
@app.after_request
def after_request(response):
    """Add cache control headers to prevent caching during development"""
    if request.endpoint and 'static' not in request.endpoint:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

try:
    # Initialize database
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {e}")
    sys.exit(1)

@app.route('/')
@app.route('/recipes/')
def recipes():
    session = get_session()
    try:
        recipes_list = session.query(Recipe).all()
        recipes_data = [recipe.to_dict() for recipe in recipes_list]
        return render_template('recipes.html', recipes=recipes_data)
    finally:
        session.close()

@app.route('/add-to-grocery-list', methods=['POST'])
def add_to_grocery_list():
    session = get_session()
    try:
        recipe_ids = request.form.getlist('recipe_ids')
        if not recipe_ids:
            return jsonify({'status': 'error', 'message': 'Please select at least one recipe.'}), 400
            
        # Update the last_added_to_grocery date for selected recipes
        current_time = datetime.utcnow()
        # Format the date as MM-DD-YYYY for display
        formatted_date = current_time.strftime('%m-%d-%Y')
        
        for recipe_id in recipe_ids:
            recipe = session.query(Recipe).filter_by(id=recipe_id).first()
            if recipe:
                recipe.last_added_to_grocery = current_time
        
        session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Selected recipes added to grocery list!',
            'groceryListUrl': url_for('grocery_list', recipe_ids=','.join(recipe_ids)),
            'timestamp': formatted_date
        })
    finally:
        session.close()

@app.route('/clear-grocery-list', methods=['POST'])
def clear_grocery_list():
    session = get_session()
    try:
        # Clear last_added_to_grocery dates for all recipes
        session.query(Recipe).update({Recipe.last_added_to_grocery: None})
        session.commit()
        return '', 204  # Return success with no content
    except Exception as e:
        logger.error(f"Error clearing grocery list: {e}")
        return 'Error clearing grocery list', 500
    finally:
        session.close()

@app.route('/grocery_list/')
@app.route('/grocery_list')  # Handle both with and without trailing slash
def grocery_list():
    session = get_session()
    try:
        recipe_ids = request.args.get('recipe_ids', '')
        ingredients_list = []
        
        # Only show recipes that have been added to grocery list
        recipes = session.query(Recipe).filter(Recipe.last_added_to_grocery.isnot(None)).all()
        
        # Extract ingredients from each recipe
        for recipe in recipes:
            if recipe.ingredients:
                ingredients_list.extend(recipe.ingredients.split('\n'))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ingredients = []
        for item in ingredients_list:
            item_lower = item.lower()
            if item_lower not in seen and item.strip():
                seen.add(item_lower)
                unique_ingredients.append(item.strip())
        
        return render_template('grocery_list.html', 
                            ingredients=unique_ingredients,
                            selected_recipes=recipes)
    except Exception as e:
        logger.error(f"Error generating grocery list: {e}")
        flash('Error generating grocery list.', 'error')
        return redirect(url_for('recipes'))
    finally:
        session.close()

@app.route('/delete-recipes', methods=['POST'])
def delete_recipes():
    session = get_session()
    try:
        recipe_ids = request.form.getlist('recipe_ids')
        if not recipe_ids:
            flash('Please select at least one recipe to delete.', 'error')
            return redirect(url_for('recipes'))

        # Delete all selected recipes
        deleted_count = session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).delete(synchronize_session='fetch')
        session.commit()

        if deleted_count > 0:
            flash(f'{deleted_count} recipe(s) deleted successfully!', 'success')
        else:
            flash('No recipes were deleted.', 'error')
    except Exception as e:
        logger.error(f"Error deleting recipes: {e}")
        flash('Error deleting recipes.', 'error')
        session.rollback()
    finally:
        session.close()
    return redirect(url_for('recipes'))



@app.route('/add-recipe-url', methods=['GET', 'POST'])
def add_recipe_url():
    if request.method == 'POST':
        url = request.form.get('recipe_url')
        if not url:
            flash('Please enter a recipe URL', 'error')
            return redirect(url_for('add_recipe_url'))
        
        # Attempt to scrape the recipe
        recipe_data, error = recipe_scraper.scrape_recipe(url)
        
        if recipe_data:
            try:
                # Format the recipe data
                formatted_recipe = recipe_scraper.format_recipe(recipe_data)
                
                # Create new recipe in database
                session = get_session()
                new_recipe = Recipe(
                    title=formatted_recipe['title'],
                    ingredients=formatted_recipe['ingredients'],
                    source_url=formatted_recipe['source_url']
                )
                session.add(new_recipe)
                session.commit()
                
                flash('Recipe successfully imported!', 'success')
                return redirect(url_for('recipes'))
            except Exception as e:
                flash(f'Error saving recipe: {str(e)}', 'error')
                return redirect(url_for('add_recipe_url'))
        else:
            flash(f'Unable to extract recipe: {error}', 'error')
            return redirect(url_for('add_recipe_url'))
            
    return render_template('add_recipe_url.html')

@app.route('/add-recipe-manual', methods=['GET', 'POST'])
def add_recipe_manual():
    if request.method == 'POST':
        try:
            session = get_session()
            new_recipe = Recipe(
                title=request.form.get('title'),
                ingredients=request.form.get('ingredients'),
                instructions=request.form.get('instructions')
            )
            session.add(new_recipe)
            session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('recipes'))
        except Exception as e:
            flash(f'Error saving recipe: {str(e)}', 'error')
            return redirect(url_for('add_recipe_manual'))
        finally:
            session.close()
    
    # Add cache control headers to prevent caching issues
    response = app.make_response(render_template('add_recipe_manual.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ===== API ENDPOINTS FOR MOBILE APP =====

@app.route('/static/manifest.json')
def serve_manifest():
    """Serve PWA manifest file"""
    return app.send_static_file('manifest.json')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for mobile app connectivity"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/recipes', methods=['GET'])
@app.route('/recipes', methods=['GET'])
def api_recipes():
    """API endpoint to get all recipes in JSON format"""
    # Check if request expects JSON (from mobile app)
    if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
        session = get_session()
        try:
            recipes_list = session.query(Recipe).all()
            recipes_data = [recipe.to_dict() for recipe in recipes_list]
            return jsonify({'recipes': recipes_data})
        except Exception as e:
            logger.error(f"Error fetching recipes API: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    else:
        # Original web interface behavior
        session = get_session()
        try:
            recipes_list = session.query(Recipe).all()
            recipes_data = [recipe.to_dict() for recipe in recipes_list]
            return render_template('recipes.html', recipes=recipes_data)
        finally:
            session.close()

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
@app.route('/delete_recipe/<int:recipe_id>', methods=['DELETE', 'POST'])
def api_delete_recipe(recipe_id):
    """API endpoint to delete a recipe"""
    session = get_session()
    try:
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        recipe_name = recipe.name
        session.delete(recipe)
        session.commit()
        
        return jsonify({'message': f'Recipe "{recipe_name}" deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting recipe API: {e}")
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/recipes/url', methods=['POST'])
@app.route('/add_recipe_url', methods=['POST'])
def api_add_recipe_url():
    """API endpoint to add recipe from URL"""
    if request.method == 'POST':
        session = get_session()
        try:
            # Handle both JSON (mobile) and form data (web)
            if request.is_json:
                data = request.get_json()
                url = data.get('url', '').strip()
            else:
                url = request.form.get('recipe_url', '').strip()
            
            if not url:
                error_msg = 'Recipe URL is required'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('add_recipe_url'))
            
            # Extract recipe using the scraping service
            try:
                recipe_data = recipe_scraper.scrape_recipe(url)
            except Exception as scrape_error:
                error_msg = f'Failed to extract recipe from URL: {str(scrape_error)}'
                logger.error(f"Scraping error for URL {url}: {scrape_error}")
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('add_recipe_url'))
            
            # Create and save recipe
            new_recipe = Recipe(
                name=recipe_data['name'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data.get('instructions', ''),
                url=url
            )
            
            session.add(new_recipe)
            session.commit()
            
            recipe_dict = new_recipe.to_dict()
            
            if request.is_json:
                return jsonify(recipe_dict), 201
            else:
                flash('Recipe added successfully!', 'success')
                return redirect(url_for('recipes'))
                
        except Exception as e:
            session.rollback()
            error_msg = f'Error adding recipe: {str(e)}'
            logger.error(error_msg)
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return redirect(url_for('add_recipe_url'))
        finally:
            session.close()

@app.route('/api/recipes/manual', methods=['POST'])
@app.route('/add_recipe_manual', methods=['POST'])
def api_add_recipe_manual():
    """API endpoint to add recipe manually"""
    if request.method == 'POST':
        session = get_session()
        try:
            # Handle both JSON (mobile) and form data (web)
            if request.is_json:
                data = request.get_json()
                name = data.get('name', '').strip()
                ingredients = data.get('ingredients', [])
                instructions = data.get('instructions', '').strip()
            else:
                name = request.form.get('recipe_name', '').strip()
                ingredients_text = request.form.get('ingredients', '').strip()
                instructions = request.form.get('instructions', '').strip()
                
                # Parse ingredients from text (split by newlines)
                ingredients = [ing.strip() for ing in ingredients_text.split('\n') if ing.strip()]
            
            if not name:
                error_msg = 'Recipe name is required'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('add_recipe_manual'))
            
            if not ingredients:
                error_msg = 'At least one ingredient is required'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return redirect(url_for('add_recipe_manual'))
            
            # Create and save recipe
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions or ''
            )
            
            session.add(new_recipe)
            session.commit()
            
            recipe_dict = new_recipe.to_dict()
            
            if request.is_json:
                return jsonify(recipe_dict), 201
            else:
                flash('Recipe added successfully!', 'success')
                return redirect(url_for('recipes'))
                
        except Exception as e:
            session.rollback()
            error_msg = f'Error saving recipe: {str(e)}'
            logger.error(error_msg)
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return redirect(url_for('add_recipe_manual'))
        finally:
            session.close()

@app.route('/api/grocery-list', methods=['GET'])
@app.route('/grocery_list', methods=['GET'])
def api_grocery_list():
    """API endpoint to get grocery list in JSON format"""
    # Check if request expects JSON (from mobile app)
    if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
        session = get_session()
        try:
            recipes = session.query(Recipe).all()
            
            # Generate grocery list from all recipes
            grocery_items = {}
            for recipe in recipes:
                for ingredient in recipe.ingredients:
                    ingredient = ingredient.strip()
                    if ingredient and ingredient not in grocery_items:
                        grocery_items[ingredient] = False  # Not checked by default
            
            # Convert to list format expected by mobile app
            grocery_list = [{'name': item, 'checked': checked} for item, checked in grocery_items.items()]
            grocery_list.sort(key=lambda x: x['name'].lower())
            
            return jsonify({'grocery_list': grocery_list})
        except Exception as e:
            logger.error(f"Error fetching grocery list API: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    else:
        # Original web interface behavior
        session = get_session()
        try:
            recipes = session.query(Recipe).all()
            return render_template('grocery_list.html', recipes=recipes)
        finally:
            session.close()

@app.route('/api/grocery-list/update', methods=['POST'])
@app.route('/update_grocery_item', methods=['POST'])
def api_update_grocery_item():
    """API endpoint to update grocery item checked status"""
    try:
        if request.is_json:
            data = request.get_json()
            item_name = data.get('item_name', '').strip()
            checked = data.get('checked', False)
        else:
            item_name = request.form.get('item_name', '').strip()
            checked = request.form.get('checked') == 'true'
        
        if not item_name:
            return jsonify({'error': 'Item name is required'}), 400
        
        # For now, just return success (in a full implementation, you might store checked states in database)
        # The mobile app handles state locally, this endpoint maintains compatibility
        return jsonify({'message': 'Item updated successfully', 'item': item_name, 'checked': checked})
        
    except Exception as e:
        logger.error(f"Error updating grocery item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingredients/update', methods=['POST'])
@app.route('/update_ingredient', methods=['POST'])
def api_update_ingredient():
    """API endpoint to update recipe ingredient"""
    session = get_session()
    try:
        if request.is_json:
            data = request.get_json()
            recipe_id = data.get('recipe_id')
            old_ingredient = data.get('old_ingredient', '').strip()
            new_ingredient = data.get('new_ingredient', '').strip()
        else:
            recipe_id = request.form.get('recipe_id')
            old_ingredient = request.form.get('old_ingredient', '').strip()
            new_ingredient = request.form.get('new_ingredient', '').strip()
        
        if not all([recipe_id, old_ingredient, new_ingredient]):
            return jsonify({'error': 'Recipe ID, old ingredient, and new ingredient are required'}), 400
        
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # Update ingredient in the list
        ingredients = recipe.ingredients.copy()
        if old_ingredient in ingredients:
            index = ingredients.index(old_ingredient)
            ingredients[index] = new_ingredient
            recipe.ingredients = ingredients
            session.commit()
            
            return jsonify({'message': 'Ingredient updated successfully'})
        else:
            return jsonify({'error': 'Ingredient not found in recipe'}), 404
            
    except Exception as e:
        logger.error(f"Error updating ingredient: {e}")
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/pwa-debug/')
def pwa_debug():
    """PWA installation debug page"""
    return render_template('pwa_debug.html')


if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        
        # Always use Waitress WSGI server (production-grade)
        import threading
        import webbrowser
        import time
        from waitress import serve
        
        print("=" * 60)
        print("🍽️  QuickBasket - Production Server")
        print("=" * 60)
        print(f"Server: Waitress WSGI Server")
        print(f"Local: http://127.0.0.1:{port}")
        print(f"Network: http://192.168.1.17:{port} (for tablets)")
        print("=" * 60)
        print("✅ Progressive Web App - Installable on tablets")
        print("✅ Web scraping - Import recipes from URLs")
        print("✅ Offline support - Service worker caching")
        print("=" * 60)
        
        # Detect if running in cloud environment (no browser opening)
        is_cloud = os.environ.get('DYNO') or os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER')
        
        if not getattr(sys, 'frozen', False) and not is_cloud:
            # Open browser automatically when run locally (not in cloud)
            browser_thread = threading.Thread(
                target=lambda: (time.sleep(2), webbrowser.open(f'http://127.0.0.1:{port}'))
            )
            browser_thread.daemon = True
            browser_thread.start()
        
        # Start Waitress server
        host = '0.0.0.0'  # Bind to all interfaces for cloud hosting
        logger.info(f"Starting Waitress WSGI server on {host}:{port}")
        print(f"Environment: {'Cloud' if is_cloud else 'Local'}")
        serve(app, host=host, port=port, threads=6)
            
    except Exception as e:
        logger.error(f"Error starting Flask application: {e}")
        if not os.environ.get('DYNO'):  # Don't wait for input in cloud
            input("Press Enter to exit...")
        sys.exit(1)
