@description('Short lowercase prefix used for Azure resource names.')
param prefix string = 'invoice-risk'

@description('Azure region for the API resources.')
param location string = resourceGroup().location

@description('Immutable container image reference, preferably pinned to a digest.')
param containerImage string

@description('Name of an existing Azure Container Registry in this resource group.')
param containerRegistryName string

@description('Published Foundry Agent Application endpoint ending in /protocols/openai.')
param foundryAgentEndpoint string

param foundryApiVersion string = '2025-11-15-preview'
param allowedOrigins string = ''
param minReplicas int = 2
param maxReplicas int = 10

@description('Client ID of the Entra app registration representing this API.')
param entraClientId string

@description('Microsoft Entra tenant ID.')
param tenantId string

@description('Accepted API audience configured on the Entra app registration.')
param entraAllowedAudience string = 'api://${entraClientId}'

var suffix = uniqueString(resourceGroup().id)
var appName = '${prefix}-api-${suffix}'

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs-${suffix}'
  location: location
  properties: {
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-appi-${suffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-identity-${suffix}'
  location: location
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, identity.id, 'acrpull')
  scope: registry
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    )
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-env-${suffix}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        transport: 'auto'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: containerImage
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          env: [
            {
              name: 'FOUNDRY_AGENT_ENDPOINT'
              value: foundryAgentEndpoint
            }
            {
              name: 'FOUNDRY_API_VERSION'
              value: foundryApiVersion
            }
            {
              name: 'AUTH_MODE'
              value: 'entra'
            }
            {
              name: 'ALLOWED_ORIGINS'
              value: allowedOrigins
            }
            {
              name: 'MAX_CONCURRENT_FOUNDRY_CALLS'
              value: '20'
            }
            {
              name: 'QUEUE_TIMEOUT_SECONDS'
              value: '10'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: insights.properties.ConnectionString
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health/live'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health/ready'
                port: 8000
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
  dependsOn: [
    acrPull
  ]
}

resource auth 'Microsoft.App/containerApps/authConfigs@2024-03-01' = {
  parent: api
  name: 'current'
  properties: {
    platform: {
      enabled: true
    }
    globalValidation: {
      unauthenticatedClientAction: 'Return401'
    }
    identityProviders: {
      azureActiveDirectory: {
        enabled: true
        registration: {
          clientId: entraClientId
          openIdIssuer: 'https://login.microsoftonline.com/${tenantId}/v2.0'
        }
        validation: {
          allowedAudiences: [
            entraAllowedAudience
          ]
        }
      }
    }
  }
}

output apiName string = api.name
output apiUrl string = 'https://${api.properties.configuration.ingress.fqdn}'
output managedIdentityPrincipalId string = identity.properties.principalId
