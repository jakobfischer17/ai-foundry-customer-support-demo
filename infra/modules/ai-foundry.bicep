// Azure AI Foundry Hub and Project

@description('Base name for resources')
param baseName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object

@description('Storage account ID for AI Foundry')
param storageAccountId string

@description('Application Insights ID')
param applicationInsightsId string

@description('Azure OpenAI account ID')
param openAiAccountId string

@description('AI Search service ID')
param searchServiceId string

// AI Foundry Hub (formerly AI Studio Hub)
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: 'hub-${baseName}'
  location: location
  tags: tags
  kind: 'Hub'
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Customer Support AI Hub'
    description: 'AI Foundry Hub for Customer Support Agent Demo'
    storageAccount: storageAccountId
    applicationInsights: applicationInsightsId
    publicNetworkAccess: 'Enabled'
  }
}

// AI Foundry Project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: 'proj-${baseName}'
  location: location
  tags: tags
  kind: 'Project'
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Customer Support Agents'
    description: 'Project for multi-agent customer support orchestration'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

// Connection to Azure OpenAI
resource openAiConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = {
  parent: aiHub
  name: 'azure-openai'
  properties: {
    category: 'AzureOpenAI'
    target: openAiAccountId
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: openAiAccountId
    }
  }
}

// Connection to AI Search
resource searchConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = {
  parent: aiHub
  name: 'azure-ai-search'
  properties: {
    category: 'CognitiveSearch'
    target: searchServiceId
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ResourceId: searchServiceId
    }
  }
}

output hubId string = aiHub.id
output projectId string = aiProject.id
output projectEndpoint string = 'https://${location}.api.azureml.ms/discovery/workspaces/${aiProject.id}'
output projectName string = aiProject.name
