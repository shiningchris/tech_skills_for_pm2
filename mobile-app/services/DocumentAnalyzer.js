/**
 * DocumentAnalyzer Service
 * Provides NLP-like functionality for analyzing documents,
 * explaining clauses, and suggesting improvements.
 */

/**
 * Analyzes a document and extracts main clauses with explanations
 * @param {string} documentText - The full text of the document
 * @returns {Promise<Array>} Array of clause objects with explanations
 */
export async function analyzeDocumentClauses(documentText) {
  // Simulate async processing
  await new Promise((resolve) => setTimeout(resolve, 1500));

  // Split document into sections (in a real app, this would use NLP)
  const sections = identifySections(documentText);

  return sections.map((section, index) => ({
    id: `clause-${index}`,
    title: section.title,
    snippet: section.text.substring(0, 80) + '...',
    fullText: section.text,
    explanation: generateExplanation(section),
    keyPoints: extractKeyPoints(section),
    importance: determineImportance(section),
  }));
}

/**
 * Generates suggestions for improving the document
 * @param {string} documentText - The full text of the document
 * @returns {Promise<Array>} Array of suggestion objects
 */
export async function suggestDocumentChanges(documentText) {
  // Simulate async processing
  await new Promise((resolve) => setTimeout(resolve, 1500));

  const suggestions = [];

  // Check for common issues and generate suggestions

  // 1. Check for vague language
  if (hasVagueLanguage(documentText)) {
    suggestions.push({
      id: 'suggestion-vague',
      title: 'Reduce Vague Language',
      summary: 'Document contains ambiguous terms that should be clarified',
      priority: 'High',
      category: 'Clarity',
      issue: 'The document uses vague terms like "reasonable", "appropriate", or "timely" without specific definitions.',
      reason: 'Vague language can lead to disputes and different interpretations. Clear, specific terms reduce ambiguity and legal risks.',
      recommendedChange: 'Replace vague terms with specific metrics, timeframes, or definitions. For example: "within 30 days" instead of "in a timely manner".',
      benefits: [
        'Reduces potential for misunderstandings',
        'Makes enforcement easier',
        'Provides clear expectations for all parties',
      ],
      examples: 'Change "reasonable notice" to "14 days written notice"',
    });
  }

  // 2. Check for missing dates or deadlines
  if (isMissingDates(documentText)) {
    suggestions.push({
      id: 'suggestion-dates',
      title: 'Add Specific Dates and Deadlines',
      summary: 'Document lacks clear timeframes for obligations',
      priority: 'High',
      category: 'Completeness',
      issue: 'Some obligations or terms lack specific dates, deadlines, or timeframes.',
      reason: 'Without clear deadlines, it\'s difficult to enforce agreements or hold parties accountable.',
      recommendedChange: 'Add specific dates for all commitments, renewal dates, termination notice periods, and payment schedules.',
      benefits: [
        'Clear accountability',
        'Easier to track compliance',
        'Reduces potential disputes',
      ],
    });
  }

  // 3. Check for complex sentences
  if (hasComplexSentences(documentText)) {
    suggestions.push({
      id: 'suggestion-complexity',
      title: 'Simplify Complex Sentences',
      summary: 'Some sentences are overly long and complex',
      priority: 'Medium',
      category: 'Readability',
      issue: 'The document contains sentences with multiple clauses that are difficult to parse.',
      reason: 'Complex sentences reduce readability and increase the chance of misinterpretation.',
      recommendedChange: 'Break long sentences into shorter ones. Use bullet points for lists. Aim for one main idea per sentence.',
      benefits: [
        'Improved readability',
        'Better understanding by all parties',
        'Reduced risk of misinterpretation',
      ],
      examples: 'Split sentences longer than 30 words into multiple sentences',
    });
  }

  // 4. Check for missing definitions
  if (needsDefinitions(documentText)) {
    suggestions.push({
      id: 'suggestion-definitions',
      title: 'Add Definitions Section',
      summary: 'Key terms should be formally defined',
      priority: 'Medium',
      category: 'Clarity',
      issue: 'The document uses technical or important terms without formal definitions.',
      reason: 'Undefined terms can be interpreted differently by different parties, leading to confusion.',
      recommendedChange: 'Add a "Definitions" section at the beginning of the document defining all key terms.',
      benefits: [
        'Ensures consistent interpretation',
        'Reduces ambiguity',
        'Makes document more professional',
      ],
    });
  }

  // 5. Check for one-sided terms
  if (hasImbalancedTerms(documentText)) {
    suggestions.push({
      id: 'suggestion-balance',
      title: 'Balance Rights and Obligations',
      summary: 'Some terms may be disproportionately favorable to one party',
      priority: 'High',
      category: 'Fairness',
      issue: 'Certain clauses appear to heavily favor one party over the other.',
      reason: 'Heavily one-sided agreements may be challenged in court or damage business relationships.',
      recommendedChange: 'Review terms for fairness. Ensure both parties have reasonable rights and obligations.',
      benefits: [
        'More likely to be enforceable',
        'Better long-term relationships',
        'Reduced risk of legal challenges',
      ],
    });
  }

  // 6. General improvements
  suggestions.push({
    id: 'suggestion-structure',
    title: 'Improve Document Structure',
    summary: 'Consider reorganizing for better flow',
    priority: 'Low',
    category: 'Structure',
    issue: 'The document could benefit from better organization and formatting.',
    reason: 'Well-structured documents are easier to navigate, understand, and reference.',
    recommendedChange: 'Use numbered sections, clear headings, and consistent formatting. Consider adding a table of contents for longer documents.',
    benefits: [
      'Easier navigation',
      'More professional appearance',
      'Simpler to reference specific sections',
    ],
  });

  return suggestions;
}

