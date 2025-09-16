import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface HomeScreenProps {
  navigation: any;
}

const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>QuickBasket</Text>
          <Text style={styles.subtitle}>Smart Recipe & Grocery Manager</Text>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionCard, styles.recipesCard]}
            onPress={() => navigation.navigate('Recipes')}>
            <View style={styles.cardIcon}>
              <Text style={styles.cardIconText}>📖</Text>
            </View>
            <Text style={styles.cardTitle}>My Recipes</Text>
            <Text style={styles.cardSubtitle}>View and manage your saved recipes</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, styles.groceryCard]}
            onPress={() => navigation.navigate('GroceryList')}>
            <View style={styles.cardIcon}>
              <Text style={styles.cardIconText}>🛒</Text>
            </View>
            <Text style={styles.cardTitle}>Grocery List</Text>
            <Text style={styles.cardSubtitle}>Smart shopping list from your recipes</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, styles.addCard]}
            onPress={() => navigation.navigate('AddRecipe')}>
            <View style={styles.cardIcon}>
              <Text style={styles.cardIconText}>➕</Text>
            </View>
            <Text style={styles.cardTitle}>Add Recipe</Text>
            <Text style={styles.cardSubtitle}>Import from URL or add manually</Text>
          </TouchableOpacity>
        </View>

        {/* Features */}
        <View style={styles.featuresContainer}>
          <Text style={styles.featuresTitle}>Features</Text>
          <View style={styles.featuresList}>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>🌐</Text>
              <Text style={styles.featureText}>Import recipes from any URL</Text>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>📝</Text>
              <Text style={styles.featureText}>Add custom recipes manually</Text>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>🧠</Text>
              <Text style={styles.featureText}>Smart ingredient grouping</Text>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>✅</Text>
              <Text style={styles.featureText}>Interactive grocery lists</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#6c757d',
    textAlign: 'center',
  },
  actionsContainer: {
    marginBottom: 40,
  },
  actionCard: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 16,
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    alignItems: 'center',
  },
  recipesCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#2c5530',
  },
  groceryCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#28a745',
  },
  addCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#007bff',
  },
  cardIcon: {
    marginBottom: 12,
  },
  cardIconText: {
    fontSize: 40,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#6c757d',
    textAlign: 'center',
  },
  featuresContainer: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  featuresTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 16,
    textAlign: 'center',
  },
  featuresList: {
    gap: 12,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  featureIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#495057',
    flex: 1,
  },
});

export default HomeScreen;