// Main Bicep template for Azure AI Foundry Customer Support Demo
targetScope = 'subscription'

@description('Environment name (dev, staging, prod)')
param environmentName string = 'dev'

@description('Primary location for resources')
param location string = 'eastus2'

@description('Base name for resources')
param baseName string = 'aics'

@description('Tags to apply to all resources')
param tags object = {
  project: 'ai-foundry-customer-support-demo'
  environment: environmentName
}

var resourceGroupName = 'rg-${baseName}-${environmentName}'
var uniqueSuffix = uniqueString(subscription().subscriptionId, resourceGroupName)

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// Application Insights & Log Analytics
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
  }
}

// Storage Account (for AI Foundry and data)
module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    uniqueSuffix: uniqueSuffix
    tags: tags
  }
}

// Azure OpenAI Service
module openai 'modules/openai.bicep' = {
  name: 'openai-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
  }
}

// Azure AI Search
module search 'modules/search.bicep' = {
  name: 'search-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
  }
}

// Cosmos DB
module cosmos 'modules/cosmos.bicep' = {
  name: 'cosmos-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
  }
}

// AI Foundry Hub and Project
module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'ai-foundry-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
    storageAccountId: storage.outputs.storageAccountId
    applicationInsightsId: monitoring.outputs.applicationInsightsId
    openAiAccountId: openai.outputs.openAiAccountId
    searchServiceId: search.outputs.searchServiceId
  }
}

// Container Registry
module acr 'modules/container-registry.bicep' = {
  name: 'acr-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    uniqueSuffix: uniqueSuffix
    tags: tags
  }
}

// Container Apps Environment and Backend App
module containerApps 'modules/container-apps.bicep' = {
  name: 'container-apps-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    acrLoginServer: acr.outputs.acrLoginServer
    aiFoundryProjectEndpoint: aiFoundry.outputs.projectEndpoint
    cosmosEndpoint: cosmos.outputs.cosmosEndpoint
    searchEndpoint: search.outputs.searchEndpoint
    openAiEndpoint: openai.outputs.openAiEndpoint
  }
}

// Static Web App for Frontend
module staticWebApp 'modules/static-web-app.bicep' = {
  name: 'swa-deployment'
  scope: rg
  params: {
    baseName: baseName
    location: location
    tags: tags
    backendUrl: containerApps.outputs.backendUrl
  }
}

// Outputs
output resourceGroupName string = rg.name
output backendUrl string = containerApps.outputs.backendUrl
output frontendUrl string = staticWebApp.outputs.staticWebAppUrl
output aiFoundryProjectEndpoint string = aiFoundry.outputs.projectEndpoint
output acrLoginServer string = acr.outputs.acrLoginServer
