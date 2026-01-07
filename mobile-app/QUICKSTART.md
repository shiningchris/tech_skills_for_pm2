# Quick Start Guide

Get the Document Explainer app running in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
cd mobile-app
npm install
```

## Step 2: Start the App (1 minute)

```bash
npm start
```

This will open Expo DevTools in your browser and show a QR code.

## Step 3: Run on Your Device (2 minutes)

### On Your Phone:
1. Install "Expo Go" from App Store (iOS) or Play Store (Android)
2. Open Expo Go app
3. Scan the QR code from your terminal
4. Wait for the app to load

### On Your Computer:
- Press `w` in the terminal to open in web browser
- Press `a` for Android emulator
- Press `i` for iOS simulator (Mac only)

## That's It!

You should now see the Document Explainer app running. Try:
1. Tap "Load Sample Contract" to see it in action
2. Switch to "Explain Clauses" tab to see analysis
3. Switch to "Suggest Changes" tab for recommendations

## Troubleshooting

**App won't start?**
```bash
expo start -c  # Clear cache
```

**Can't scan QR code?**
- Make sure your phone and computer are on the same WiFi network
- Try pressing `t` in terminal to send a link via SMS/email

**Dependencies error?**
```bash
rm -rf node_modules
npm install
```
