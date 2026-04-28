# Design

Semantic routing layer for Hermes using Pinecone.

Flow:
User → embed → Pinecone → skill candidates → filter → Hermes skill_view()
