import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    // Sign.com brand colors
    primary: '#FFEE55',           // Lighter (yellow) - primary CTA color
    primaryContainer: '#FFF9C4',  // Light yellow container
    secondary: '#1D2228',         // Petrol (dark blue-gray)
    secondaryContainer: '#F5F5F5', // Light gray

    // Background & surface
    background: '#F5F5F5',        // Light gray background
    surface: '#FFFFFF',           // White cards/surfaces
    surfaceVariant: '#FAFAFA',    // Off-white variant

    // Status colors
    error: '#D32F2F',             // Red
    success: '#00C853',           // Green
    warning: '#FF9800',           // Orange
    info: '#90CDF4',              // Hybrid (light blue)

    // Text colors
    onPrimary: '#1D2228',         // Dark text on yellow buttons
    onSecondary: '#FFFFFF',       // White text on dark backgrounds
    onBackground: '#1D2228',      // Dark text on light background
    onSurface: '#1D2228',         // Dark text on white surfaces
    onSurfaceVariant: '#666666',  // Medium gray for secondary text

    // UI elements
    outline: '#E0E0E0',           // Light gray borders
    outlineVariant: '#EEEEEE',    // Subtle dividers
  },
  roundness: 24, // Fully rounded buttons (sign.com style)
};
