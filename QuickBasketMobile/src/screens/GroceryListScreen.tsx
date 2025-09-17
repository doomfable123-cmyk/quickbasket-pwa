import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import apiService, { GroceryItem } from '../services/apiService';

interface GroceryListScreenProps {
  navigation: any;
}

const GroceryListScreen: React.FC<GroceryListScreenProps> = ({ navigation }) => {
  const [groceryList, setGroceryList] = useState<GroceryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadGroceryList = async () => {
    try {
      const list = await apiService.getGroceryList();
      setGroceryList(list);
    } catch (error) {
      Alert.alert('Error', 'Failed to load grocery list. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadGroceryList();
    setRefreshing(false);
  };

  const toggleItem = async (itemName: string, currentChecked: boolean) => {
    try {
      await apiService.updateGroceryItem(itemName, !currentChecked);
      
      // Update local state
      setGroceryList(prevList =>
        prevList.map(item =>
          item.name === itemName ? { ...item, checked: !currentChecked } : item
        )
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to update item');
    }
  };

  const getStats = () => {
    const total = groceryList.length;
    const checked = groceryList.filter(item => item.checked).length;
    const progress = total > 0 ? (checked / total) * 100 : 0;
    return { total, checked, progress };
  };

  // Group items by checked status
  const uncheckedItems = groceryList.filter(item => !item.checked);
  const checkedItems = groceryList.filter(item => item.checked);

  useFocusEffect(
    useCallback(() => {
      loadGroceryList();
    }, [])
  );

  const stats = getStats();

  return (
    <SafeAreaView style={styles.container}>
      {/* Header with Stats */}
      <View style={styles.header}>
        <Text style={styles.title}>Smart Grocery List</Text>
        {!loading && groceryList.length > 0 && (
          <View style={styles.statsContainer}>
            <Text style={styles.statsText}>
              {stats.checked} of {stats.total} items completed
            </Text>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${stats.progress}%` }
                ]}
              />
            </View>
          </View>
        )}
      </View>

      {/* Grocery List */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }>
        {loading ? (
          <View style={styles.centerContainer}>
            <Text style={styles.loadingText}>Loading grocery list...</Text>
          </View>
        ) : groceryList.length === 0 ? (
          <View style={styles.centerContainer}>
            <Text style={styles.emptyText}>No grocery items found</Text>
            <Text style={styles.emptySubtext}>
              Add some recipes to generate your grocery list
            </Text>
            <TouchableOpacity
              style={styles.addRecipesButton}
              onPress={() => navigation.navigate('Recipes')}>
              <Text style={styles.addRecipesButtonText}>Browse Recipes</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.listContainer}>
            {/* Unchecked Items */}
            {uncheckedItems.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>
                  Shopping List ({uncheckedItems.length})
                </Text>
                <View style={styles.itemsList}>
                  {uncheckedItems.map((item, index) => (
                    <TouchableOpacity
                      key={`unchecked-${index}`}
                      style={[styles.groceryItem, styles.uncheckedItem]}
                      onPress={() => toggleItem(item.name, item.checked)}>
                      <View style={styles.checkbox}>
                        <Text style={styles.checkboxEmpty}>⚪</Text>
                      </View>
                      <Text style={styles.itemName}>{item.name}</Text>
                      <TouchableOpacity
                        style={styles.checkButton}
                        onPress={() => toggleItem(item.name, item.checked)}>
                        <Text style={styles.checkButtonText}>✓</Text>
                      </TouchableOpacity>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}

            {/* Checked Items */}
            {checkedItems.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>
                  Completed ({checkedItems.length})
                </Text>
                <View style={styles.itemsList}>
                  {checkedItems.map((item, index) => (
                    <TouchableOpacity
                      key={`checked-${index}`}
                      style={[styles.groceryItem, styles.checkedItem]}
                      onPress={() => toggleItem(item.name, item.checked)}>
                      <View style={styles.checkbox}>
                        <Text style={styles.checkboxChecked}>✅</Text>
                      </View>
                      <Text style={[styles.itemName, styles.checkedItemName]}>
                        {item.name}
                      </Text>
                      <TouchableOpacity
                        style={styles.uncheckButton}
                        onPress={() => toggleItem(item.name, item.checked)}>
                        <Text style={styles.uncheckButtonText}>↶</Text>
                      </TouchableOpacity>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}

            {/* Tips */}
            <View style={styles.tipsContainer}>
              <Text style={styles.tipsTitle}>💡 Smart Shopping Tips</Text>
              <Text style={styles.tipText}>
                • Items are automatically grouped from your recipes
              </Text>
              <Text style={styles.tipText}>
                • Tap items to check them off your list
              </Text>
              <Text style={styles.tipText}>
                • Add more recipes to expand your grocery list
              </Text>
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
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 12,
  },
  statsContainer: {
    marginBottom: 8,
  },
  statsText: {
    fontSize: 16,
    color: '#6c757d',
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#e9ecef',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#28a745',
    borderRadius: 3,
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
    marginBottom: 20,
  },
  addRecipesButton: {
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 8,
  },
  addRecipesButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  listContainer: {
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 12,
  },
  itemsList: {
    gap: 8,
  },
  groceryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 1,
  },
  uncheckedItem: {
    borderLeftWidth: 4,
    borderLeftColor: '#28a745',
  },
  checkedItem: {
    borderLeftWidth: 4,
    borderLeftColor: '#6c757d',
    backgroundColor: '#f8f9fa',
  },
  checkbox: {
    marginRight: 12,
  },
  checkboxEmpty: {
    fontSize: 20,
    color: '#dee2e6',
  },
  checkboxChecked: {
    fontSize: 20,
  },
  itemName: {
    flex: 1,
    fontSize: 16,
    color: '#495057',
  },
  checkedItemName: {
    textDecorationLine: 'line-through',
    color: '#6c757d',
  },
  checkButton: {
    backgroundColor: '#28a745',
    padding: 8,
    borderRadius: 4,
  },
  checkButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  uncheckButton: {
    backgroundColor: '#6c757d',
    padding: 8,
    borderRadius: 4,
  },
  uncheckButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  tipsContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginTop: 20,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 1,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c5530',
    marginBottom: 12,
  },
  tipText: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 6,
    lineHeight: 20,
  },
});

export default GroceryListScreen;