# MISO Deployment Script (v2.1 - Final for v1.0.0)
# This script automates the process of updating the ECS service with a new image.

# --- Configuration ---
$clusterName = "miso-cluster"
$serviceName = "discovery-interview-service"
$taskFamily = "discovery-interview"
$newImageUri = "356206423360.dkr.ecr.us-east-1.amazonaws.com/miso/discovery-interview:1.0.0"

# --- Script Body ---
Write-Host "Starting deployment process for $serviceName..."

# 1. Get the latest active task definition object
Write-Host "Fetching latest task definition for family: $taskFamily..."
$taskDef = (aws ecs describe-task-definition --task-definition $taskFamily | ConvertFrom-Json).taskDefinition
if (-not $taskDef) {
    Write-Error "Failed to fetch task definition. Aborting."
    exit 1
}

# 2. Update the image URI directly on the container definition object
Write-Host "Updating image URI to: $newImageUri"
$taskDef.containerDefinitions[0].image = $newImageUri

# 3. Remove output-only fields that are invalid for a new registration
$taskDef.psobject.Properties.Remove('taskDefinitionArn')
$taskDef.psobject.Properties.Remove('revision')
$taskDef.psobject.Properties.Remove('status')
$taskDef.psobject.Properties.Remove('requiresAttributes')
$taskDef.psobject.Properties.Remove('compatibilities')
$taskDef.psobject.Properties.Remove('registeredAt')
$taskDef.psobject.Properties.Remove('registeredBy')
$taskDef.psobject.Properties.Remove('deregisteredAt')

# 4. Convert the modified object to JSON and save to a temporary file for reliability
$newRevisionJson = $taskDef | ConvertTo-Json -Depth 10
$tempJsonFile = ".\temp-task-def.json"
$newRevisionJson | Set-Content -Path $tempJsonFile

# 5. Register the new task definition revision from the file
Write-Host "Registering new task definition revision..."
$registerResult = aws ecs register-task-definition --cli-input-json "file://$tempJsonFile" | ConvertFrom-Json
$newRevisionArn = $registerResult.taskDefinition.taskDefinitionArn

# 6. Clean up the temporary file
Remove-Item $tempJsonFile

if (-not $newRevisionArn) {
    Write-Error "Failed to register new task definition. Aborting."
    exit 1
}
Write-Host "Successfully registered new task definition: $newRevisionArn"

# 7. Update the service to use the new revision and force deployment
Write-Host "Updating service $serviceName to use new task definition..."
aws ecs update-service --cluster $clusterName --service $serviceName --task-definition $newRevisionArn --force-new-deployment
Write-Host ""
Write-Host "SUCCESS: Service update initiated."
Write-Host "Monitor the 'Health' tab in the ECS console. The new task should become Healthy within a few minutes."
