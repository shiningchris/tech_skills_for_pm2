import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import {
  Provider as PaperProvider,
  Appbar,
  Card,
  Button,
  Text,
  Chip,
  Portal,
  Modal,
  Divider,
} from 'react-native-paper';
import DocumentReader from './components/DocumentReader';
import ClauseExplainer from './components/ClauseExplainer';
import ChangeSuggester from './components/ChangeSuggester';

export default function App() {
  const [documentText, setDocumentText] = useState('');
  const [documentName, setDocumentName] = useState('');
  const [activeTab, setActiveTab] = useState('reader');

  const handleDocumentLoaded = (text, name) => {
    setDocumentText(text);
    setDocumentName(name);
  };

  return (
    <PaperProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />

        <Appbar.Header>
          <Appbar.Content title="Document Explainer" />
        </Appbar.Header>

        {documentName ? (
          <Card style={styles.documentCard}>
            <Card.Content>
              <Text variant="labelSmall">Current Document:</Text>
              <Text variant="titleMedium">{documentName}</Text>
            </Card.Content>
          </Card>
        ) : null}

        <View style={styles.tabContainer}>
          <Chip
            selected={activeTab === 'reader'}
            onPress={() => setActiveTab('reader')}
            style={styles.tab}
          >
            Read Document
          </Chip>
          <Chip
            selected={activeTab === 'explain'}
            onPress={() => setActiveTab('explain')}
            style={styles.tab}
            disabled={!documentText}
          >
            Explain Clauses
          </Chip>
          <Chip
            selected={activeTab === 'suggest'}
            onPress={() => setActiveTab('suggest')}
            style={styles.tab}
            disabled={!documentText}
          >
            Suggest Changes
          </Chip>
        </View>

        <ScrollView style={styles.content}>
          {activeTab === 'reader' && (
            <DocumentReader onDocumentLoaded={handleDocumentLoaded} />
          )}
          {activeTab === 'explain' && (
            <ClauseExplainer documentText={documentText} />
          )}
          {activeTab === 'suggest' && (
            <ChangeSuggester documentText={documentText} />
          )}
        </ScrollView>
      </SafeAreaView>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  documentCard: {
    margin: 10,
    elevation: 2,
  },
  tabContainer: {
    flexDirection: 'row',
    padding: 10,
    justifyContent: 'space-around',
    backgroundColor: '#fff',
  },
  tab: {
    marginHorizontal: 4,
  },
  content: {
    flex: 1,
    padding: 10,
  },
});
