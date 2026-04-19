/**
 * Hard Cap Billing Kill Switch
 * Automatically unlinks the billing account from the project when budget is reached.
 */
const {CloudBillingClient} = require('@google-cloud/billing');
const billing = new CloudBillingClient();

exports.stopBilling = async (pubsubMessage) => {
  const data = JSON.parse(Buffer.from(pubsubMessage.data, 'base64').toString());
  const cost = data.costAmount;
  const budget = data.budgetAmount;
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;

  console.log(`Checking budget for ${projectId}: Current Cost $${cost} / Budget $${budget}`);

  // Only trigger if cost meets or exceeds the configured budget limit
  if (cost >= budget) {
    console.log(`Budget exceeded: ${cost}/${budget}. Disabling billing for ${projectId}...`);
    
    try {
      const name = `projects/${projectId}`;
      
      // Update project billing info to remove the billing account
      // This is the action that stops all billable services immediately.
      await billing.updateProjectBillingInfo({
        name,
        projectBillingInfo: { 
          billingAccountName: '' // Setting to empty string unlinks the account
        }
      });
      
      console.log('Success: Billing disabled and project capped.');
    } catch (error) {
      console.error('Error disabling billing:', error);
      throw error;
    }
  } else {
    console.log('Budget threshold not yet reached. No action taken.');
  }
};
