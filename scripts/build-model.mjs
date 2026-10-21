import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const inputPath = path.join(root, 'data', 'model-inputs.json');
const outputPath = path.join(root, 'data', 'matches.json');
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

const MODEL_VERSION = 'evidence-shrink-v1.0.0';
const COEFFICIENTS = Object.freeze({
  strength: 0.42,
  form: 0.22,
});

const marketConfig = {
  baseball: { handicapUnit: 'runs', scale: 5, totalUnit: 'runs' },
  basketball: { handicapUnit: 'points', scale: 42, totalUnit: 'points' },
  cricket: { handicapUnit: 'runs', scale: 80, totalUnit: 'first-innings runs' },
  darts: { handicapUnit: 'legs', scale: 12, totalUnit: 'legs' },
  'gaelic-football': { handicapUnit: 'points', scale: 28, totalUnit: 'points' },
  handball: { handicapUnit: 'goals', scale: 24, totalUnit: 'goals' },
  'ice-hockey': { handicapUnit: 'goals', scale: 7, totalUnit: 'goals' },
  'rugby-union': { handicapUnit: 'points', scale: 45, totalUnit: 'points' },
  snooker: { handicapUnit: 'frames', scale: 8, totalUnit: 'frames' },
  tennis: { handicapUnit: 'games', scale: 13, totalUnit: 'games' },
  volleyball: { handicapUnit: 'sets', scale: 5, totalUnit: 'sets' },
};

