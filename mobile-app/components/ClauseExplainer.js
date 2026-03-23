import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Card,
  Text,
  Chip,
  ActivityIndicator,
  List,
  Divider,
} from 'react-native-paper';
import { analyzeDocumentClauses } from '../services/DocumentAnalyzer';

export default function ClauseExplainer({ documentText, onClausesAnalyzed }) {
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    if (documentText) {
      analyzeClauses();
    }
  }, [documentText]);

  const analyzeClauses = async () => {
    setLoading(true);
    try {
      const analyzedClauses = await analyzeDocumentClauses(documentText);
      setClauses(analyzedClauses);
      // Lift state to parent App.js
      if (onClausesAnalyzed) {
        onClausesAnalyzed(analyzedClauses);
      }
    } catch (error) {
      console.error('Error analyzing clauses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePress = (clauseId) => {
    setExpandedId(expandedId === clauseId ? null : clauseId);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Analyzing document clauses...</Text>
      </View>
    );
  }

  if (!documentText) {
    return (
      <Card style={styles.emptyCard}>
        <Card.Content>
          <Text variant="titleMedium">No document loaded</Text>
          <Text variant="bodyMedium" style={styles.emptyText}>
            Please load a document first to see clause explanations
          </Text>
        </Card.Content>
      </Card>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="titleLarge">Document Analysis</Text>
          <Text variant="bodyMedium" style={styles.summaryText}>
            Found {clauses.length} main clauses in the document
          </Text>
        </Card.Content>
      </Card>

      <List.Section>
        {clauses.map((clause, index) => (
          <View key={clause.id}>
            <List.Accordion
              title={clause.title}
              description={clause.snippet}
              expanded={expandedId === clause.id}
              onPress={() => handlePress(clause.id)}
              left={(props) => <List.Icon {...props} icon="file-document-outline" />}
            >
              <Card style={styles.clauseCard}>
                <Card.Content>
                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Full Text:
                  </Text>
                  <Text variant="bodyMedium" style={styles.clauseText}>
                    {clause.fullText}
                  </Text>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Plain English Explanation:
                  </Text>
                  <Text variant="bodyMedium" style={styles.explanation}>
                    {clause.explanation}
                  </Text>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Key Points:
                  </Text>
                  {clause.keyPoints.map((point, idx) => (
                    <View key={idx} style={styles.bulletPoint}>
                      <Text variant="bodyMedium">• {point}</Text>
                    </View>
                  ))}

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Importance Level:
                  </Text>
                  <Chip
                    mode="flat"
                    style={[
                      styles.importanceChip,
                      { backgroundColor: getImportanceColor(clause.importance) },
                    ]}
                  >
                    {clause.importance}
                  </Chip>
                </Card.Content>
              </Card>
            </List.Accordion>
            {index < clauses.length - 1 && <Divider />}
          </View>
        ))}
      </List.Section>
    </ScrollView>
  );
}

const getImportanceColor = (importance) => {
  switch (importance.toLowerCase()) {
    case 'high':
      return '#FFCDD2'; // Light red for high importance
    case 'medium':
      return '#FFF9C4'; // Light yellow for medium importance
    case 'low':
      return '#C8E6C9'; // Light green for low importance
    default:
      return '#E0E0E0'; // Light gray for undefined
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
  },
  emptyCard: {
    margin: 10,
  },
  emptyText: {
    marginTop: 10,
  },
  summaryCard: {
    marginBottom: 15,
    elevation: 2,
  },
  summaryText: {
    marginTop: 10,
  },
  clauseCard: {
    margin: 10,
  },
  sectionTitle: {
    marginTop: 10,
    marginBottom: 5,
    fontWeight: 'bold',
  },
  clauseText: {
    fontStyle: 'italic',
    padding: 10,
    borderRadius: 5,
  },
  explanation: {
    lineHeight: 22,
  },
  bulletPoint: {
    marginLeft: 10,
    marginTop: 5,
  },
  divider: {
    marginVertical: 15,
  },
  importanceChip: {
    alignSelf: 'flex-start',
    marginTop: 5,
  },
});
