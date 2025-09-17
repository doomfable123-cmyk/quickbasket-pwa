/**
 * QuickBasket Mobile App
 * Recipe and Grocery List Manager for Android Tablets
 *
 * @format
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar, useColorScheme } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import HomeScreen from './src/screens/HomeScreen';
import RecipesScreen from './src/screens/RecipesScreen';
import GroceryListScreen from './src/screens/GroceryListScreen';
import AddRecipeScreen from './src/screens/AddRecipeScreen';
import ErrorBoundary from './src/components/ErrorBoundary';

const Stack = createStackNavigator();

function App() {
  const isDarkMode = useColorScheme() === 'dark';

  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <NavigationContainer>
          <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
          <Stack.Navigator
            initialRouteName="Home"
            screenOptions={{
              headerStyle: {
                backgroundColor: '#2c5530',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
                fontSize: 20,
              },
            }}>
            <Stack.Screen 
              name="Home" 
              component={HomeScreen}
              options={{ title: 'QuickBasket' }}
            />
            <Stack.Screen 
              name="Recipes" 
              component={RecipesScreen}
              options={{ title: 'My Recipes' }}
            />
            <Stack.Screen 
              name="GroceryList" 
              component={GroceryListScreen}
              options={{ title: 'Grocery List' }}
            />
            <Stack.Screen 
              name="AddRecipe" 
              component={AddRecipeScreen}
              options={{ title: 'Add Recipe' }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}

export default App;
