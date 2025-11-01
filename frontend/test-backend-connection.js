// Simple test script to verify backend connection
const API_BASE = "http://127.0.0.1:5000";

async function testConnection() {
  console.log("Testing connection to Zoid GPT backend...");
  
  try {
    // Test health endpoint
    console.log("Checking health endpoint...");
    const healthResponse = await fetch(`${API_BASE}/health`);
    const healthData = await healthResponse.json();
    console.log("Health check:", healthData);
    
    // Test generate endpoint
    console.log("Testing generate endpoint...");
    const generateResponse = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt: "Hello, world!" })
    });
    
    const generateData = await generateResponse.json();
    console.log("Generate response:", generateData);
    
    console.log("All tests passed! Frontend should work correctly.");
  } catch (error) {
    console.error("Connection test failed:", error.message);
    console.log("Please ensure the backend server is running on port 5000");
  }
}

testConnection();