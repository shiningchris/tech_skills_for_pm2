# Document Explainer Mobile App

A simple mobile application that helps users understand legal documents, contracts, and agreements by explaining clauses and suggesting improvements.

## Features

### 1. Read Document
- **Upload Files**: Pick document files from your device (TXT, PDF, DOC)
- **Manual Input**: Paste or type document text directly
- **Sample Documents**: Try the app with pre-loaded sample contracts

### 2. Explain Main Clauses
- **Automatic Analysis**: Identifies and extracts main clauses from your document
- **Plain English Explanations**: Converts legal jargon into easy-to-understand language
- **Key Points Extraction**: Highlights the most important aspects of each clause
- **Importance Rating**: Categorizes clauses by their importance (High, Medium, Low)

### 3. Suggest Changes
- **Smart Recommendations**: Analyzes documents for common issues
- **Priority-Based**: Suggestions ranked by importance (High, Medium, Low)
- **Multiple Categories**: Covers clarity, completeness, readability, fairness, and structure
- **Actionable Advice**: Provides specific recommendations with expected benefits

## Technology Stack

- **React Native**: Cross-platform mobile framework
- **Expo**: Development platform and toolchain
- **React Native Paper**: Material Design component library
- **React Navigation**: Navigation and routing

## Installation

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Expo CLI

### Setup Instructions

1. **Install dependencies**
   ```bash
   cd mobile-app
   npm install
   ```

2. **Install Expo CLI globally** (if not already installed)
   ```bash
   npm install -g expo-cli
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Run on your device**
   - Install the "Expo Go" app on your iOS or Android device
   - Scan the QR code displayed in the terminal
   - The app will load on your device

### Alternative: Run on Emulator/Simulator

**For Android:**
```bash
npm run android
```

**For iOS (Mac only):**
```bash
npm run ios
```

**For Web:**
```bash
npm run web
```

## Project Structure

```
mobile-app/
├── App.js                      # Main app component
├── components/
│   ├── DocumentReader.js      # File upload and text input
│   ├── ClauseExplainer.js     # Clause analysis and explanation
│   └── ChangeSuggester.js     # Improvement suggestions
├── services/
│   └── DocumentAnalyzer.js    # Document analysis logic
├── package.json               # Dependencies and scripts
├── app.json                   # Expo configuration
└── README.md                  # This file
```

## How to Use

### Step 1: Load a Document
1. Open the app
2. On the "Read Document" tab:
   - **Option A**: Tap "Pick Document File" to upload a file from your device
   - **Option B**: Type or paste text in the manual input area and tap "Load Text"
   - **Option C**: Tap "Load Sample Contract" to try with example data

### Step 2: Explain Clauses
1. Switch to the "Explain Clauses" tab
2. Wait for the analysis to complete (1-2 seconds)
3. Tap on any clause to expand and see:
   - Full clause text
   - Plain English explanation
   - Key points
   - Importance level

### Step 3: Review Suggestions
1. Switch to the "Suggest Changes" tab
2. Wait for suggestions to be generated (1-2 seconds)
3. Review each suggestion:
   - Priority level (High/Medium/Low)
   - Category (Clarity, Completeness, Readability, etc.)
   - Issue description
   - Recommended changes
   - Expected benefits

## Features in Detail

### Document Analysis Engine
The app uses pattern matching and text analysis to:
- Identify document sections and clauses
- Recognize common legal terms and phrases
- Detect vague language, missing dates, and complex sentences
- Flag potentially one-sided terms

### Intelligent Explanations
Each clause is analyzed for:
- **Type**: Employment, compensation, termination, confidentiality, etc.
- **Key obligations**: What parties must or must not do
- **Importance**: How critical the clause is to the agreement

### Improvement Suggestions
The app checks for:
- **Vague language**: Terms like "reasonable," "timely," "appropriate"
- **Missing dates**: Lack of specific timeframes and deadlines
- **Complex sentences**: Overly long or convoluted text
- **Undefined terms**: Technical or important terms without definitions
- **Imbalanced terms**: Clauses heavily favoring one party
- **Poor structure**: Organization and formatting issues

## Limitations

This is a demonstration app with simplified analysis. For production use, consider:
- Integration with real NLP/AI services (OpenAI, Google Cloud NLP, etc.)
- Support for more document formats (PDF parsing, DOCX, etc.)
- Legal database integration for more accurate clause identification
- User authentication and document storage
- Export functionality (PDF reports, email, etc.)
- Multi-language support

## Future Enhancements

Potential improvements:
- [ ] AI-powered clause analysis using GPT or similar models
- [ ] PDF rendering and annotation
- [ ] Document comparison feature
- [ ] Template library for common contracts
- [ ] Collaboration features (share, comment)
- [ ] Offline mode with local storage
- [ ] Document version history
- [ ] Integration with cloud storage (Google Drive, Dropbox)

## Development Notes

### Customization

**To modify the analysis logic:**
Edit `services/DocumentAnalyzer.js` to change how clauses are identified or suggestions are generated.

**To change the UI:**
Edit component files in `components/` directory. The app uses React Native Paper components for consistent Material Design.

**To add new features:**
Create new components and import them in `App.js`. Update the tab navigation as needed.

## Support

For issues or questions:
- Check the console for error messages
- Ensure all dependencies are installed correctly
- Try clearing the Expo cache: `expo start -c`

## License

This project is created for educational purposes.

## Author

Created as part of the Technical Skills for PM course assignment.
