# React Native Development Rules

## Mobile Component Structure

### React Native Component Pattern

```tsx
import React, { useState, useCallback, useMemo, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
  Animated,
  Dimensions,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useNetInfo } from "@react-native-community/netinfo";
import AsyncStorage from "@react-native-async-storage/async-storage";

interface UserProfileProps {
  userId: string;
  onRefresh?: () => Promise<void>;
}

export function UserProfile({ userId, onRefresh }: UserProfileProps) {
  const insets = useSafeAreaInsets();
  const netInfo = useNetInfo();
  const scrollY = useRef(new Animated.Value(0)).current;

  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Implementation continues...
}
```

### Offline-First Data Loading

```tsx
// Offline-first data loading with AsyncStorage
const loadUser = useCallback(async () => {
  try {
    // Try cache first
    const cached = await AsyncStorage.getItem(`user_${userId}`);
    if (cached) {
      setUser(JSON.parse(cached));
      setLoading(false);
    }

    // Fetch fresh data if online
    if (netInfo.isConnected) {
      const response = await fetch(`/api/users/${userId}`);
      const data = await response.json();

      // Update cache
      await AsyncStorage.setItem(`user_${userId}`, JSON.stringify(data));
      setUser(data);
    }
  } catch (error) {
    console.error("Failed to load user:", error);
    // Show cached data or error state
  } finally {
    setLoading(false);
  }
}, [userId, netInfo.isConnected]);

// Pull-to-refresh handling
const handleRefresh = useCallback(async () => {
  setRefreshing(true);
  try {
    await onRefresh?.();
    await loadUser();
  } finally {
    setRefreshing(false);
  }
}, [onRefresh, loadUser]);
```

## Platform-Specific Implementation

### Platform Services

```tsx
import { Platform, PermissionsAndroid, Linking } from "react-native";
import * as Location from "expo-location";
import * as Notifications from "expo-notifications";

export class PlatformServices {
  // Location permissions
  static async requestLocationPermission(): Promise<boolean> {
    if (Platform.OS === "ios") {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === "granted";
    } else {
      // Android requires additional handling
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: "Location Permission",
          message: "This app needs access to your location",
          buttonNeutral: "Ask Me Later",
          buttonNegative: "Cancel",
          buttonPositive: "OK",
        },
      );
      return granted === PermissionsAndroid.RESULTS.GRANTED;
    }
  }

  // Push notification setup
  static async setupPushNotifications(): Promise<string | null> {
    // Platform-specific notification setup
    if (Platform.OS === "android") {
      await Notifications.setNotificationChannelAsync("default", {
        name: "default",
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: "#FF231F7C",
      });
    }

    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== "granted") {
      return null;
    }

    const token = await Notifications.getExpoPushTokenAsync();
    return token.data;
  }

  // Deep linking
  static async openSettings(): Promise<void> {
    if (Platform.OS === "ios") {
      await Linking.openURL("app-settings:");
    } else {
      await Linking.openSettings();
    }
  }
}
```

## Navigation Patterns

### Type-Safe Navigation

```tsx
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { enableScreens } from "react-native-screens";

// Enable native screens for performance
enableScreens();

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Type-safe navigation
export type RootStackParamList = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};

export type TabParamList = {
  Feed: undefined;
  Search: undefined;
  Profile: undefined;
};

// Navigation setup with proper typing
export function AppNavigator() {
  return (
    <NavigationContainer
      linking={{
        prefixes: ["myapp://", "https://myapp.com"],
        config: {
          screens: {
            Home: "",
            Profile: "user/:userId",
            Settings: "settings",
          },
        },
      }}
    >
      <Stack.Navigator
        screenOptions={{
          headerLargeTitle: true,
          headerTransparent: Platform.OS === "ios",
          headerBlurEffect: "regular",
        }}
      >
        <Stack.Screen name="Home" component={TabNavigator} />
        <Stack.Screen
          name="Profile"
          component={ProfileScreen}
          options={({ route }) => ({
            title: route.params?.userId || "Profile",
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## State Management for Mobile

### Zustand with Persistence

```typescript
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";
import NetInfo from "@react-native-community/netinfo";

interface AppState {
  // State
  user: User | null;
  isOnline: boolean;
  syncQueue: SyncItem[];

  // Actions
  setUser: (user: User | null) => void;
  setOnline: (online: boolean) => void;
  addToSyncQueue: (item: SyncItem) => void;
  processSyncQueue: () => Promise<void>;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isOnline: true,
      syncQueue: [],

      // Actions
      setUser: (user) => set({ user }),

      setOnline: (isOnline) => set({ isOnline }),

      addToSyncQueue: (item) =>
        set((state) => ({
          syncQueue: [...state.syncQueue, item],
        })),

      processSyncQueue: async () => {
        const { syncQueue, isOnline } = get();
        if (!isOnline || syncQueue.length === 0) return;

        const processed: string[] = [];

        for (const item of syncQueue) {
          try {
            await syncItem(item);
            processed.push(item.id);
          } catch (error) {
            console.error("Sync failed:", error);
          }
        }

        set((state) => ({
          syncQueue: state.syncQueue.filter(
            (item) => !processed.includes(item.id),
          ),
        }));
      },
    }),
    {
      name: "app-storage",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        syncQueue: state.syncQueue,
      }),
    },
  ),
);

