param location string = resourceGroup().location
param appName string = 'llm-beeldbeschrijver'
param containerImage string
param containerPort int = 8000
param cpu string = '0.5'
param memory string = '1.0Gi'
param maxReplicas int = 3

param openAiName string = '${appName}-openai'
param openAiSku string = 'S0'
param openAiDeploymentName string = 'gpt-4o'
param openAiModelName string = 'gpt-4o'
param openAiModelVersion string = '2024-08-06'
param existingOpenAiName string = ''
param existingOpenAiResourceGroup string = ''
param existingOpenAiDeploymentName string = 'gpt-4o'

// Azure AI Foundry serverless endpoint (bijv. Llama)
param azureInferenceEndpoint string = ''
@secure()
param azureInferenceApiKey string = ''
param azureInferenceDeployment string = ''


param envName string = '${appName}-env'
param logAnalyticsName string = '${appName}-logs'
param existingManagedEnvId string = ''
param acrName string = ''

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (existingManagedEnvId == '') {
	name: logAnalyticsName
	location: location
	properties: {
		sku: {
			name: 'PerGB2018'
		}
		retentionInDays: 30
	}
}

resource managedEnv 'Microsoft.App/managedEnvironments@2023-05-01' = if (existingManagedEnvId == '') {
	name: envName
	location: location
	properties: {
		appLogsConfiguration: {
			destination: 'log-analytics'
			logAnalyticsConfiguration: {
				#disable-next-line BCP318
				customerId: logAnalytics.properties.customerId
				#disable-next-line BCP318
				sharedKey: listKeys(logAnalytics.id, '2020-08-01').primarySharedKey
			}
		}
	}
}

var managedEnvId = existingManagedEnvId != '' ? existingManagedEnvId : managedEnv.id

var usingExistingOpenAi = existingOpenAiName != '' && existingOpenAiResourceGroup != ''

resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' = if (!usingExistingOpenAi) {
	name: openAiName
	location: location
	kind: 'OpenAI'
	sku: {
		name: openAiSku
	}
	properties: {
		customSubDomainName: openAiName
		publicNetworkAccess: 'Enabled'
	}
}

resource existingOpenAi 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = if (existingOpenAiName != '' && existingOpenAiResourceGroup != '') {
	name: existingOpenAiName
	scope: resourceGroup(existingOpenAiResourceGroup)
}

resource openAiDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = if (!usingExistingOpenAi) {
	name: openAiDeploymentName
	parent: openAi
	sku: {
		name: 'Standard'
		capacity: 1
	}
	properties: {
		model: {
			format: 'OpenAI'
			name: openAiModelName
			version: openAiModelVersion
		}
	}
}

#disable-next-line BCP318
var openAiId = usingExistingOpenAi ? existingOpenAi.id : openAi.id
#disable-next-line BCP318
var openAiEndpoint = usingExistingOpenAi ? existingOpenAi.properties.endpoint : openAi.properties.endpoint
var openAiDeploymentForApp = usingExistingOpenAi ? existingOpenAiDeploymentName : openAiDeploymentName

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
	name: appName
	location: location
	properties: {
		managedEnvironmentId: managedEnvId
		configuration: {
			registries: acrName != '' ? [
				{
					server: '${acrName}.azurecr.io'
					#disable-next-line BCP318
					username: listCredentials(acrResource.id, '2023-01-01-preview').username
					passwordSecretRef: 'acr-password'
				}
			] : []
			secrets: concat(
				[
					{
						name: 'azure-openai-key'
						value: listKeys(openAiId, '2023-05-01').key1
					}
				],
				acrName != '' ? [
					{
						name: 'acr-password'
						#disable-next-line BCP318
						value: listCredentials(acrResource.id, '2023-01-01-preview').passwords[0].value
					}
				] : [],
				azureInferenceApiKey != '' ? [
					{
						name: 'azure-inference-key'
						value: azureInferenceApiKey
					}
				] : []
			)
			ingress: {
				external: true
				targetPort: containerPort
			}
		}
		template: {
			containers: [
				{
					name: 'api'
					image: containerImage
					resources: {
						cpu: json(cpu)
						memory: memory
					}
					env: concat(
						[
							{
								name: 'AZURE_OPENAI_ENDPOINT'
								value: openAiEndpoint
							}
							{
								name: 'AZURE_OPENAI_API_KEY'
								secretRef: 'azure-openai-key'
							}
							{
								name: 'AZURE_OPENAI_DEPLOYMENT'
								value: openAiDeploymentForApp
							}
							{
								name: 'AZURE_OPENAI_API_VERSION'
								value: '2024-06-01'
							}
						],
						azureInferenceEndpoint != '' ? [
							{
								name: 'AZURE_INFERENCE_ENDPOINT'
								value: azureInferenceEndpoint
							}
							{
								name: 'AZURE_INFERENCE_API_KEY'
								secretRef: 'azure-inference-key'
							}
							{
								name: 'AZURE_INFERENCE_DEPLOYMENT'
								value: azureInferenceDeployment
							}
						] : []
					)
				}
			]
			scale: {
				minReplicas: 0
				maxReplicas: maxReplicas
			}
		}
	}
}

resource acrResource 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = if (acrName != '') {
	name: acrName
}

output containerAppUrl string = containerApp.properties.configuration.ingress.fqdn
output openAiEndpoint string = openAiEndpoint
