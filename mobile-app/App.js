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
import { theme } from './theme';
import DocumentReader from './components/DocumentReader';
import ClauseExplainer from './components/ClauseExplainer';
import ChangeSuggester from './components/ChangeSuggester';
import ClauseComments from './components/ClauseComments';
import ResearchParticipationModal from './components/ResearchParticipationModal';
import ConfirmationScreen from './components/ConfirmationScreen';
import * as ResearchService from './services/ResearchService';

export default function App() {
  // Document state
  const [documentText, setDocumentText] = useState('');
  const [documentName, setDocumentName] = useState('');
  const [activeTab, setActiveTab] = useState('reader');

  // Lifted state from child components
  const [clauses, setClauses] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [comments, setComments] = useState({}); // keyed by clauseId or 'general'

  // Research participation state
  const [participantData, setParticipantData] = useState(null);
  const [researchSubmitted, setResearchSubmitted] = useState(false);
  const [showResearchModal, setShowResearchModal] = useState(false);
  const [flowStep, setFlowStep] = useState(0); // 0=reading, 1=analyzed, 2=commented, 3=submitted

  const handleDocumentLoaded = (text, name) => {
    setDocumentText(text);
    setDocumentName(name);
  };

  const handleClausesAnalyzed = (analyzedClauses) => {
    setClauses(analyzedClauses);
    setFlowStep(1); // User has analyzed clauses
  };

  const handleSuggestionsGenerated = (generatedSuggestions) => {
    setSuggestions(generatedSuggestions);
  };

  const addComment = (clauseId, text) => {
    const newComment = {
      id: Date.now().toString(),
      text,
      timestamp: new Date().toISOString(),
    };
    setComments((prev) => ({
      ...prev,
      [clauseId]: [...(prev[clauseId] || []), newComment],
    }));
    setFlowStep(2); // User has added comments
  };

  return (
    <PaperProvider theme={theme}>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" />

        <Appbar.Header>
          <Appbar.Content title="Contract Analyzer" />
        </Appbar.Header>

        {documentName ? (
          <Card style={styles.documentCard}>
            <Card.Content>
              <Text variant="labelSmall">Current Document:</Text>
              <Text variant="titleMedium">{documentName}</Text>
            </Card.Content>
          </Card>
        ) : null}

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.tabContainer}
          contentContainerStyle={styles.tabContent}
        >
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
          <Chip
            selected={activeTab === 'comments'}
            onPress={() => setActiveTab('comments')}
            style={styles.tab}
            disabled={clauses.length === 0}
          >
            Comments
          </Chip>
          {researchSubmitted && (
            <Chip
              selected={activeTab === 'confirmation'}
              onPress={() => setActiveTab('confirmation')}
              style={styles.tab}
            >
              Confirmation
            </Chip>
          )}
        </ScrollView>

        <ScrollView style={styles.content}>
          {activeTab === 'reader' && (
            <DocumentReader onDocumentLoaded={handleDocumentLoaded} />
          )}
          {activeTab === 'explain' && (
            <ClauseExplainer
              documentText={documentText}
              onClausesAnalyzed={handleClausesAnalyzed}
            />
          )}
          {activeTab === 'suggest' && (
            <ChangeSuggester
              documentText={documentText}
              onSuggestionsGenerated={handleSuggestionsGenerated}
              onNavigateToComments={() => setActiveTab('comments')}
            />
          )}
          {activeTab === 'comments' && (
            <ClauseComments
              clauses={clauses}
              comments={comments}
              addComment={addComment}
              documentName={documentName}
              onContinue={() => setShowResearchModal(true)}
            />
          )}
          {activeTab === 'confirmation' && researchSubmitted && (
            <ConfirmationScreen
              documentText={documentText}
              documentName={documentName}
              clauses={clauses}
              suggestions={suggestions}
              comments={comments}
              participantEmail={participantData?.email}
              onReset={() => {
                setDocumentText('');
                setDocumentName('');
                setClauses([]);
                setSuggestions([]);
                setComments({});
                setParticipantData(null);
                setResearchSubmitted(false);
                setActiveTab('reader');
                setFlowStep(0);
              }}
            />
          )}
        </ScrollView>

        {/* Research Participation Modal */}
        <ResearchParticipationModal
          visible={showResearchModal}
          onDismiss={() => setShowResearchModal(false)}
          onSubmit={async ({ email, role, teamSize, challenge }) => {
            const result = await ResearchService.submitResearchParticipant({
              email,
              role,
              teamSize,
              challenge,
              documentName,
              documentText,
              analysisData: {
                clauses,
                suggestions,
                comments,
              },
              timestamp: new Date().toISOString(),
            });

            setParticipantData({ email, role, teamSize, challenge });
            setResearchSubmitted(true);
            setShowResearchModal(false);
            setFlowStep(3);
            setActiveTab('confirmation');
          }}
        />
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
    backgroundColor: '#fff',
    paddingVertical: 10,
  },
  tabContent: {
    paddingHorizontal: 10,
    gap: 8,
  },
  tab: {
    marginHorizontal: 4,
  },
  content: {
    flex: 1,
    padding: 10,
  },
  placeholderCard: {
    padding: 20,
    elevation: 2,
  },
  modalContainer: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
});
