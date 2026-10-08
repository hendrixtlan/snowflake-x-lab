-- CLOUD / PAID: optional licensed/synthetic poster image, event flyer and audio assets.
-- Upload files to @MUSIC_LAB.AI.MEDIA_STAGE manually; NEVER place unlicensed artist media.
CREATE STAGE IF NOT EXISTS MUSIC_LAB.AI.MEDIA_STAGE ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- 1. Extract date/venue/price from a staged poster (PNG/JPEG/PDF).
SELECT AI_EXTRACT(
   file => TO_FILE('@MUSIC_LAB.AI.MEDIA_STAGE', 'flyer.png'),
   responseFormat => [
      ['venue', 'What venue is advertised?'],
      ['date', 'What date is advertised?'],
      ['ticket_price', 'What price is shown?']
   ]
) AS POSTER_FACTS;

-- 2. Image-based, model-dependent semantic understanding.
SELECT AI_COMPLETE('claude-sonnet-4-6',
  'Describe the event poster accurately. Mark uncertain visual details.',
  TO_FILE('@MUSIC_LAB.AI.MEDIA_STAGE','flyer.png')) AS IMAGE_DESCRIPTION;

-- 3. Audio transcription with word timestamps for a synthetic radio/podcast excerpt.
SELECT AI_TRANSCRIBE(
  TO_FILE('@MUSIC_LAB.AI.MEDIA_STAGE','event_promo.wav'),
  OBJECT_CONSTRUCT('timestamp_granularity','word')) AS TRANSCRIPT;

-- Measure extraction accuracy and transcription WER vs separately prepared human labels.
-- None of these execute unless user stages authorized sample files.
