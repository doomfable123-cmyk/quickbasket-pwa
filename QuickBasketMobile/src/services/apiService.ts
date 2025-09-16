import axios from 'axios';

// Configuration for backend API
const API_BASE_URL = 'http://localhost:5000'; // Flask backend URL
const API_TIMEOUT = 30000; // 30 seconds timeout for web scraping

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Recipe {
  id: number;
  name: string;
  ingredients: string[];
  instructions?: string;
  url?: string;
  created_at: string;
}

export interface GroceryItem {
  name: string;
  checked: boolean;
}

// API Service Class
class ApiService {
  // Recipe methods
  async getRecipes(): Promise<Recipe[]> {
    try {
      const response = await api.get('/recipes');
      return response.data.recipes || [];
    } catch (error) {
      console.error('Error fetching recipes:', error);
      throw error;
    }
  }

  async deleteRecipe(id: number): Promise<void> {
    try {
      await api.delete(`/delete_recipe/${id}`);
    } catch (error) {
      console.error('Error deleting recipe:', error);
      throw error;
    }
  }

  async addRecipeFromUrl(url: string): Promise<Recipe> {
    try {
      const response = await api.post('/add_recipe_url', { url });
      return response.data;
    } catch (error) {
      console.error('Error adding recipe from URL:', error);
      throw error;
    }
  }

  async addManualRecipe(name: string, ingredients: string[], instructions?: string): Promise<Recipe> {
    try {
      const response = await api.post('/add_recipe_manual', {
        name,
        ingredients,
        instructions,
      });
      return response.data;
    } catch (error) {
      console.error('Error adding manual recipe:', error);
      throw error;
    }
  }

  // Grocery list methods
  async getGroceryList(): Promise<GroceryItem[]> {
    try {
      const response = await api.get('/grocery_list');
      return response.data.grocery_list || [];
    } catch (error) {
      console.error('Error fetching grocery list:', error);
      throw error;
    }
  }

  async updateGroceryItem(itemName: string, checked: boolean): Promise<void> {
    try {
      await api.post('/update_grocery_item', {
        item_name: itemName,
        checked: checked,
      });
    } catch (error) {
      console.error('Error updating grocery item:', error);
      throw error;
    }
  }

  async updateIngredient(recipeId: number, oldIngredient: string, newIngredient: string): Promise<void> {
    try {
      await api.post('/update_ingredient', {
        recipe_id: recipeId,
        old_ingredient: oldIngredient,
        new_ingredient: newIngredient,
      });
    } catch (error) {
      console.error('Error updating ingredient:', error);
      throw error;
    }
  }

  // Health check for backend connection
  async checkBackendHealth(): Promise<boolean> {
    try {
      const response = await api.get('/health', { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;