import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import {
  Card,
  Text,
  Button,
  Avatar,
  List,
  Snackbar,
  Surface,
} from 'react-native-paper';
import * as Clipboard from 'expo-clipboard';
import * as ResearchService from '../services/ResearchService';

export default function ConfirmationScreen({
  documentText,
  documentName,
  clauses,
  suggestions,
  comments,
  participantEmail,
  onReset,
}) {
  const [downloading, setDownloading] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleDownloadAnalysis = async () => {
    setDownloading(true);
    try {
      const analysisText = await ResearchService.exportAnalysisText(
        documentName,
        clauses,
        suggestions,
        comments
      );

      // Copy to clipboard (since we can't actually download files in mobile app)
      await Clipboard.setStringAsync(analysisText);
      setSnackbarMessage('Analysis copied to clipboard!');
      setSnackbarVisible(true);

      // Show alert with preview
      Alert.alert(
        'Analysis Ready',
        'Your analysis has been copied to your clipboard. You can paste it into any text editor or email.',
        [
          {
            text: 'Preview',
            onPress: () => {
              Alert.alert(
                'Analysis Preview',
                analysisText.substring(0, 500) + '...\n\n(Full analysis copied to clipboard)'
              );
            },
          },
          { text: 'OK' },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to generate analysis: ' + error.message);
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyDocument = async () => {
    try {
      await Clipboard.setStringAsync(documentText);
      setSnackbarMessage('Document text copied to clipboard!');
      setSnackbarVisible(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to copy document: ' + error.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Success Header */}
      <Surface style={styles.headerSurface} elevation={0}>
        <Avatar.Icon
          size={64}
          icon="check-circle"
          style={styles.successIcon}
        />
        <Text variant="headlineSmall" style={styles.title}>
          Thank You! Check Your Email
        </Text>
        <Text variant="bodyLarge" style={styles.subtitle}>
          We've emailed your contract analysis to{' '}
          <Text style={styles.emailText}>{participantEmail}</Text>. We'll contact
          you within 48 hours to schedule your 30-minute session and share your
          $50 gift card details.
        </Text>
      </Surface>

      {/* What Happens Next Card */}
      <Card style={styles.card}>
        <Card.Title
          title="What Happens Next"
          titleVariant="titleLarge"
          left={(props) => <List.Icon {...props} icon="timeline-clock" />}
        />
        <Card.Content>
          <List.Section>
            <List.Item
              title="Check your email"
              description="Your contract analysis PDF is waiting"
              left={(props) => (
                <Avatar.Text
                  {...props}
                  size={40}
                  label="1"
                  style={styles.stepNumber}
                />
              )}
            />
            <List.Item
              title="We'll reach out"
              description="Expect an email within 48 hours to schedule your 30-min session"
              left={(props) => (
                <Avatar.Text
                  {...props}
                  size={40}
                  label="2"
                  style={styles.stepNumber}
                />
              )}
            />
            <List.Item
              title="Share your feedback"
              description="Help us understand your contract challenges"
              left={(props) => (
                <Avatar.Text
                  {...props}
                  size={40}
                  label="3"
                  style={styles.stepNumber}
                />
              )}
            />
            <List.Item
              title="Receive $50"
              description="Gift card sent after the call"
              left={(props) => (
                <Avatar.Text
                  {...props}
                  size={40}
                  label="4"
                  style={styles.stepNumber}
                />
              )}
            />
          </List.Section>
        </Card.Content>
      </Card>

      {/* Actions Card */}
      <Card style={styles.card}>
        <Card.Title
          title="Your Analysis"
          titleVariant="titleLarge"
          left={(props) => <List.Icon {...props} icon="file-document" />}
        />
        <Card.Content>
          <Text variant="bodyMedium" style={styles.actionDescription}>
            Download a backup copy of your analysis now
          </Text>
          <Button
            mode="contained"
            icon="download"
            loading={downloading}
            disabled={downloading}
            onPress={handleDownloadAnalysis}
            style={styles.button}
          >
            Download Analysis Now
          </Button>
        </Card.Content>
      </Card>

      {/* Optional: Need to sign now? */}
      <Card style={styles.card}>
        <List.Accordion
          title="Need to sign this contract now?"
          description="We don't offer signing yet, but here are options"
          left={(props) => <List.Icon {...props} icon="pen" />}
        >
          <Card.Content>
            <Text variant="bodyMedium" style={styles.signingHelp}>
              You can copy your document text and paste it into your preferred
              signing tool:
            </Text>
            <Button
              mode="outlined"
              icon="content-copy"
              onPress={handleCopyDocument}
              style={styles.button}
            >
              Copy Document Text
            </Button>
            <Text variant="bodySmall" style={styles.signingNote}>
              Paste into DocuSign, sign.com, or your preferred signing tool
            </Text>
          </Card.Content>
        </List.Accordion>
      </Card>

      {/* Reset Button */}
      <Card style={styles.card}>
        <Card.Content>
          <Button mode="text" icon="refresh" onPress={onReset}>
            Analyze Another Contract
          </Button>
        </Card.Content>
      </Card>

      {/* Snackbar for notifications */}
      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={3000}
        action={{
          label: 'OK',
          onPress: () => setSnackbarVisible(false),
        }}
      >
        {snackbarMessage}
      </Snackbar>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerSurface: {
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  successIcon: {
    backgroundColor: '#00C853',
    marginBottom: 16,
  },
  title: {
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    textAlign: 'center',
    lineHeight: 24,
  },
  emailText: {
    fontWeight: '600',
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  stepNumber: {
    backgroundColor: '#FFEE55',
  },
  actionDescription: {
    marginBottom: 12,
  },
  button: {
    marginTop: 12,
  },
  signingHelp: {
    marginBottom: 12,
  },
  signingNote: {
    marginTop: 8,
    opacity: 0.7,
  },
});
