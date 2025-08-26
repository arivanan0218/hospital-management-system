📋 **FRONTEND DEBUGGING INSTRUCTIONS**

✅ **Debugging Steps:**

1. **Open Frontend**: Go to http://localhost:3000
2. **Open Console**: Press F12 → Console tab
3. **Test Query**: Type "check bed 401A status"
4. **Watch Console**: Look for these debug messages:
   ```
   🔍 Analyzing message: check bed 401a status
   🔍 Full userMessage: check bed 401A status
   🎯 BED STATUS CHECK TRIGGERED!
   🔍 Detected bed status query, parameters: {bed_id: "401A"}
   ✅ Added get_bed_status_with_time_remaining to toolsNeeded
   🔧 Tools needed: [{name: "get_bed_status_with_time_remaining", arguments: {bed_id: "401A"}}]
   ```

❌ **If you see instead:**
   ```
   🏥 GENERIC BED LISTING TRIGGERED
   ⚠️ Added list_beds to toolsNeeded
   🔧 Tools needed: [{name: "list_beds", arguments: {}}]
   ```

🔍 **What to look for:**
- Does the bed status condition trigger?
- What tools are in the final toolsNeeded array?
- Are there any errors in the console?

💡 **Alternative Test:**
If frontend console doesn't work, you can test the logic directly:

1. Open browser console on any page
2. Paste and run:
```javascript
const message = "check bed 401a status";
const hasKeywords = message.includes('bed') && 
  (message.includes('cleaning') || message.includes('status') || 
   message.includes('turnover') || message.includes('remaining') || message.includes('time'));
console.log('Should trigger bed status:', hasKeywords);
```

This should return `true` ✅