const round = (value, places = 1) => Number(value.toFixed(places));
const roundHalf = (value) => Math.round(value * 2) / 2;
const logistic = (value) => 1 / (1 + Math.exp(-value));
const wordCount = (value = '') => (value.match(/[\p{L}\p{N}’'-]+/gu) || []).length;

function lineFor(match) {
  const inputModel = match.modelInput;
  const config = marketConfig[match.categorySlug];
  if (!config) throw new Error(`No market configuration for ${match.categorySlug}`);

  const venueEdge = inputModel.venueEdgeA;
  const evidenceScore =
    COEFFICIENTS.strength * inputModel.strengthEdgeA +
    COEFFICIENTS.form * inputModel.formEdgeA +
    venueEdge;
  const rawA = logistic(evidenceScore);
  const reliabilityCap = match.officialStatus === 'verified' ? 1 : 0.35;
  const reliability = Math.min(inputModel.reliability, reliabilityCap);
  const probabilityA = 0.5 + (rawA - 0.5) * reliability;
  const probabilityB = 1 - probabilityA;
  const aIsPick = probabilityA >= probabilityB;
  const pick = aIsPick ? match.participantA : match.participantB;
  const favoriteProbability = Math.max(probabilityA, probabilityB);
  const fairOddsA = 1 / probabilityA;
  const fairOddsB = 1 / probabilityB;

  let confidence = 'low';
  const hasHighAnalysis = wordCount(match.highConfidenceAnalysis) >= 30;
  if (
    favoriteProbability >= 0.7 &&
    match.officialStatus === 'verified' &&
    reliability >= 0.85 &&
    hasHighAnalysis
  ) {
    confidence = 'high';
  } else if (favoriteProbability >= 0.58 && match.officialStatus !== 'unverified') {
    confidence = 'medium';
  }

  const rawHandicap = (favoriteProbability - 0.5) * config.scale;
  const handicapMagnitude = Math.max(0.5, roundHalf(rawHandicap));
  const handicap = `${pick} -${handicapMagnitude.toFixed(1)} ${config.handicapUnit}`;
  const totalAnchor = inputModel.totalAnchor;
  if (typeof totalAnchor !== 'number') {
    throw new Error(`${match.id} has no numeric total anchor`);
  }

  const caveats = [];
  if (match.officialStatus !== 'verified') {
    caveats.push('Fixture verification is incomplete; the line is a low-confidence research prior only.');
  }
  if (match.flags.length) {
    caveats.push('See Flagged for Review before using this row.');
  }
  caveats.push('Fair prices contain no bookmaker margin and are not live odds.');

  return {
    version: MODEL_VERSION,
    independenceStatement: 'OLBG tip percentages, displayed selections and bookmaker prices are excluded from every model input.',
    formula: 'p_raw = logistic(0.42×strength + 0.22×form + venue); p_final = 0.50 + reliability×(p_raw−0.50)',
    inputs: {
      strengthEdgeA: inputModel.strengthEdgeA,
      formEdgeA: inputModel.formEdgeA,
      venueEdgeA: inputModel.venueEdgeA,
      requestedReliability: inputModel.reliability,
      appliedReliability: round(reliability, 2),
      evidenceScore: round(evidenceScore, 3),
      note: inputModel.note,
    },
    winner: {
      selection: pick,
      probabilityPct: round(favoriteProbability * 100, 1),
      fairDecimalOdds: round(1 / favoriteProbability, 2),
      participantAProbabilityPct: round(probabilityA * 100, 1),
      participantAFairDecimalOdds: round(fairOddsA, 2),
      participantBProbabilityPct: round(probabilityB * 100, 1),
      participantBFairDecimalOdds: round(fairOddsB, 2),
    },
    handicap: {
      line: handicap,
      unit: config.handicapUnit,
      modelMargin: handicapMagnitude,
    },
    total: {
      line: `${totalAnchor.toFixed(1)} ${config.totalUnit}`,
      midpoint: totalAnchor,
      unit: config.totalUnit,
      lean: 'midpoint only — no verified pace input for a directional over/under pick',
    },
    confidence,
    rationale: inputModel.note,
    highConfidenceAnalysis: confidence === 'high' ? match.highConfidenceAnalysis : '',
    caveats,
  };
}

const matches = input.matches.map((match) => ({
  id: match.id,
  sport: match.sport,
  categorySlug: match.categorySlug,
  competition: match.competition,
  capturedAt: match.capturedAt,
  origin: match.origin,
  participants: {
    a: match.participantA,
    b: match.participantB,
  },
  schedule: {
    date: match.officialDate,
    time: match.officialTime,
    timezone: match.officialTimezone,
    venue: match.venue,
    verification: match.officialStatus,
  },
  sources: {
    official: match.officialSource,
    discovery: {
      label: 'OLBG category capture (discovery only)',
      url: match.olbgDiscoveryUrl,
    },
  },
  sourceFacts: match.sourceFacts,
  model: lineFor(match),
  flags: match.flags,
  audit: {
    valuesRule: 'Unconfirmed schedule fields are blank; model outputs are explicitly derived estimates, never represented as official facts.',
    reviewedAt: match.capturedAt,
  },
}));

const summary = {
  matchCount: matches.length,
  verifiedCount: matches.filter((match) => match.schedule.verification === 'verified').length,
  partialCount: matches.filter((match) => match.schedule.verification === 'partially-verified').length,
  unverifiedCount: matches.filter((match) => match.schedule.verification === 'unverified').length,
  flaggedMatchCount: matches.filter((match) => match.flags.length).length,
  highConfidenceCount: matches.filter((match) => match.model.confidence === 'high').length,
  categoryCount: new Set(matches.map((match) => match.categorySlug)).size,
};

const output = {
  schemaVersion: '1.0.0',
  generatedAt: input.capturedAt,
  captureWindow: {
    timestampUtc: input.capturedAt,
    label: 'Visible OLBG category rows captured on 21 October 2026; official schedules normalized at the same research cutoff.',
    limitation: 'OLBG pages are volatile and some retain “Load More Tips”. This is a timestamped visible-feed audit, not a claim about undisclosed rows.',
  },
  methodology: {
    modelVersion: MODEL_VERSION,
    coefficients: COEFFICIENTS,
    reliabilityRule: 'Each directional signal is shrunk toward 50%; non-verified fixtures are capped at 0.35 reliability.',
    confidenceRule: 'High requires ≥70% model probability, official fixture verification, ≥0.85 applied reliability, and a unique source-grounded analysis of at least 30 words.',
    pricesRule: 'Fair decimal odds are 1 ÷ model probability with no overround. Handicap and total values are model midpoints, not scraped bookmaker quotes.',
  },
  summary,
  matches,
};

fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`);
console.log(`Built ${matches.length} modeled match rows (${summary.highConfidenceCount} high confidence).`);
