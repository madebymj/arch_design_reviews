targetScope = 'resourceGroup'

module freeSearch 'br/public:avm/res/search/search-service:0.9.2' = {
  name: 'architecture-review-free-search-test'
  params: {
    name: 'archdesignreview-free-test'
    location: 'westeurope'
    sku: 'free'
    replicaCount: 1
    partitionCount: 1
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    semanticSearch: 'free'
    enableTelemetry: false
    tags: {
      purpose: 'isolated-architecture-review-free-tier-test'
    }
  }
}
