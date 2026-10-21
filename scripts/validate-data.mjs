import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data', 'matches.json'), 'utf8'));
const categories = JSON.parse(fs.readFileSync(path.join(root, 'data', 'categories.json'), 'utf8')).categories;
const errors = [];
const requiredMatchKeys = [
  'id', 'sport', 'categorySlug', 'competition', 'capturedAt', 'origin',
  'participants', 'schedule', 'sources', 'sourceFacts', 'model', 'flags', 'audit',
];
const requiredModelKeys = [
  'version', 'independenceStatement', 'formula', 'inputs', 'winner', 'handicap',
  'total', 'confidence', 'rationale', 'highConfidenceAnalysis', 'caveats',
];
const excluded = new Set([
  'soccer', 'boxing', 'ufc', 'mma', 'football', 'american-football',
  'hurling', 'horse-racing', 'cycling', 'specials',
]);
const ids = new Set();
const highAnalyses = new Set();
const wordCount = (value = '') => (value.match(/[\p{L}\p{N}’'-]+/gu) || []).length;

for (const match of data.matches) {
  for (const key of requiredMatchKeys) {
    if (!(key in match)) errors.push(`${match.id || 'unknown'} missing ${key}`);
  }
  for (const key of requiredModelKeys) {
    if (!(key in match.model)) errors.push(`${match.id} model missing ${key}`);
  }
  if (ids.has(match.id)) errors.push(`duplicate id ${match.id}`);
  ids.add(match.id);
  if (excluded.has(match.categorySlug)) errors.push(`${match.id} uses excluded category ${match.categorySlug}`);
  if (!match.participants.a || !match.participants.b) errors.push(`${match.id} has a blank participant`);
  if (!match.competition) errors.push(`${match.id} has a blank competition`);
  if (!['verified', 'partially-verified', 'unverified'].includes(match.schedule.verification)) {
    errors.push(`${match.id} has invalid verification state`);
  }
  if (match.schedule.verification === 'verified' && !match.schedule.date) {
    errors.push(`${match.id} is verified but date is blank`);
  }
  if (match.schedule.verification === 'unverified' && match.model.confidence !== 'low') {
    errors.push(`${match.id} is unverified but confidence is not low`);
  }
  const official = match.sources.official;
  if (!official?.label || !official?.url?.startsWith('https://')) {
    errors.push(`${match.id} lacks an HTTPS official source`);
  }
  if (official?.url?.includes('olbg.com')) errors.push(`${match.id} treats OLBG as official evidence`);
  if (!match.sources.discovery?.url?.startsWith('https://www.olbg.com/')) {
    errors.push(`${match.id} lacks a labeled OLBG discovery source`);
  }
  if (match.schedule.time && !match.schedule.timezone) errors.push(`${match.id} has a time without a timezone`);
  if (!Array.isArray(match.sourceFacts) || match.sourceFacts.length === 0) {
    errors.push(`${match.id} has no source-fact audit note`);
  }
  const winner = match.model.winner;
  const probabilitySum = winner.participantAProbabilityPct + winner.participantBProbabilityPct;
  if (Math.abs(probabilitySum - 100) > 0.11) errors.push(`${match.id} probability sum is ${probabilitySum}`);
  if (![match.participants.a, match.participants.b].includes(winner.selection)) {
    errors.push(`${match.id} winner is not a participant`);
  }
  if (!(winner.fairDecimalOdds > 1)) errors.push(`${match.id} has invalid fair odds`);
  if (!match.model.handicap.line || !match.model.total.line) errors.push(`${match.id} lacks modeled markets`);
  if (!['low', 'medium', 'high'].includes(match.model.confidence)) errors.push(`${match.id} has invalid confidence`);
  if (match.model.confidence === 'high') {
    const analysis = match.model.highConfidenceAnalysis;
    if (wordCount(analysis) < 30) errors.push(`${match.id} high analysis has fewer than 30 words`);
    if (!analysis.toLocaleLowerCase().includes(winner.selection.toLocaleLowerCase())) {
      errors.push(`${match.id} high analysis does not identify the selection`);
    }
    if (highAnalyses.has(analysis)) errors.push(`${match.id} duplicates another high-confidence analysis`);
    highAnalyses.add(analysis);
    if (match.schedule.verification !== 'verified') errors.push(`${match.id} high confidence is not verified`);
  } else if (match.model.highConfidenceAnalysis) {
    errors.push(`${match.id} has high-confidence copy without high confidence`);
  }
}

const categorySlugs = new Set(categories.map((category) => category.slug));
for (const match of data.matches) {
  if (!categorySlugs.has(match.categorySlug)) errors.push(`${match.id} has no category record`);
}
for (const category of categories) {
  if (!category.slug || !category.name || !category.description || !category.status) {
    errors.push(`incomplete category record ${category.slug || 'unknown'}`);
  }
  if (excluded.has(category.slug)) errors.push(`excluded category record ${category.slug}`);
  if (category.emptyReason && (!category.officialSource?.label || !category.officialSource?.url?.startsWith('https://'))) {
    errors.push(`empty category ${category.slug} lacks an HTTPS official review source`);
  }
}

const recomputed = {
  matchCount: data.matches.length,
  verifiedCount: data.matches.filter((match) => match.schedule.verification === 'verified').length,
  partialCount: data.matches.filter((match) => match.schedule.verification === 'partially-verified').length,
  unverifiedCount: data.matches.filter((match) => match.schedule.verification === 'unverified').length,
  flaggedMatchCount: data.matches.filter((match) => match.flags.length).length,
  highConfidenceCount: data.matches.filter((match) => match.model.confidence === 'high').length,
  categoryCount: new Set(data.matches.map((match) => match.categorySlug)).size,
};
for (const [key, value] of Object.entries(recomputed)) {
  if (data.summary[key] !== value) errors.push(`summary ${key} is ${data.summary[key]}, expected ${value}`);
}

if (data.matches.length !== 135) errors.push(`expected 135 modeled rows in this frozen capture, found ${data.matches.length}`);
if (categories.length !== 15) errors.push(`expected 15 included category records, found ${categories.length}`);

if (errors.length) {
  console.error(`Validation failed with ${errors.length} error(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log(`Validated ${data.matches.length} rows, ${categories.length} categories and ${highAnalyses.size} unique high-confidence analyses.`);
