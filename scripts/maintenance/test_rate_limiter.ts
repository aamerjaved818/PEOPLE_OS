import { RateLimiter } from './src/utils/security';

async function testRateLimiter() {
  console.log('--- Testing RateLimiter peekRequest ---');
  const limiter = new RateLimiter(5, 10000); // 5 requests per 10s

  console.log('Initial state:', limiter.peekRequest() ? 'Can request' : 'Blocked');

  for (let i = 0; i < 5; i++) {
    const start = limiter.peekRequest();
    const consumed = limiter.canMakeRequest();
    console.log(`Request ${i + 1}: Peek=${start}, Consumed=${consumed}`);
  }

  console.log(
    'After 5 requests:',
    limiter.peekRequest() ? 'Can request (FAILURE)' : 'Blocked (SUCCESS)'
  );

  // Test non-consuming check
  console.log('\n--- Testing Non-consuming Check ---');
  const limiter2 = new RateLimiter(1, 10000);
  console.log('Peek 1:', limiter2.peekRequest());
  console.log('Peek 2:', limiter2.peekRequest());
  console.log('Consume 1:', limiter2.canMakeRequest());
  console.log('Peek 3:', limiter2.peekRequest() ? 'Can request (FAILURE)' : 'Blocked (SUCCESS)');
}

testRateLimiter().catch(console.error);
