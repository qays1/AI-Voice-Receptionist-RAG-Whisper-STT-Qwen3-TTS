import os
import sys
from qdrant_client import QdrantClient

# Add current directory to path
sys.path.append(os.getcwd())

def inspect_knowledge():
    # Path to your local Qdrant storage
    storage_path = os.path.join(os.getcwd(), "backend/data/qdrant_local")
    
    if not os.path.exists(storage_path):
        print(f"❌ Storage path not found: {storage_path}")
        return

    client = QdrantClient(path=storage_path)
    collection_name = "user_knowledge"
    
    try:
        collection_info = client.get_collection(collection_name)
        print(f"--- Collection: {collection_name} ---")
        print(f"Total Points: {collection_info.points_count}")
        print("-" * 30)

        # Scroll through points (retrieve data)
        # We'll fetch the first 20 points to see what's inside
        points, _ = client.scroll(
            collection_name=collection_name,
            limit=20,
            with_payload=True,
            with_vectors=False
        )

        if not points:
            print("No data found in this collection yet.")
            return

        for point in points:
            user_id = point.payload.get("user_id", "Unknown")
            content = point.payload.get("content", "")
            filename = point.payload.get("metadata", {}).get("source", "Unknown file")
            
            print(f"👤 User ID: {user_id}")
            print(f"📄 File: {filename}")
            print(f"📝 Content Snippet: {content[:100]}...")
            print("-" * 20)

    except Exception as e:
        print(f"❌ Error accessing collection: {e}")

if __name__ == "__main__":
    inspect_knowledge()
