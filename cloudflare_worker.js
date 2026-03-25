/**
 * Andile Cloudflare Worker
 * 
 * Lightweight Andile that runs on Cloudflare Workers
 * Free tier: 100k requests/day
 */

const ANDILE_IDENTITY = {
  name: "Andile Sizophila Mchunu",
  moniker: "Skywalkingzulu",
  username: "Skywalkingzulu1",
  instagram: "https://www.instagram.com/skywalkingzulu/",
  owner: "Andile Sizophila Mchunu"
};

// Simple response generator (no LLM - would need external API)
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
  
  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }
  
  // Routes
  if (path === "/") {
    return new Response(JSON.stringify({
      status: "active",
      andile: ANDILE_IDENTITY,
      message: "Andile is running on Cloudflare Workers",
      endpoints: ["/", "/identity", "/status", "/think"]
    }, null, 2), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  
  if (path === "/identity") {
    return new Response(JSON.stringify(ANDILE_IDENTITY, null, 2), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  
  if (path === "/status") {
    // Get state from KV
    const state = await ANDILE_STATE.get("state");
    return new Response(JSON.stringify({
      status: "running",
      location: "cloudflare_workers",
      identity: ANDILE_IDENTITY,
      state: state ? JSON.parse(state) : null,
      timestamp: new Date().toISOString()
    }, null, 2), {
      headers: { ...corsHeaders, "Content-Type": "application/json" }
    });
  }
  
  if (path === "/think" && request.method === "POST") {
    try {
      const body = await request.json();
      const prompt = body.prompt;
      
      // For actual thinking, would need to call external LLM API
      // This is a placeholder response
      const response = {
        thought: `Andile thinking about: ${prompt}`,
        identity: ANDILE_IDENTITY,
        note: "Full LLM requires external API (use Ollama or other provider)"
      };
      
      return new Response(JSON.stringify(response, null, 2), {
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  }
  
  // 404
  return new Response(JSON.stringify({ error: "Not found" }), {
    status: 404,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
}

export default {
  async fetch(request, env, ctx) {
    return handleRequest(request);
  },
  
  async scheduled(event, env, ctx) {
    // Scheduled task - run every hour
    // Update state, check airdrops, etc.
    console.log("Andile scheduled task running...");
    
    // This would run background tasks
    // For now, just log
  }
};
