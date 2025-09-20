#!/usr/bin/env python3
"""
Test script for the unified AI client supporting both Gemini and OpenAI APIs
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .ai_client import get_ai_client, ai_client_context, ConcurrentAIClient
    from logging_config import setup_logging
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_api_detection():
    """Test automatic API type detection"""
    load_dotenv(override=True)
    
    print("=== API Detection Test ===")
    google_api_base = os.getenv('GOOGLE_API_BASE', '')
    print(f"GOOGLE_API_BASE: {google_api_base}")
    
    client = ConcurrentAIClient(api_type="auto")
    client.initialize()
    
    detected_type = client.get_api_type()
    print(f"Detected API type: {detected_type}")
    
    client.shutdown()
    return detected_type

def test_sync_messages():
    """Test synchronous message sending"""
    print("\n=== Synchronous Messages Test ===")
    
    try:
        client = get_ai_client()
        
        # Test simple message
        print("Sending: 'Hello, what is AI?'")
        response = client.send_message("Hello, what is AI?")
        print(f"API Type: {response.model_type}")
        print(f"Response: {response.content[:200]}...")
        print(f"Session ID: {response.session_id}")
        
        # Test follow-up message in same session
        print("\nSending follow-up: 'Can you explain machine learning?'")
        response2 = client.send_message("Can you explain machine learning?", session_id=response.session_id)
        print(f"Response: {response2.content[:200]}...")
        print(f"Same session: {response.session_id == response2.session_id}")
        
        # Test batch messages
        print("\nTesting batch messages...")
        messages = [
            "What is Python?",
            "What is literature review?",
            "How to conduct systematic research?"
        ]
        responses = client.send_messages_batch(messages)
        
        for i, resp in enumerate(responses):
            if resp:
                print(f"Batch {i+1}: {resp.content[:100]}...")
            else:
                print(f"Batch {i+1}: Failed")
        
        print(f"Active sessions: {client.get_active_sessions()}")
        
    except Exception as e:
        print(f"Error in sync test: {e}")
        import traceback
        traceback.print_exc()

async def test_async_messages():
    """Test asynchronous message sending"""
    print("\n=== Asynchronous Messages Test ===")
    
    try:
        async with ai_client_context() as client:
            # Test async message
            print("Sending async: 'What is academic research?'")
            response = await client.send_message_async("What is academic research?")
            print(f"API Type: {response.model_type}")
            print(f"Async Response: {response.content[:200]}...")
            
            # Test async batch
            print("\nTesting async batch...")
            messages = [
                "What is data analysis?",
                "How to write a research paper?",
                "What are research methodologies?"
            ]
            responses = await client.send_messages_batch_async(messages)
            
            for i, resp in enumerate(responses):
                if resp:
                    print(f"Async Batch {i+1}: {resp.content[:100]}...")
                else:
                    print(f"Async Batch {i+1}: Failed")
                    
    except Exception as e:
        print(f"Error in async test: {e}")
        import traceback
        traceback.print_exc()

def test_session_management():
    """Test session creation and management"""
    print("\n=== Session Management Test ===")
    
    try:
        client = get_ai_client()
        
        # Create multiple sessions
        session1 = client.create_session()
        session2 = client.create_session()
        
        print(f"Created sessions: {session1}, {session2}")
        
        # Send messages to different sessions
        resp1 = client.send_message("My name is Alice", session_id=session1)
        resp2 = client.send_message("My name is Bob", session_id=session2)
        
        print(f"Session 1 response: {resp1.content[:100]}...")
        print(f"Session 2 response: {resp2.content[:100]}...")
        
        # Test memory in sessions
        resp1_follow = client.send_message("What is my name?", session_id=session1)
        resp2_follow = client.send_message("What is my name?", session_id=session2)
        
        print(f"Session 1 remembers: {resp1_follow.content[:100]}...")
        print(f"Session 2 remembers: {resp2_follow.content[:100]}...")
        
        # Close sessions
        client.close_session(session1)
        client.close_session(session2)
        
        print(f"Active sessions after cleanup: {client.get_active_sessions()}")
        
    except Exception as e:
        print(f"Error in session test: {e}")
        import traceback
        traceback.print_exc()

def test_api_switching():
    """Test manual API type switching"""
    print("\n=== API Switching Test ===")
    
    try:
        # Test with forced Gemini (if available)
        print("Testing with forced API types...")
        
        load_dotenv(override=True)
        google_api_base = os.getenv('GOOGLE_API_BASE', '')
        
        if '/v1' in google_api_base or 'openai' in google_api_base.lower():
            print("Detected OpenAI-compatible endpoint")
            client_openai = ConcurrentAIClient(api_type="openai")
            client_openai.initialize()
            
            response = client_openai.send_message("Test OpenAI API")
            print(f"OpenAI Response: {response.content[:100]}...")
            print(f"Detected type: {client_openai.get_api_type()}")
            
            client_openai.shutdown()
        else:
            print("Detected Gemini endpoint")
            # Would test Gemini here if we had a real Gemini endpoint
            
    except Exception as e:
        print(f"Error in API switching test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    # Setup logging
    setup_logging()
    
    print("Starting AI Client Tests")
    print("=" * 50)
    
    # Test API detection
    detected_type = test_api_detection()
    
    # Test synchronous operations
    test_sync_messages()
    
    # Test asynchronous operations
    asyncio.run(test_async_messages())
    
    # Test session management
    test_session_management()
    
    # Test API switching
    test_api_switching()
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()
