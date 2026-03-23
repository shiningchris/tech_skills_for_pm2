import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import {
  Card,
  Button,
  Text,
  TextInput,
  HelperText,
} from 'react-native-paper';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

export default function DocumentReader({ onDocumentLoaded }) {
  const [manualText, setManualText] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePickDocument = async () => {
    try {
      setLoading(true);
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/*', 'application/pdf', 'application/msword'],
        copyToCacheDirectory: true,
      });

      if (result.type === 'success') {
        const fileContent = await FileSystem.readAsStringAsync(result.uri);
        onDocumentLoaded(fileContent, result.name);
        Alert.alert('Success', 'Document loaded successfully!');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load document: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleManualInput = () => {
    if (manualText.trim()) {
      onDocumentLoaded(manualText, 'Manual Input');
      Alert.alert('Success', 'Text loaded successfully!');
    } else {
      Alert.alert('Error', 'Please enter some text');
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Upload Document" />
        <Card.Content>
          <Text variant="bodyMedium" style={styles.description}>
            Choose a document file from your device to analyze
          </Text>
          <Button
            mode="contained"
            onPress={handlePickDocument}
            loading={loading}
            disabled={loading}
            icon="file-upload"
            style={styles.button}
          >
            Pick Document File
          </Button>
          <HelperText type="info">
            Supported formats: TXT, PDF, DOC
          </HelperText>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Or Enter Text Manually" />
        <Card.Content>
          <TextInput
            mode="outlined"
            multiline
            numberOfLines={10}
            value={manualText}
            onChangeText={setManualText}
            placeholder="Paste or type your document text here..."
            style={styles.textInput}
          />
          <Button
            mode="contained-tonal"
            onPress={handleManualInput}
            icon="text-box-check"
            style={styles.button}
          >
            Load Text
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Sample Documents" />
        <Card.Content>
          <Button
            mode="outlined"
            onPress={() => {
              const sampleContract = `EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into on January 1, 2024.

1. POSITION AND DUTIES
The Employee shall serve as Senior Software Engineer and shall perform duties as assigned by the supervisor.

2. COMPENSATION
The Employee shall receive an annual salary of $100,000, payable in accordance with company payroll practices.

3. BENEFITS
The Employee shall be entitled to participate in all standard benefit programs including health insurance, retirement plans, and paid time off.

4. TERMINATION
Either party may terminate this agreement with 30 days written notice.

5. CONFIDENTIALITY
The Employee agrees to maintain confidentiality of all proprietary information.`;

              onDocumentLoaded(sampleContract, 'Sample Employment Contract');
              Alert.alert('Success', 'Sample contract loaded!');
            }}
            icon="file-document"
            style={styles.sampleButton}
          >
            Load Sample Contract
          </Button>
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  card: {
    marginBottom: 15,
    elevation: 2,
  },
  description: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
  },
  sampleButton: {
    marginTop: 5,
  },
  textInput: {
    marginBottom: 10,
    minHeight: 150,
  },
});
