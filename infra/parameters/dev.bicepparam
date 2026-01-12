using '../main.bicep'

param environmentName = 'dev'
param location = 'eastus2'
param baseName = 'aics'
param tags = {
  project: 'ai-foundry-customer-support-demo'
  environment: 'dev'
  owner: 'demo'
}
