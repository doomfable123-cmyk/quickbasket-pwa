import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import apiService from '../services/apiService';

interface AddRecipeScreenProps {
  navigation: any;
}

const AddRecipeScreen: React.FC<AddRecipeScreenProps> = ({ navigation }) => {
  const [activeTab, setActiveTab] = useState<'url' | 'manual'>('url');
  
  // URL form state
  const [url, setUrl] = useState('');
  const [urlLoading, setUrlLoading] = useState(false);
  
  // Manual form state
  const [manualName, setManualName] = useState('');
  const [manualIngredients, setManualIngredients] = useState('');
  const [manualInstructions, setManualInstructions] = useState('');
  const [manualLoading, setManualLoading] = useState(false);

  const handleAddFromUrl = async () => {
    if (!url.trim()) {
      Alert.alert('Error', 'Please enter a recipe URL');
      return;
    }

    // Validate URL format
    try {
      new URL(url);
    } catch {
      Alert.alert('Error', 'Please enter a valid URL');
      return;
    }

    setUrlLoading(true);
    try {
      await apiService.addRecipeFromUrl(url.trim());
      Alert.alert(
        'Success',
        'Recipe added successfully!',
        [
          {
            text: 'Add Another',
            onPress: () => setUrl(''),
          },
          {
            text: 'View Recipes',
            onPress: () => navigation.navigate('Recipes'),
          },
        ]
      );
    } catch (error: any) {
      console.error('Add recipe error:', error);
      
      let errorMessage = 'Failed to add recipe from URL. ';
      if (error.response?.status === 400) {
        errorMessage += 'The website may not be supported or accessible.';
      } else if (error.response?.status === 500) {
        errorMessage += 'Server error while processing the recipe.';
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage += 'Please check your internet connection.';
      } else {
        errorMessage += 'Please try again or add the recipe manually.';
      }
      
      Alert.alert('Error', errorMessage);
    } finally {
      setUrlLoading(false);
    }
  };

  const handleAddManual = async () => {
    if (!manualName.trim()) {
      Alert.alert('Error', 'Please enter a recipe name');
      return;
    }
    
    if (!manualIngredients.trim()) {
      Alert.alert('Error', 'Please enter at least one ingredient');
      return;
    }

    setManualLoading(true);
    try {
      // Parse ingredients (split by lines, commas, or semicolons)
      const ingredientsList = manualIngredients
        .split(/[,;\n]/)
        .map(ingredient => ingredient.trim())
        .filter(ingredient => ingredient.length > 0);

      await apiService.addManualRecipe(
        manualName.trim(),
        ingredientsList,
        manualInstructions.trim() || undefined
      );

      Alert.alert(
        'Success',
        'Recipe added successfully!',
        [
          {
            text: 'Add Another',
            onPress: () => {
              setManualName('');
              setManualIngredients('');
              setManualInstructions('');
            },
          },
          {
            text: 'View Recipes',
            onPress: () => navigation.navigate('Recipes'),
          },
        ]
      );
    } catch (error) {
      console.error('Add manual recipe error:', error);
      Alert.alert('Error', 'Failed to add recipe. Please try again.');
    } finally {
      setManualLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'url' && styles.activeTab]}
          onPress={() => setActiveTab('url')}>
          <Text style={[styles.tabText, activeTab === 'url' && styles.activeTabText]}>
            🌐 From URL
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'manual' && styles.activeTab]}
          onPress={() => setActiveTab('manual')}>
          <Text style={[styles.tabText, activeTab === 'manual' && styles.activeTabText]}>
            ✏️ Manual Entry
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {activeTab === 'url' ? (
          /* URL Tab Content */
          <View style={styles.formContainer}>
            <Text style={styles.formTitle}>Import Recipe from URL</Text>
            <Text style={styles.formSubtitle}>
              Enter any recipe URL and we'll automatically extract the ingredients and details
            </Text>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Recipe URL *</Text>
              <TextInput
                style={styles.textInput}
                placeholder="https://example.com/recipe"
                value={url}
                onChangeText={setUrl}
                autoCapitalize="none"
                keyboardType="url"
                editable={!urlLoading}
              />
            </View>

            <TouchableOpacity
              style={[styles.submitButton, urlLoading && styles.disabledButton]}
              onPress={handleAddFromUrl}
              disabled={urlLoading}>
              {urlLoading ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator color="#fff" size="small" />
                  <Text style={styles.submitButtonText}>Importing Recipe...</Text>
                </View>
              ) : (
                <Text style={styles.submitButtonText}>Import Recipe</Text>
              )}
            </TouchableOpacity>

            {/* Supported Sites Info */}
            <View style={styles.infoContainer}>
              <Text style={styles.infoTitle}>✨ Supported Features</Text>
              <Text style={styles.infoText}>• Automatic ingredient extraction</Text>
              <Text style={styles.infoText}>• Recipe name detection</Text>
              <Text style={styles.infoText}>• Works with most recipe websites</Text>
              <Text style={styles.infoText}>• Instant grocery list integration</Text>
            </View>
          </View>
        ) : (
          /* Manual Tab Content */
          <View style={styles.formContainer}>
            <Text style={styles.formTitle}>Add Recipe Manually</Text>
            <Text style={styles.formSubtitle}>
              Enter your recipe details manually for complete control
            </Text>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Recipe Name *</Text>
              <TextInput
                style={styles.textInput}
                placeholder="Enter recipe name"
                value={manualName}
                onChangeText={setManualName}
                editable={!manualLoading}
              />
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Ingredients *</Text>
              <Text style={styles.inputHint}>
                Enter each ingredient on a new line or separated by commas
              </Text>
              <TextInput
                style={[styles.textInput, styles.multilineInput]}
                placeholder="1 cup flour&#10;2 eggs&#10;1/2 cup milk"
                value={manualIngredients}
                onChangeText={setManualIngredients}
                multiline
                numberOfLines={6}
                textAlignVertical="top"
                editable={!manualLoading}
              />
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Instructions (Optional)</Text>
              <TextInput
                style={[styles.textInput, styles.multilineInput]}
                placeholder="Enter cooking instructions..."
                value={manualInstructions}
                onChangeText={setManualInstructions}
                multiline
                numberOfLines={4}
                textAlignVertical="top"
                editable={!manualLoading}
              />
            </View>

            <TouchableOpacity
              style={[styles.submitButton, manualLoading && styles.disabledButton]}
              onPress={handleAddManual}
              disabled={manualLoading}>
              {manualLoading ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator color="#fff" size="small" />
                  <Text style={styles.submitButtonText}>Adding Recipe...</Text>
                </View>
              ) : (
                <Text style={styles.submitButtonText}>Add Recipe</Text>
              )}
            </TouchableOpacity>

            {/* Tips */}
            <View style={styles.infoContainer}>
              <Text style={styles.infoTitle}>💡 Tips</Text>
              <Text style={styles.infoText}>• Use specific measurements (1 cup, 2 tbsp)</Text>
              <Text style={styles.infoText}>• Separate ingredients with commas or new lines</Text>
              <Text style={styles.infoText}>• Instructions are optional but helpful</Text>
              <Text style={styles.infoText}>• Your recipe will appear in the grocery list</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  tab: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#28a745',
  },
  tabText: {
    fontSize: 16,
    color: '#6c757d',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#28a745',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  formContainer: {
    padding: 20,
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 8,
  },
  formSubtitle: {
    fontSize: 16,
    color: '#6c757d',
    marginBottom: 24,
    lineHeight: 22,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 6,
  },
  inputHint: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  textInput: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#dee2e6',
    fontSize: 16,
  },
  multilineInput: {
    height: 120,
  },
  submitButton: {
    backgroundColor: '#28a745',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 20,
  },
  disabledButton: {
    backgroundColor: '#6c757d',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 1,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 6,
    lineHeight: 20,
  },
});

export default AddRecipeScreen;