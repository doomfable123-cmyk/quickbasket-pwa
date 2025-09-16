import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  TextInput,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import apiService, { Recipe } from '../services/apiService';

interface RecipesScreenProps {
  navigation: any;
}

const RecipesScreen: React.FC<RecipesScreenProps> = ({ navigation }) => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const loadRecipes = async () => {
    try {
      const fetchedRecipes = await apiService.getRecipes();
      setRecipes(fetchedRecipes);
    } catch (error) {
      Alert.alert('Error', 'Failed to load recipes. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadRecipes();
    setRefreshing(false);
  };

  const handleDeleteRecipe = async (id: number, name: string) => {
    Alert.alert(
      'Delete Recipe',
      `Are you sure you want to delete "${name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.deleteRecipe(id);
              setRecipes(recipes.filter(recipe => recipe.id !== id));
              Alert.alert('Success', 'Recipe deleted successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete recipe');
            }
          },
        },
      ]
    );
  };

  const filteredRecipes = recipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useFocusEffect(
    useCallback(() => {
      loadRecipes();
    }, [])
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search recipes..."
          value={searchTerm}
          onChangeText={setSearchTerm}
        />
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('AddRecipe')}>
          <Text style={styles.addButtonText}>+ Add Recipe</Text>
        </TouchableOpacity>
      </View>

      {/* Recipes List */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }>
        {loading ? (
          <View style={styles.centerContainer}>
            <Text style={styles.loadingText}>Loading recipes...</Text>
          </View>
        ) : filteredRecipes.length === 0 ? (
          <View style={styles.centerContainer}>
            <Text style={styles.emptyText}>
              {searchTerm ? 'No recipes match your search' : 'No recipes added yet'}
            </Text>
            <Text style={styles.emptySubtext}>
              {!searchTerm && 'Add your first recipe to get started!'}
            </Text>
          </View>
        ) : (
          <View style={styles.recipesList}>
            {filteredRecipes.map(recipe => (
              <View key={recipe.id} style={styles.recipeCard}>
                <View style={styles.recipeHeader}>
                  <Text style={styles.recipeName}>{recipe.name}</Text>
                  <TouchableOpacity
                    style={styles.deleteButton}
                    onPress={() => handleDeleteRecipe(recipe.id, recipe.name)}>
                    <Text style={styles.deleteButtonText}>🗑️</Text>
                  </TouchableOpacity>
                </View>

                <View style={styles.recipeInfo}>
                  <Text style={styles.ingredientsLabel}>
                    Ingredients ({recipe.ingredients.length}):
                  </Text>
                  <View style={styles.ingredientsList}>
                    {recipe.ingredients.slice(0, 3).map((ingredient, index) => (
                      <Text key={index} style={styles.ingredient}>
                        • {ingredient}
                      </Text>
                    ))}
                    {recipe.ingredients.length > 3 && (
                      <Text style={styles.moreIngredients}>
                        ... and {recipe.ingredients.length - 3} more
                      </Text>
                    )}
                  </View>
                </View>

                {recipe.url && (
                  <View style={styles.recipeSource}>
                    <Text style={styles.sourceLabel}>Source: </Text>
                    <Text style={styles.sourceUrl} numberOfLines={1}>
                      {recipe.url}
                    </Text>
                  </View>
                )}

                <Text style={styles.recipeDate}>
                  Added: {new Date(recipe.created_at).toLocaleDateString()}
                </Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Quick Actions */}
      {!loading && recipes.length > 0 && (
        <TouchableOpacity
          style={styles.groceryListButton}
          onPress={() => navigation.navigate('GroceryList')}>
          <Text style={styles.groceryListButtonText}>
            📋 View Grocery List ({recipes.length} recipes)
          </Text>
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  searchInput: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  addButton: {
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 18,
    color: '#6c757d',
  },
  emptyText: {
    fontSize: 18,
    color: '#6c757d',
    textAlign: 'center',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#adb5bd',
    textAlign: 'center',
  },
  recipesList: {
    padding: 20,
    gap: 16,
  },
  recipeCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    borderLeftWidth: 4,
    borderLeftColor: '#28a745',
  },
  recipeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  recipeName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c5530',
    flex: 1,
    marginRight: 12,
  },
  deleteButton: {
    padding: 4,
  },
  deleteButtonText: {
    fontSize: 18,
    color: '#dc3545',
  },
  recipeInfo: {
    marginBottom: 12,
  },
  ingredientsLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 6,
  },
  ingredientsList: {
    gap: 2,
  },
  ingredient: {
    fontSize: 14,
    color: '#6c757d',
    lineHeight: 18,
  },
  moreIngredients: {
    fontSize: 14,
    color: '#adb5bd',
    fontStyle: 'italic',
  },
  recipeSource: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  sourceLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#495057',
  },
  sourceUrl: {
    fontSize: 12,
    color: '#007bff',
    flex: 1,
  },
  recipeDate: {
    fontSize: 12,
    color: '#adb5bd',
  },
  groceryListButton: {
    backgroundColor: '#2c5530',
    margin: 20,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  groceryListButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default RecipesScreen;