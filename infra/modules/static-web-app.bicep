// Azure Static Web App for Frontend

@description('Base name for resources')
param baseName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object

@description('Backend API URL')
param backendUrl string

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: 'swa-${baseName}'
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'dist'
    }
  }
}

// App settings for backend URL
resource appSettings 'Microsoft.Web/staticSites/config@2023-12-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    VITE_API_URL: backendUrl
  }
}

output staticWebAppId string = staticWebApp.id
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output staticWebAppName string = staticWebApp.name
