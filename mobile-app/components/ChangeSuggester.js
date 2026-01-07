import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Card,
  Text,
  ActivityIndicator,
  List,
  Chip,
  Button,
  Divider,
} from 'react-native-paper';
import { suggestDocumentChanges } from '../services/DocumentAnalyzer';

export default function ChangeSuggester({ documentText }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    if (documentText) {
      generateSuggestions();
    }
  }, [documentText]);

  const generateSuggestions = async () => {
    setLoading(true);
    try {
      const changes = await suggestDocumentChanges(documentText);
      setSuggestions(changes);
    } catch (error) {
      console.error('Error generating suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePress = (suggestionId) => {
    setExpandedId(expandedId === suggestionId ? null : suggestionId);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>
          Analyzing document and generating suggestions...
        </Text>
      </View>
    );
  }

  if (!documentText) {
    return (
      <Card style={styles.emptyCard}>
        <Card.Content>
          <Text variant="titleMedium">No document loaded</Text>
          <Text variant="bodyMedium" style={styles.emptyText}>
            Please load a document first to get improvement suggestions
          </Text>
        </Card.Content>
      </Card>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="titleLarge">Suggested Improvements</Text>
          <Text variant="bodyMedium" style={styles.summaryText}>
            {suggestions.length} suggestions to improve your document
          </Text>
        </Card.Content>
      </Card>

      <List.Section>
        {suggestions.map((suggestion, index) => (
          <View key={suggestion.id}>
            <List.Accordion
              title={suggestion.title}
              description={suggestion.summary}
              expanded={expandedId === suggestion.id}
              onPress={() => handlePress(suggestion.id)}
              left={(props) => (
                <List.Icon
                  {...props}
                  icon={getPriorityIcon(suggestion.priority)}
                  color={getPriorityColor(suggestion.priority)}
                />
              )}
            >
              <Card style={styles.suggestionCard}>
                <Card.Content>
                  <View style={styles.priorityRow}>
                    <Text variant="labelMedium">Priority:</Text>
                    <Chip
                      mode="flat"
                      style={[
                        styles.priorityChip,
                        { backgroundColor: getPriorityColor(suggestion.priority) },
                      ]}
                    >
                      {suggestion.priority}
                    </Chip>
                  </View>

                  <View style={styles.categoryRow}>
                    <Text variant="labelMedium">Category:</Text>
                    <Chip mode="outlined" style={styles.categoryChip}>
                      {suggestion.category}
                    </Chip>
                  </View>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Issue Found:
                  </Text>
                  <Text variant="bodyMedium" style={styles.issueText}>
                    {suggestion.issue}
                  </Text>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Why This Matters:
                  </Text>
                  <Text variant="bodyMedium" style={styles.reasonText}>
                    {suggestion.reason}
                  </Text>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Recommended Change:
                  </Text>
                  <Card style={styles.changeCard}>
                    <Card.Content>
                      <Text variant="bodyMedium">{suggestion.recommendedChange}</Text>
                    </Card.Content>
                  </Card>

                  <Divider style={styles.divider} />

                  <Text variant="labelLarge" style={styles.sectionTitle}>
                    Expected Benefits:
                  </Text>
                  {suggestion.benefits.map((benefit, idx) => (
                    <View key={idx} style={styles.bulletPoint}>
                      <Text variant="bodyMedium">✓ {benefit}</Text>
                    </View>
                  ))}

                  {suggestion.examples && (
                    <>
                      <Divider style={styles.divider} />
                      <Text variant="labelLarge" style={styles.sectionTitle}>
                        Example:
                      </Text>
                      <Text variant="bodySmall" style={styles.exampleText}>
                        {suggestion.examples}
                      </Text>
                    </>
                  )}
                </Card.Content>
              </Card>
            </List.Accordion>
            {index < suggestions.length - 1 && <Divider />}
          </View>
        ))}
      </List.Section>

      <Card style={styles.actionCard}>
        <Card.Content>
          <Text variant="titleMedium">Next Steps</Text>
          <Text variant="bodyMedium" style={styles.actionText}>
            Review each suggestion and consider implementing the changes that
            best fit your needs.
          </Text>
          <Button
            mode="contained"
            icon="download"
            style={styles.exportButton}
            onPress={() => {
              // Export suggestions functionality
              console.log('Export suggestions');
            }}
          >
            Export Suggestions Report
          </Button>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const getPriorityIcon = (priority) => {
  switch (priority.toLowerCase()) {
    case 'high':
      return 'alert-circle';
    case 'medium':
      return 'alert';
    case 'low':
      return 'information';
    default:
      return 'circle-outline';
  }
};

const getPriorityColor = (priority) => {
  switch (priority.toLowerCase()) {
    case 'high':
      return '#ef5350';
    case 'medium':
      return '#ffa726';
    case 'low':
      return '#66bb6a';
    default:
      return '#9e9e9e';
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
    color: '#666',
  },
  summaryCard: {
    marginBottom: 15,
    elevation: 2,
  },
  summaryText: {
    marginTop: 10,
    color: '#666',
  },
  suggestionCard: {
    margin: 10,
    backgroundColor: '#f9f9f9',
  },
  priorityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  priorityChip: {
    marginLeft: 10,
  },
  categoryRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryChip: {
    marginLeft: 10,
  },
  sectionTitle: {
    marginTop: 10,
    marginBottom: 5,
    fontWeight: 'bold',
  },
  issueText: {
    color: '#d32f2f',
    fontWeight: '500',
    padding: 10,
    backgroundColor: '#ffebee',
    borderRadius: 5,
  },
  reasonText: {
    lineHeight: 22,
    color: '#555',
  },
  changeCard: {
    backgroundColor: '#e8f5e9',
    marginTop: 5,
  },
  bulletPoint: {
    marginLeft: 10,
    marginTop: 5,
  },
  exampleText: {
    fontStyle: 'italic',
    color: '#666',
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 5,
  },
  divider: {
    marginVertical: 15,
  },
  actionCard: {
    marginTop: 15,
    marginBottom: 20,
    elevation: 2,
  },
  actionText: {
    marginTop: 10,
    marginBottom: 15,
    color: '#666',
  },
  exportButton: {
    marginTop: 10,
  },
});
