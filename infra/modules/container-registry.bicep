// Azure Container Registry

@description('Base name for resources')
param baseName string

@description('Location for resources')
param location string

@description('Unique suffix for globally unique names')
param uniqueSuffix string

@description('Tags to apply to resources')
param tags object

var acrName = 'acr${replace(baseName, '-', '')}${uniqueSuffix}'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: take(acrName, 50)
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

output acrId string = containerRegistry.id
output acrLoginServer string = containerRegistry.properties.loginServer
output acrName string = containerRegistry.name
