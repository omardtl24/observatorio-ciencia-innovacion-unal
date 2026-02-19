/**
 * Local Storage Manager
 * Provides utility functions for managing data in browser's localStorage.
 */

/**
 * Set an item in localStorage
 * @param {string} key - The key to store the value under
 * @param {string} value - The value to store
 */
export function setItem(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    console.error(`Error setting localStorage item '${key}':`, error);
  }
}

/**
 * Get an item from localStorage
 * @param {string} key - The key to retrieve
 * @returns {string|null} The value, or null if not found
 */
export function getItem(key) {
  try {
    return localStorage.getItem(key);
  } catch (error) {
    console.error(`Error getting localStorage item '${key}':`, error);
    return null;
  }
}

/**
 * Remove an item from localStorage
 * @param {string} key - The key to remove
 */
export function removeItem(key) {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Error removing localStorage item '${key}':`, error);
  }
}

/**
 * Clear all items from localStorage
 */
export function clear() {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('Error clearing localStorage:', error);
  }
}
