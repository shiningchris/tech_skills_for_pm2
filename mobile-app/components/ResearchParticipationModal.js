import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Modal,
  Portal,
  Card,
  Text,
  TextInput,
  Button,
  HelperText,
  Menu,
  Divider,
} from 'react-native-paper';

const ROLES = [
  'Founder',
  'HR Manager',
  'Legal/Compliance',
  'Team Lead',
  'Employee',
  'Other',
];

const TEAM_SIZES = [
  'Just me',
  '2-10 people',
  '11-50',
  '51-200',
  '201+',
];

export default function ResearchParticipationModal({
  visible,
  onDismiss,
  onSubmit,
}) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('');
  const [teamSize, setTeamSize] = useState('');
  const [challenge, setChallenge] = useState('');

  const [roleMenuVisible, setRoleMenuVisible] = useState(false);
  const [teamSizeMenuVisible, setTeamSizeMenuVisible] = useState(false);

  const [emailError, setEmailError] = useState('');
  const [touched, setTouched] = useState({
    email: false,
    role: false,
    teamSize: false,
  });

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleEmailBlur = () => {
    setTouched((prev) => ({ ...prev, email: true }));
    if (!email.trim()) {
      setEmailError('Email is required');
    } else if (!validateEmail(email)) {
      setEmailError('Please enter a valid email address');
    } else {
      setEmailError('');
    }
  };

  const isFormValid =
    email.trim() &&
    validateEmail(email) &&
    role &&
    teamSize;

  const handleSubmit = () => {
    if (isFormValid) {
      onSubmit({
        email: email.trim(),
        role,
        teamSize,
        challenge: challenge.trim(),
      });
      // Reset form
      setEmail('');
      setRole('');
      setTeamSize('');
      setChallenge('');
      setTouched({ email: false, role: false, teamSize: false });
      setEmailError('');
    }
  };

  const characterLimit = 300;
  const remainingChars = characterLimit - challenge.length;

  return (
    <Portal>
      <Modal
        visible={visible}
        onDismiss={onDismiss}
        contentContainerStyle={styles.modalContainer}
      >
        <Card>
          <ScrollView>
            <Card.Content>
              {/* Header */}
              <Text variant="headlineSmall" style={styles.title}>
                Help Us Build Better Contract Tools for Small Teams
              </Text>
              <Text variant="bodyMedium" style={styles.description}>
                We're building contract & document management tools to help small teams
                feel legally protected. Share your experience in a 30-minute conversation
                and receive a <Text style={styles.highlight}>$50 gift card</Text>. Plus,
                get your analysis emailed to you now.
              </Text>

              <Divider style={styles.divider} />

              {/* Email Field */}
              <TextInput
                mode="outlined"
                label="Email *"
                value={email}
                onChangeText={setEmail}
                onBlur={handleEmailBlur}
                keyboardType="email-address"
                autoCapitalize="none"
                error={touched.email && !!emailError}
                style={styles.input}
              />
              {touched.email && emailError ? (
                <HelperText type="error" visible={true}>
                  {emailError}
                </HelperText>
              ) : null}

              {/* Role Dropdown */}
              <Menu
                visible={roleMenuVisible}
                onDismiss={() => setRoleMenuVisible(false)}
                anchor={
                  <Button
                    mode="outlined"
                    onPress={() => setRoleMenuVisible(true)}
                    style={styles.dropdownButton}
                    contentStyle={styles.dropdownContent}
                    icon="chevron-down"
                  >
                    {role || 'Select your role *'}
                  </Button>
                }
              >
                {ROLES.map((r) => (
                  <Menu.Item
                    key={r}
                    onPress={() => {
                      setRole(r);
                      setRoleMenuVisible(false);
                      setTouched((prev) => ({ ...prev, role: true }));
                    }}
                    title={r}
                  />
                ))}
              </Menu>
              {touched.role && !role ? (
                <HelperText type="error" visible={true}>
                  Please select your role
                </HelperText>
              ) : null}

              {/* Team Size Dropdown */}
              <Menu
                visible={teamSizeMenuVisible}
                onDismiss={() => setTeamSizeMenuVisible(false)}
                anchor={
                  <Button
                    mode="outlined"
                    onPress={() => setTeamSizeMenuVisible(true)}
                    style={styles.dropdownButton}
                    contentStyle={styles.dropdownContent}
                    icon="chevron-down"
                  >
                    {teamSize || 'Select team size *'}
                  </Button>
                }
              >
                {TEAM_SIZES.map((size) => (
                  <Menu.Item
                    key={size}
                    onPress={() => {
                      setTeamSize(size);
                      setTeamSizeMenuVisible(false);
                      setTouched((prev) => ({ ...prev, teamSize: true }));
                    }}
                    title={size}
                  />
                ))}
              </Menu>
              {touched.teamSize && !teamSize ? (
                <HelperText type="error" visible={true}>
                  Please select your team size
                </HelperText>
              ) : null}

              {/* Challenge Field (Optional) */}
              <TextInput
                mode="outlined"
                label="What's your biggest contract challenge? (optional)"
                value={challenge}
                onChangeText={(text) => {
                  if (text.length <= characterLimit) {
                    setChallenge(text);
                  }
                }}
                multiline
                numberOfLines={3}
                placeholder="e.g., understanding legal terms, tracking versions, negotiating terms, signing & storing..."
                style={styles.input}
                maxLength={characterLimit}
              />
              <HelperText type="info" visible={true}>
                {remainingChars} characters remaining
              </HelperText>

              <Divider style={styles.divider} />

              {/* Action Buttons */}
              <Button
                mode="contained"
                onPress={handleSubmit}
                disabled={!isFormValid}
                icon="gift"
                style={styles.submitButton}
              >
                Send My Analysis & Claim $50
              </Button>

              <Button
                mode="text"
                onPress={onDismiss}
                style={styles.dismissButton}
              >
                No thanks, I'll just download
              </Button>
            </Card.Content>
          </ScrollView>
        </Card>
      </Modal>
    </Portal>
  );
}

const styles = StyleSheet.create({
  modalContainer: {
    maxHeight: '90%',
    marginHorizontal: 20,
    marginVertical: 40,
  },
  title: {
    marginBottom: 12,
    fontWeight: 'bold',
  },
  description: {
    lineHeight: 24,
    marginBottom: 8,
  },
  highlight: {
    fontWeight: 'bold',
  },
  divider: {
    marginVertical: 16,
  },
  input: {
    marginBottom: 8,
  },
  dropdownButton: {
    marginBottom: 8,
    marginTop: 8,
  },
  dropdownContent: {
    justifyContent: 'space-between',
  },
  submitButton: {
    marginTop: 8,
    paddingVertical: 4,
  },
  dismissButton: {
    marginTop: 8,
  },
});
