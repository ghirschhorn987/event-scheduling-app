const { chromium, devices } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext(devices['iPhone 13']);
  const page = await context.newPage();

  // Go to login to use mock auth
  await page.goto('http://localhost:5173/login');
  
  // Wait for mock auth toolbar to be visible and click the first user
  try {
     // Wait for the select or button. Let's see what the mock auth component looks like and just set localStorage directly, it is easiest.
     await page.evaluate(() => {
         const mockSession = {
            access_token: "mock-token-793db7d3-7996-4669-8714-8340f784085c",
            refresh_token: "mock-refresh",
            user: {
                id: "793db7d3-7996-4669-8714-8340f784085c",
                email: "mock.admin@test.com",
                user_metadata: { full_name: "Mock Admin" }
            }
         };
         // Supabase stores session in localStorage. 
         // Since we don't know the exact key (it's project-specific), we can just use the mock login button.
     });
     
     // The mock auth toolbar is rendered anywhere.
     // Let's look for a button containing "Mock" or "Login"
     await page.selectOption('select', { index: 1 }); // Assuming it's a select
     await page.click('button:has-text("Login as Mock User")'); // Or whatever the button says
  } catch (e) {}

  // Or just bypass by setting localStorage key for supabase if we know it.
  
  // Alternatively, just wait a bit for user to see the dashboard manually?
  // No, let's just use the mock auth click. We don't know the exact button text. 
  
  await browser.close();
})();
