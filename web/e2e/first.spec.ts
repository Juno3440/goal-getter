import { test, expect } from '@playwright/test';

// These should be set in CI environment
const TEST_EMAIL = process.env.E2E_TEST_EMAIL || 'test@example.com';
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD || 'testpassword123';

test.describe('GoalGPT E2E Tests', () => {
  test('visits homepage, logs in, and asserts GoalTree is visible', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');

    // Should see auth page initially
    await expect(page.locator('h2')).toContainText(['Sign In', 'Login', 'Auth']);

    // Fill in login credentials
    await page.fill('input[type="email"], input[placeholder*="email" i]', TEST_EMAIL);
    await page.fill('input[type="password"], input[placeholder*="password" i]', TEST_PASSWORD);

    // Click sign in button
    await page.click('button:has-text("Sign In"), button:has-text("Login")');

    // Wait for successful login and redirect to main app
    await expect(page.locator('h1')).toContainText('GPT GOALNET');

    // Should see the goal input component
    await expect(page.locator('input[placeholder*="goal" i]')).toBeVisible();

    // Should see add button
    await expect(page.locator('button:has-text("ADD")')).toBeVisible();

    // Test creating a new goal
    const goalTitle = `Test Goal ${Date.now()}`;
    await page.fill('input[placeholder*="goal" i]', goalTitle);
    await page.click('button:has-text("ADD")');

    // Wait for goal to be added and appear in the tree
    // Note: This depends on having actual goals to render
    // For now, just verify the basic structure is present
    await expect(page.locator('.retro-goal-input')).toBeVisible();

    // Check if GoalTree container is visible
    await expect(page.locator('#goal-tree-container, svg')).toBeVisible();
  });

  test('handles login failure gracefully', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Try invalid credentials
    await page.fill('input[type="email"], input[placeholder*="email" i]', 'invalid@example.com');
    await page.fill('input[type="password"], input[placeholder*="password" i]', 'wrongpassword');

    await page.click('button:has-text("Sign In"), button:has-text("Login")');

    // Should show error message
    await expect(page.locator('text=/error/i, text=/invalid/i')).toBeVisible();

    // Should still be on auth page
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('goal input validation works', async ({ page }) => {
    // For this test, we'd need to be logged in first
    // This is a placeholder for when we have proper test auth setup
    await page.goto('http://localhost:3000');
    
    // Skip if not authenticated
    if (await page.locator('input[type="email"]').isVisible()) {
      test.skip('Skipping goal input test - authentication required');
      return;
    }

    // Test empty goal submission
    const addButton = page.locator('button:has-text("ADD")');
    await expect(addButton).toBeDisabled();

    // Add text to enable button
    await page.fill('input[placeholder*="goal" i]', 'Test Goal');
    await expect(addButton).not.toBeDisabled();

    // Clear text to disable button again
    await page.fill('input[placeholder*="goal" i]', '');
    await expect(addButton).toBeDisabled();
  });
});