// Azure OpenAI Service

@description('Base name for resources')
param baseName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: 'oai-${baseName}'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'oai-${baseName}'
    publicNetworkAccess: 'Enabled'
  }
}

// GPT-4o deployment for agents
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAiAccount
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
  }
}

// Text embedding deployment for RAG
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAiAccount
  name: 'text-embedding-3-small'
  sku: {
    name: 'Standard'
    capacity: 120
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
  }
  dependsOn: [gpt4oDeployment]
}

output openAiAccountId string = openAiAccount.id
output openAiEndpoint string = openAiAccount.properties.endpoint
output openAiAccountName string = openAiAccount.name
