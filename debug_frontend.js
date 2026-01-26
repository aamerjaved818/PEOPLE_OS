/**
 * Test script to verify the complete data flow from backend to frontend
 * Run this in browser console while on the login page
 */

// After you login with root/root, run this in console:
console.log('=== FRONTEND DATA FLOW DEBUG ===\n');

// Check secureStorage
console.log('1. Checking secureStorage:');
console.log('   - token:', localStorage.getItem('token') ? 'Set (hidden)' : 'Not set');
console.log('   - current_user:', localStorage.getItem('current_user'));

// Check what would be in secureStorage
const currentUserStr =
  localStorage.getItem('current_user') || sessionStorage.getItem('current_user');
if (currentUserStr) {
  try {
    const currentUser = JSON.parse(currentUserStr);
    console.log('\n2. Current User from storage:');
    console.log(currentUser);
    console.log(`   - role: ${currentUser.role}`);
    console.log(`   - isSystemUser: ${currentUser.isSystemUser}`);
  } catch (e) {
    console.error('Failed to parse current_user', e);
  }
}

// Check the Zustand store
console.log('\n3. Checking Zustand store (useOrgStore):');
setTimeout(() => {
  // This requires the store to be exported or accessible globally
  // For now, just note that you should check:
  console.log('   - Check browser DevTools -> React -> useOrgStore');
  console.log('   - Look for: currentUser, users');
  console.log('   - Verify isSystemUser is present in users array');
}, 100);

console.log('\n4. Manual verification:');
console.log('   - Open Network tab');
console.log('   - Look for GET /api/v1/users');
console.log('   - Check response has isSystemUser field');

console.log('\n=== END DEBUG ===');
