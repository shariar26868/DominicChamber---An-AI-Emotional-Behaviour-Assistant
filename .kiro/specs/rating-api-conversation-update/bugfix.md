# Bugfix Requirements Document

## Introduction

The ratings API (`POST /profiles/{profile_id}/ratings`) currently accepts a single flat score and an optional note. There is no mechanism to pass a `conversation_id`, fetch the conversation messages, generate AI-driven rating questions from that conversation, or collect per-question scores and thoughts from the user. This makes it impossible to implement a conversation-aware rating flow where the backend drives question generation and the client collects structured feedback per question.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a client sends a rating request with a `conversation_id` THEN the system has no endpoint or schema to accept it, returning a validation error or ignoring the field entirely.

1.2 WHEN a rating submission is received THEN the system does not fetch the associated conversation or its messages, so no conversation context is available for generating questions.

1.3 WHEN a rating submission is received THEN the system does not call the AI to generate rating questions based on conversation content, so no questions are produced.

1.4 WHEN a client tries to submit per-question ratings (each with a question, a score, and an optional thought) THEN the system has no schema or storage model to accept that structure.

1.5 WHEN a rating session is stored THEN the system persists only a single `score` integer and an optional `note`, discarding all per-question context.

### Expected Behavior (Correct)

2.1 WHEN a client sends `POST /profiles/{profile_id}/ratings/questions` with a valid `conversation_id` THEN the system SHALL fetch the conversation messages for that `conversation_id`.

2.2 WHEN the conversation messages are fetched THEN the system SHALL call the AI (OpenAI) to generate 3–5 rating questions tailored to the content of that conversation.

2.3 WHEN the AI generates rating questions THEN the system SHALL return the list of questions to the client so the user can rate each one.

2.4 WHEN a client sends `POST /profiles/{profile_id}/ratings` with a `conversation_id` and a list of per-question rating entries (each containing a question, a numeric score, and an optional thought) THEN the system SHALL validate and store the full rating session.

2.5 WHEN a rating session is stored THEN the system SHALL persist all question-score-thought entries together as a single document linked to the `profile_id`, `user_id`, and `conversation_id`.

2.6 WHEN a rating session is successfully created THEN the system SHALL return a response that includes the stored per-question entries and the associated `conversation_id`.

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a valid `profile_id` is provided THEN the system SHALL CONTINUE TO validate that the profile exists and return 404 if it does not.

3.2 WHEN an invalid or malformed `profile_id`, `user_id`, or `conversation_id` is provided THEN the system SHALL CONTINUE TO return an appropriate error response (422 or 400).

3.3 WHEN ratings are retrieved for a profile via `GET /profiles/{profile_id}/ratings` THEN the system SHALL CONTINUE TO return all rating sessions associated with that profile.

3.4 WHEN an average rating is requested via `GET /profiles/{profile_id}/ratings/average` THEN the system SHALL CONTINUE TO return an aggregated score for the profile, computed from the per-question scores in the stored sessions.

---

## Bug Condition (Pseudocode)

**Bug Condition Function** — identifies requests that expose the missing conversation-based rating flow:

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type RatingRequest
  OUTPUT: boolean

  // Bug is triggered when the client attempts to use
  // the conversation-based rating flow
  RETURN X.has_conversation_id = true
      OR X.expects_ai_generated_questions = true
      OR X.entries IS List<{question, score, thought}>
END FUNCTION
```

**Property: Fix Checking**

```pascal
// Property: Fix Checking — Question Generation
FOR ALL X WHERE isBugCondition(X) AND X.step = "generate_questions" DO
  result ← generateRatingQuestions'(X)
  ASSERT result.status = 200
    AND result.body.questions IS List
    AND length(result.body.questions) >= 3
    AND length(result.body.questions) <= 5
END FOR

// Property: Fix Checking — Rating Submission
FOR ALL X WHERE isBugCondition(X) AND X.step = "submit_ratings" DO
  result ← submitRating'(X)
  ASSERT result.status = 201
    AND result.body contains per_question_entries
    AND each entry has (question, score, thought)
    AND session is persisted with profile_id AND user_id AND conversation_id
END FOR
```

**Property: Preservation Checking**

```pascal
// Property: Preservation Checking
FOR ALL X WHERE NOT isBugCondition(X) DO
  // Non-buggy inputs: profile validation, invalid IDs, fetch/average operations
  ASSERT F(X) = F'(X)
END FOR
```