// Network monitoring
NetInfo.addEventListener((state) => {
  useAppStore.getState().setOnline(state.isConnected ?? false);

  // Process sync queue when coming online
  if (state.isConnected) {
    useAppStore.getState().processSyncQueue();
  }
});
```

## Animation Patterns

### Animated Header

```tsx
// Animated header with scroll
const headerOpacity = scrollY.interpolate({
  inputRange: [0, 100],
  outputRange: [0, 1],
  extrapolate: "clamp",
});

return (
  <View style={[styles.container, { paddingTop: insets.top }]}>
    {/* Animated Header */}
    <Animated.View style={[styles.header, { opacity: headerOpacity }]}>
      <Text style={styles.headerTitle}>{user?.name}</Text>
    </Animated.View>

    {/* Scrollable Content */}
    <Animated.ScrollView
      contentContainerStyle={{ paddingBottom: insets.bottom }}
      onScroll={Animated.event(
        [{ nativeEvent: { contentOffset: { y: scrollY } } }],
        { useNativeDriver: true },
      )}
      scrollEventThrottle={16}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      <UserContent user={user} />
    </Animated.ScrollView>
  </View>
);
```

## Styling Patterns

### Platform-Specific Styles

```tsx
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F5F5",
  },
  header: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 88,
    backgroundColor: "white",
    justifyContent: "flex-end",
    paddingBottom: 12,
    paddingHorizontal: 16,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: "600",
    color: "#000",
  },
  offlineBanner: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "#FF3B30",
    paddingVertical: 8,
    alignItems: "center",
  },
  offlineText: {
    color: "white",
    fontSize: 14,
    fontWeight: "500",
  },
});
```

## Performance Optimization

### Optimized List Components

```tsx
import React, { memo, useCallback, useMemo } from "react";
import { FlatList, Image, Text, View } from "react-native";
import FastImage from "react-native-fast-image";
import { FlashList } from "@shopify/flash-list";

// Optimized list item
const ListItem = memo<ItemProps>(({ item, onPress }) => {
  const handlePress = useCallback(() => {
    onPress(item.id);
  }, [item.id, onPress]);

  return (
    <TouchableOpacity onPress={handlePress}>
      <View style={styles.listItem}>
        <FastImage
          style={styles.avatar}
          source={{
            uri: item.avatarUrl,
            priority: FastImage.priority.normal,
          }}
          resizeMode={FastImage.resizeMode.cover}
        />
        <Text style={styles.title}>{item.title}</Text>
      </View>
    </TouchableOpacity>
  );
});

// Optimized list component
export function OptimizedList({ data, onItemPress }) {
  // Key extractor
  const keyExtractor = useCallback((item) => item.id, []);

  // Render item
  const renderItem = useCallback(
    ({ item }) => <ListItem item={item} onPress={onItemPress} />,
    [onItemPress],
  );

  return (
    <FlashList
      data={data}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      estimatedItemSize={ITEM_HEIGHT}
      removeClippedSubviews
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={10}
      onEndReachedThreshold={0.5}
      maintainVisibleContentPosition={{
        minIndexForVisible: 0,
      }}
    />
  );
}
```

## Testing Patterns

### React Native Testing

```typescript
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { UserProfile } from '@/components/UserProfile';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Mock native modules
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}));

jest.mock('@react-native-community/netinfo', () => ({
  useNetInfo: () => ({ isConnected: true }),
}));

describe('UserProfile', () => {
  const mockUser = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should load cached data when offline', async () => {
    // Setup
    AsyncStorage.getItem.mockResolvedValue(JSON.stringify(mockUser));

    // Render with offline state
    const { getByText } = render(
      <NavigationContainer>
        <UserProfile userId="123" />
      </NavigationContainer>
    );

    // Verify cached data is displayed
    await waitFor(() => {
      expect(getByText('John Doe')).toBeTruthy();
    });

    expect(AsyncStorage.getItem).toHaveBeenCalledWith('user_123');
  });

  it('should handle pull-to-refresh', async () => {
    const onRefresh = jest.fn();

    const { getByTestId } = render(
      <NavigationContainer>
        <UserProfile userId="123" onRefresh={onRefresh} />
      </NavigationContainer>
    );

    // Trigger refresh
    const scrollView = getByTestId('user-scroll-view');
    fireEvent.scroll(scrollView, {
      nativeEvent: {
        contentOffset: { y: -100 },
      },
    });

    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalled();
    });
  });
});
```

## Development Standards

### React Native Quality Checklist

- [ ] Works on iOS 13+ and Android 6+
- [ ] Handles device rotation correctly
- [ ] Responds to keyboard appearance
- [ ] Works offline with proper sync
- [ ] Respects platform UI guidelines
- [ ] Optimized bundle size (<50MB)
- [ ] 60fps animations
- [ ] Accessibility compliant
- [ ] Push notifications working
- [ ] Deep linking configured
- [ ] Proper error handling and loading states
- [ ] Platform-specific code properly abstracted
- [ ] Performance optimized for mobile devices
