# 🚨 URGENT: Frontend AI Tool Selection Fix

## 🎯 IMMEDIATE ACTION REQUIRED

The frontend AI is using the WRONG tool for bed status queries. Here's how to fix it:

### ❌ CURRENT PROBLEM:
Frontend AI is calling:
```javascript
{
  "tool": "list_beds",
  "arguments": {}
}
```

### ✅ REQUIRED FIX:
Frontend AI MUST call:
```javascript
{
  "tool": "get_bed_status_with_time_remaining", 
  "arguments": {
    "bed_id": "302A"
  }
}
```

---

## 🔧 FRONTEND INTEGRATION STEPS:

### Step 1: Update System Prompt
Add this to your frontend AI system prompt:

```
CRITICAL TOOL SELECTION RULE:
When user asks about ANY specific bed status (e.g., "check bed 302A status"), 
ALWAYS use tool: "get_bed_status_with_time_remaining" 
NEVER use: "list_beds"
```

### Step 2: Add Pre-Processing Logic
Before calling any tool, check the user query:

```javascript
function selectCorrectTool(userQuery) {
  // Check for individual bed queries
  const bedPattern = /bed\s+(\w+)\s+status|check\s+bed\s+(\w+)|bed\s+(\w+)/i;
  const match = userQuery.match(bedPattern);
  
  if (match) {
    const bedId = match[1] || match[2] || match[3];
    return {
      tool: "get_bed_status_with_time_remaining",
      arguments: { bed_id: bedId }
    };
  }
  
  // Default to list for multiple beds
  if (userQuery.includes("list beds") || userQuery.includes("all beds")) {
    return {
      tool: "list_beds",
      arguments: {}
    };
  }
}
```

### Step 3: Test the Fix
User says: "check bed 302A status"
Expected call:
```json
{
  "tool": "get_bed_status_with_time_remaining",
  "arguments": {
    "bed_id": "302A"
  }
}
```

Expected response:
```json
{
  "success": true,
  "bed_number": "302A",
  "current_status": "available",
  "room_number": "302",
  "process_status": "none",
  "time_remaining_minutes": 0,
  "progress_percentage": 100
}
```

---

## 🎯 VERIFICATION:

### ✅ Correct Response Format:
```
🛏️ **Bed 302A Status:**
- **Current Status:** Available ✅  
- **Room:** 302
- **Cleaning Process:** Completed (100%)
- **Ready for:** New patient assignment

✅ This bed completed its 30-minute cleaning cycle and is ready for use.
```

### ❌ Wrong Response (what you're getting now):
```
"The status for bed number 302A is not listed..."
```

---

## 🚨 CRITICAL: 
The backend is working correctly. Bed 302A IS available and ready. 
The frontend just needs to use the correct tool to get the detailed information.

**USE: get_bed_status_with_time_remaining**
**NOT: list_beds**
