# Expo Development Rules

## Location Services

### Location Permission Handling
```typescript
import * as Location from 'expo-location';
import { Platform } from 'react-native';

export class LocationService {
  static async requestLocationPermission(): Promise<boolean> {
    if (Platform.OS === 'ios') {
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    } else {
      // Android handles permissions through Expo
      const { status } = await Location.requestForegroundPermissionsAsync();
      return status === 'granted';
    }
  }
  
  static async getCurrentLocation(): Promise<Location.LocationObject | null> {
    try {
      const permission = await this.requestLocationPermission();
      if (!permission) {
        return null;
      }
      
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });
      
      return location;
    } catch (error) {
      console.error('Error getting location:', error);
      return null;
    }
  }
  
  static async watchLocation(
    callback: (location: Location.LocationObject) => void
  ): Promise<{ remove: () => void } | null> {
    try {
      const permission = await this.requestLocationPermission();
      if (!permission) {
        return null;
      }
      
      const subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 1000,
          distanceInterval: 1,
        },
        callback
      );
      
      return subscription;
    } catch (error) {
      console.error('Error watching location:', error);
      return null;
    }
  }
}
```

## Push Notifications

### Expo Notifications Setup
```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export class NotificationService {
  static async setupPushNotifications(): Promise<string | null> {
    if (!Device.isDevice) {
      console.log('Must use physical device for Push Notifications');
      return null;
    }
    
    // Platform-specific notification setup
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }
    
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return null;
    }
    
    try {
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: 'your-project-id', // From app.json
      });
      return token.data;
    } catch (error) {
      console.error('Error getting push token:', error);
      return null;
    }
  }
  
  static async schedulePushNotification(
    title: string,
    body: string,
    data?: any,
    trigger?: Notifications.NotificationTriggerInput
  ) {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
      },
      trigger: trigger || { seconds: 2 },
    });
  }
  
  static setupNotificationListeners() {
    // Handle notification when app is foregrounded
    const notificationListener = Notifications.addNotificationReceivedListener(
      notification => {
        console.log('Notification received:', notification);
      }
    );
    
    // Handle notification response when user taps it
    const responseListener = Notifications.addNotificationResponseReceivedListener(
      response => {
        console.log('Notification response:', response);
        // Navigate based on notification data
        const data = response.notification.request.content.data;
        if (data.screen) {
          // Navigate to specific screen
        }
      }
    );
    
    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }
}
```

## Camera & Media

### Camera Integration
```typescript
import { Camera } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as ImagePicker from 'expo-image-picker';

export class CameraService {
  static async requestCameraPermissions(): Promise<boolean> {
    const { status } = await Camera.requestCameraPermissionsAsync();
    return status === 'granted';
  }
  
  static async requestMediaLibraryPermissions(): Promise<boolean> {
    const { status } = await MediaLibrary.requestPermissionsAsync();
    return status === 'granted';
  }
  
  static async pickImageFromLibrary(): Promise<string | null> {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (permission.granted === false) {
      return null;
    }
    
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });
    
    if (!result.canceled) {
      return result.assets[0].uri;
    }
    
    return null;
  }
  
  static async takePicture(): Promise<string | null> {
    const cameraPermission = await this.requestCameraPermissions();
    const mediaPermission = await this.requestMediaLibraryPermissions();
    
    if (!cameraPermission || !mediaPermission) {
      return null;
    }
    
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });
    
    if (!result.canceled) {
      return result.assets[0].uri;
    }
    
    return null;
  }
}
```

## File System & Storage

### Expo FileSystem
```typescript
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';

export class FileService {
  static get documentsDirectory() {
    return FileSystem.documentDirectory;
  }
  
  static async saveFile(content: string, filename: string): Promise<string | null> {
    try {
      const fileUri = `${FileSystem.documentDirectory}${filename}`;
      await FileSystem.writeAsStringAsync(fileUri, content);
      return fileUri;
    } catch (error) {
      console.error('Error saving file:', error);
      return null;
    }
  }
  
  static async readFile(filename: string): Promise<string | null> {
    try {
      const fileUri = `${FileSystem.documentDirectory}${filename}`;
      const content = await FileSystem.readAsStringAsync(fileUri);
      return content;
    } catch (error) {
      console.error('Error reading file:', error);
      return null;
    }
  }
  
  static async shareFile(fileUri: string): Promise<void> {
    try {
      const isAvailable = await Sharing.isAvailableAsync();
      if (isAvailable) {
        await Sharing.shareAsync(fileUri);
      }
    } catch (error) {
      console.error('Error sharing file:', error);
    }
  }
  
  static async downloadFile(url: string, filename: string): Promise<string | null> {
    try {
      const fileUri = `${FileSystem.documentDirectory}${filename}`;
      const downloadResult = await FileSystem.downloadAsync(url, fileUri);
      
      if (downloadResult.status === 200) {
        return downloadResult.uri;
      }
      
      return null;
    } catch (error) {
      console.error('Error downloading file:', error);
      return null;
    }
  }
}
```

