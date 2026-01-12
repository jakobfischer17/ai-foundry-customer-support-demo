// Container Apps Environment and Backend API

@description('Base name for resources')
param baseName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

@description('ACR login server')
param acrLoginServer string

@description('AI Foundry project endpoint')
param aiFoundryProjectEndpoint string

@description('Cosmos DB endpoint')
param cosmosEndpoint string

@description('AI Search endpoint')
param searchEndpoint string

@description('Azure OpenAI endpoint')
param openAiEndpoint string

// Container Apps Environment
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${baseName}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey
      }
    }
  }
}

// Backend API Container App
resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-${baseName}-api'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest' // Placeholder
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'AI_FOUNDRY_PROJECT_ENDPOINT'
              value: aiFoundryProjectEndpoint
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmosEndpoint
            }
            {
              name: 'SEARCH_ENDPOINT'
              value: searchEndpoint
            }
            {
              name: 'OPENAI_ENDPOINT'
              value: openAiEndpoint
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

output containerAppsEnvId string = containerAppsEnv.id
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output backendAppName string = backendApp.name