// Helper functions

function identifySections(text) {
  const sections = [];

  // Split by numbered sections or paragraphs
  const lines = text.split('\n\n');

  lines.forEach((line, index) => {
    if (line.trim().length > 20) {
      // Extract title from numbered sections
      const titleMatch = line.match(/^(\d+\.?\s+)?([A-Z\s]+)/);
      const title = titleMatch ? titleMatch[2].trim() : `Section ${index + 1}`;

      sections.push({
        title: title.length > 50 ? title.substring(0, 47) + '...' : title,
        text: line.trim(),
      });
    }
  });

  return sections.length > 0 ? sections : [{
    title: 'Document Content',
    text: text,
  }];
}

function generateExplanation(section) {
  const text = section.text.toLowerCase();

  // Pattern matching for common clause types
  if (text.includes('employment') || text.includes('position')) {
    return 'This clause defines the employment relationship, including the role, responsibilities, and reporting structure.';
  }
  if (text.includes('compensation') || text.includes('salary') || text.includes('payment')) {
    return 'This clause specifies the payment terms, including amounts, frequency, and any additional compensation.';
  }
  if (text.includes('termination') || text.includes('cancel')) {
    return 'This clause outlines the conditions and procedures for ending the agreement, including notice periods and grounds for termination.';
  }
  if (text.includes('confidential') || text.includes('proprietary')) {
    return 'This clause protects sensitive information by requiring parties to keep certain information private and secure.';
  }
  if (text.includes('benefit') || text.includes('insurance') || text.includes('vacation')) {
    return 'This clause describes the benefits, perks, or additional compensation provided beyond base salary.';
  }
  if (text.includes('liability') || text.includes('indemnif')) {
    return 'This clause defines who is responsible for damages, losses, or legal issues that may arise.';
  }

  return 'This clause establishes specific terms and conditions that both parties must follow as part of this agreement.';
}

function extractKeyPoints(section) {
  const points = [];
  const text = section.text;

  // Extract sentences that contain key indicators
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);

  sentences.forEach(sentence => {
    const lower = sentence.toLowerCase();
    if (lower.includes('shall') || lower.includes('must') || lower.includes('required')) {
      points.push(sentence.trim());
    }
  });

  // If no key points found, extract first 2-3 sentences
  if (points.length === 0) {
    return sentences.slice(0, 3).map(s => s.trim());
  }

  return points.slice(0, 4);
}

function determineImportance(section) {
  const text = section.text.toLowerCase();

  // High importance keywords
  if (
    text.includes('termination') ||
    text.includes('compensation') ||
    text.includes('payment') ||
    text.includes('liability') ||
    text.includes('indemnif')
  ) {
    return 'High';
  }

  // Medium importance keywords
  if (
    text.includes('duties') ||
    text.includes('responsibilities') ||
    text.includes('confidential') ||
    text.includes('benefits')
  ) {
    return 'Medium';
  }

  return 'Low';
}

// Suggestion analysis helpers

function hasVagueLanguage(text) {
  const vagueTerms = [
    'reasonable',
    'appropriate',
    'timely',
    'promptly',
    'soon',
    'as needed',
  ];
  const lower = text.toLowerCase();
  return vagueTerms.some(term => lower.includes(term));
}

function isMissingDates(text) {
  // Check if document has very few date patterns
  const datePatterns = /\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}|\d{4}[-\/]\d{1,2}[-\/]\d{1,2}|\d+ days?/gi;
  const matches = text.match(datePatterns);
  return !matches || matches.length < 2;
}

function hasComplexSentences(text) {
  const sentences = text.split(/[.!?]+/);
  // Check if any sentence has more than 40 words
  return sentences.some(sentence => {
    const wordCount = sentence.trim().split(/\s+/).length;
    return wordCount > 40;
  });
}

function needsDefinitions(text) {
  const lower = text.toLowerCase();
  // Check for capitalized terms that might need definition
  const capitalizedTerms = text.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b/g);
  return capitalizedTerms && capitalizedTerms.length > 3 && !lower.includes('definitions');
}

function hasImbalancedTerms(text) {
  const lower = text.toLowerCase();
  // Simple heuristic: check for one-sided language
  const oneSidedTerms = [
    'sole discretion',
    'without limitation',
    'at any time without',
    'no liability',
  ];
  return oneSidedTerms.some(term => lower.includes(term));
}