## App Configuration

### app.json Configuration
```json
{
  "expo": {
    "name": "Your App Name",
    "slug": "your-app-slug",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourcompany.yourapp",
      "buildNumber": "1.0.0",
      "infoPlist": {
        "NSCameraUsageDescription": "This app uses the camera to take photos",
        "NSMicrophoneUsageDescription": "This app uses the microphone to record audio",
        "NSLocationWhenInUseUsageDescription": "This app uses location to provide location-based features"
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourcompany.yourapp",
      "versionCode": 1,
      "permissions": [
        "CAMERA",
        "RECORD_AUDIO",
        "ACCESS_FINE_LOCATION"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#ffffff"
        }
      ]
    ],
    "extra": {
      "eas": {
        "projectId": "your-project-id"
      }
    }
  }
}
```

## Development Build Configuration

### eas.json Configuration
```json
{
  "cli": {
    "version": ">= 5.9.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "resourceClass": "m-medium"
      }
    },
    "production": {
      "ios": {
        "resourceClass": "m-medium"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

## Bundle Optimization

### Metro Configuration for Expo
```javascript
// metro.config.js
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Enable Hermes
config.transformer.hermesCommand = 'hermes';

// Optimization settings
config.transformer.minifierConfig = {
  keep_fnames: false,
  mangle: true,
  compress: {
    drop_console: true,
    drop_debugger: true,
  },
};

// Asset extensions
config.resolver.assetExts.push('png', 'jpg', 'jpeg', 'gif', 'webp');

module.exports = config;
```

## Testing with Expo

### E2E Testing Setup with Detox
```javascript
// .detoxrc.js
module.exports = {
  testRunner: 'jest',
  runnerConfig: 'e2e/config.json',
  configurations: {
    'ios.sim.debug': {
      device: {
        type: 'ios.simulator',
        device: {
          type: 'iPhone 13',
        },
      },
      app: {
        type: 'ios.app',
        binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/YourApp.app',
        build: 'xcodebuild -workspace ios/YourApp.xcworkspace -scheme YourApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build',
      },
    },
    'android.emu.debug': {
      device: {
        type: 'android.emulator',
        device: {
          avdName: 'Pixel_3a_API_30_x86',
        },
      },
      app: {
        type: 'android.apk',
        binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
        build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
      },
    },
  },
};

// E2E test example
describe('User Registration Flow', () => {
  beforeAll(async () => {
    await device.launchApp({ 
      newInstance: true,
      permissions: { notifications: 'YES' }
    });
  });
  
  beforeEach(async () => {
    await device.reloadReactNative();
  });
  
  it('should complete registration successfully', async () => {
    // Navigate to registration
    await element(by.id('tab-profile')).tap();
    await element(by.id('sign-up-button')).tap();
    
    // Fill registration form
    await element(by.id('email-input')).typeText('new@example.com');
    await element(by.id('password-input')).typeText('SecurePass123!');
    await element(by.id('name-input')).typeText('New User');
    
    // Dismiss keyboard
    await element(by.id('name-input')).tapReturnKey();
    
    // Accept terms
    await element(by.id('terms-checkbox')).tap();
    
    // Submit
    await element(by.id('submit-button')).tap();
    
    // Verify success
    await expect(element(by.text('Welcome, New User!'))).toBeVisible();
  });
});
```

## Development Standards

### Expo Quality Checklist
- [ ] Proper permissions configured in app.json
- [ ] Push notifications working on physical devices
- [ ] Camera and media library integration tested
- [ ] Location services properly implemented
- [ ] File system operations secured
- [ ] Bundle optimized for production
- [ ] Development build configured
- [ ] E2E tests covering critical flows
- [ ] Proper error handling for device features
- [ ] Platform-specific configurations validated
- [ ] Over-the-air updates configured
- [ ] App store compliance verified