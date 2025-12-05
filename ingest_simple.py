"""
Simple, stable Qdrant ingestion script with minimal dependencies.
Ingest Docusaurus markdown docs to Qdrant with proper error handling.
"""
import os
import sys
import uuid
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
DOCS_PATH = Path(__file__).parent.parent / "my-ai-book" / "docs"

print("=" * 70)
print("Qdrant Ingestion - Simple Version")
print("=" * 70)
print(f"Collection: {QDRANT_COLLECTION_NAME}")
print(f"Docs path: {DOCS_PATH}")
print()

# Try imports
try:
    from qdrant_client import QdrantClient, models
    print("✓ qdrant-client imported")
except ImportError as e:
    print(f"✗ Failed to import qdrant-client: {e}")
    sys.exit(1)

try:
    from fastembed import TextEmbedding
    print("✓ fastembed imported")
except ImportError as e:
    print(f"✗ Failed to import fastembed: {e}")
    sys.exit(1)

print()

# Connect to Qdrant
print("Connecting to Qdrant Cloud...")
try:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30.0,
        prefer_grpc=False,
        check_compatibility=False,
    )
    print("✓ Connected to Qdrant Cloud")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)

# Check collection exists
print(f"\nChecking collection '{QDRANT_COLLECTION_NAME}'...")
try:
    info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
    print(f"✓ Collection exists")
except Exception as e:
    print(f"✗ Collection not found: {e}")
    print("\nPlease create the collection in Qdrant Cloud dashboard:")
    print("  - Go to https://cloud.qdrant.io")
    print("  - Create collection: textbook_chunks (384 dimensions, Cosine distance)")
    sys.exit(1)

# Load embedding model
print("\nLoading FastEmbed model (BAAI/bge-small-en-v1.5)...")
try:
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("✓ Model loaded")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    sys.exit(1)

# Find markdown files
print(f"\nSearching for markdown files in {DOCS_PATH}...")
md_files = sorted(list(DOCS_PATH.rglob("*.md")))
print(f"✓ Found {len(md_files)} markdown files")

if not md_files:
    print("✗ No markdown files found")
    sys.exit(1)

print()

# Ingest files
total_chunks = 0
total_files = 0

for file_idx, md_file in enumerate(md_files, 1):
    try:
        print(f"[{file_idx}/{len(md_files)}] {md_file.relative_to(DOCS_PATH)}")
        
        # Read file
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            print("  ⚠ Empty file, skipping")
            continue
        
        # Simple chunking (split by paragraphs)
        chunks = []
        for para in content.split('\n\n'):
            para = para.strip()
            if para and len(para) > 10:  # Only chunks with meaningful content
                chunks.append(para)
        
        if not chunks:
            print("  ⚠ No content chunks, skipping")
            continue
        
        print(f"  → {len(chunks)} chunks")
        
        # Generate embeddings and points
        points = []
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = list(embedding_model.embed([chunk]))[0]
                
                # Create point
                point = models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=list(embedding),
                    payload={
                        "content": chunk[:1000],  # Limit payload size
                        "source_file": str(md_file.relative_to(DOCS_PATH)),
                        "chunk_index": chunk_idx,
                    },
                )
                points.append(point)
            except Exception as e:
                print(f"    ✗ Chunk {chunk_idx}: {e}")
                continue
        
        if not points:
            print("  ⚠ No embeddings generated, skipping")
            continue
        
        # Upsert to Qdrant (single batch per file)
        try:
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=points,
            )
            print(f"  ✓ Upserted {len(points)} chunks")
            total_chunks += len(points)
            total_files += 1
        except Exception as e:
            print(f"  ✗ Upsert failed: {e}")
            continue
        
        # Small delay between files to avoid rate limiting
        time.sleep(0.5)
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        continue

print()
print("=" * 70)
print(f"✓ Ingestion complete!")
print(f"  Total files: {total_files}")
print(f"  Total chunks: {total_chunks}")
print("=" * 70)
