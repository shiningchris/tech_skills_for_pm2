import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Card,
  Text,
  TextInput,
  Button,
  List,
  Surface,
  Divider,
  IconButton,
} from 'react-native-paper';

export default function ClauseComments({
  clauses,
  comments,
  addComment,
  documentName,
  onContinue,
}) {
  const [generalNote, setGeneralNote] = useState('');
  const [clauseNotes, setClauseNotes] = useState({});
  const [expandedId, setExpandedId] = useState(null);

  const handleAddGeneralNote = () => {
    if (generalNote.trim()) {
      addComment('general', generalNote.trim());
      setGeneralNote('');
    }
  };

  const handleAddClauseNote = (clauseId) => {
    const note = clauseNotes[clauseId];
    if (note && note.trim()) {
      addComment(clauseId, note.trim());
      setClauseNotes((prev) => ({ ...prev, [clauseId]: '' }));
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}
    >
      <ScrollView style={styles.scrollView}>
        {/* Header Card */}
        <Card style={styles.headerCard}>
          <Card.Content>
            <Text variant="titleLarge">Your Notes</Text>
            <Text variant="bodyMedium" style={styles.subtitle}>
              Add comments and observations about {documentName || 'this document'}
            </Text>
          </Card.Content>
        </Card>

        {/* General Notes Section */}
        <Card style={styles.sectionCard}>
          <Card.Title
            title="General Notes"
            titleVariant="titleMedium"
            left={(props) => <List.Icon {...props} icon="comment-text" />}
          />
          <Card.Content>
            <Text variant="bodySmall" style={styles.helpText}>
              Add overall thoughts or observations about the document
            </Text>

            {/* Existing General Comments */}
            {comments.general && comments.general.length > 0 && (
              <View style={styles.commentsContainer}>
                {comments.general.map((comment) => (
                  <Surface key={comment.id} style={styles.commentSurface} elevation={1}>
                    <Text variant="bodyMedium">{comment.text}</Text>
                    <Text variant="bodySmall" style={styles.timestamp}>
                      {formatTimestamp(comment.timestamp)}
                    </Text>
                  </Surface>
                ))}
              </View>
            )}

            {/* Add New General Note */}
            <View style={styles.inputRow}>
              <TextInput
                mode="outlined"
                placeholder="Type your note here..."
                value={generalNote}
                onChangeText={setGeneralNote}
                style={styles.textInput}
                multiline
                numberOfLines={2}
              />
              <IconButton
                icon="plus-circle"
                mode="contained"
                size={28}
                onPress={handleAddGeneralNote}
                disabled={!generalNote.trim()}
              />
            </View>
          </Card.Content>
        </Card>

        {/* Per-Clause Notes */}
        <Card style={styles.sectionCard}>
          <Card.Title
            title="Notes by Clause"
            titleVariant="titleMedium"
            left={(props) => <List.Icon {...props} icon="file-document-outline" />}
          />
          <Card.Content>
            <Text variant="bodySmall" style={styles.helpText}>
              Add specific notes for each clause you want to review
            </Text>
          </Card.Content>

          <List.Section>
            {clauses.map((clause, index) => (
              <View key={clause.id}>
                <List.Accordion
                  title={clause.title}
                  description={clause.snippet}
                  expanded={expandedId === clause.id}
                  onPress={() =>
                    setExpandedId(expandedId === clause.id ? null : clause.id)
                  }
                  left={(props) => (
                    <List.Icon
                      {...props}
                      icon={
                        comments[clause.id] && comments[clause.id].length > 0
                          ? 'comment-check'
                          : 'comment-outline'
                      }
                    />
                  )}
                  right={(props) =>
                    comments[clause.id] && comments[clause.id].length > 0 ? (
                      <Text
                        variant="labelSmall"
                        style={styles.commentCount}
                      >
                        {comments[clause.id].length}
                      </Text>
                    ) : null
                  }
                >
                  <View style={styles.accordionContent}>
                    {/* Existing Comments for this Clause */}
                    {comments[clause.id] && comments[clause.id].length > 0 && (
                      <View style={styles.commentsContainer}>
                        {comments[clause.id].map((comment) => (
                          <Surface
                            key={comment.id}
                            style={styles.commentSurface}
                            elevation={1}
                          >
                            <Text variant="bodyMedium">{comment.text}</Text>
                            <Text variant="bodySmall" style={styles.timestamp}>
                              {formatTimestamp(comment.timestamp)}
                            </Text>
                          </Surface>
                        ))}
                      </View>
                    )}

                    {/* Add New Comment */}
                    <View style={styles.inputRow}>
                      <TextInput
                        mode="outlined"
                        placeholder="Add a note about this clause..."
                        value={clauseNotes[clause.id] || ''}
                        onChangeText={(text) =>
                          setClauseNotes((prev) => ({ ...prev, [clause.id]: text }))
                        }
                        style={styles.textInput}
                        multiline
                        numberOfLines={2}
                      />
                      <IconButton
                        icon="plus-circle"
                        mode="contained"
                        size={28}
                        onPress={() => handleAddClauseNote(clause.id)}
                        disabled={!clauseNotes[clause.id] || !clauseNotes[clause.id].trim()}
                      />
                    </View>
                  </View>
                </List.Accordion>
                {index < clauses.length - 1 && <Divider />}
              </View>
            ))}
          </List.Section>
        </Card>

        {/* Spacer for sticky button */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Sticky Bottom Button */}
      <Surface style={styles.bottomSurface} elevation={4}>
        <Text variant="bodySmall" style={styles.incentiveText}>
          Get a $50 gift card for sharing your feedback!
        </Text>
        <Button
          mode="contained"
          icon="gift"
          onPress={onContinue}
          style={styles.ctaButton}
        >
          Share Feedback & Get $50
        </Button>
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  headerCard: {
    marginBottom: 15,
    elevation: 2,
  },
  subtitle: {
    marginTop: 8,
  },
  sectionCard: {
    marginBottom: 15,
    elevation: 2,
  },
  helpText: {
    marginBottom: 12,
    opacity: 0.7,
  },
  commentsContainer: {
    marginVertical: 12,
  },
  commentSurface: {
    padding: 12,
    marginBottom: 8,
    borderRadius: 8,
  },
  timestamp: {
    marginTop: 4,
    opacity: 0.6,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginTop: 8,
  },
  textInput: {
    flex: 1,
    marginRight: 8,
  },
  accordionContent: {
    padding: 16,
  },
  commentCount: {
    alignSelf: 'center',
    marginRight: 16,
    fontWeight: 'bold',
  },
  bottomSurface: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    backgroundColor: '#fff',
  },
  incentiveText: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: '500',
  },
  ctaButton: {
    paddingVertical: 4,
  },
});
