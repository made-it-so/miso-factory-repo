# MISO Deployment Script (v5 - Final Port Fix)

# --- Configuration ---
$clusterName = "miso-cluster"
$serviceName = "discovery-interview-service"
$taskFamily = "discovery-interview"
$subnets = @("subnet-0d5b8687b028ef1ac", "subnet-01df846c12e725654", "subnet-08b99fdefac81424e", "subnet-02832ec949ebf1994", "subnet-065eb180fb19e1e36", "subnet-0faca65ba8ae5f3e4")
$securityGroup = "sg-0cfdce2e9a10667ef"
$targetGroupArn = "arn:aws:elasticloadbalancing:us-east-1:356206423360:targetgroup/miso-discovery-interview-tg/ddf01d06ec9b07fe"

# --- Script Body ---
Write-Host "Starting definitive deployment for $serviceName..."

# 1. Get latest task definition ARN
$latestTaskDef = aws ecs describe-task-definition --task-definition $taskFamily | ConvertFrom-Json
$taskDefArn = $latestTaskDef.taskDefinition.taskDefinitionArn
Write-Host "Using latest task definition: $taskDefArn"

# 2. Delete the old, misconfigured service
Write-Host "Deleting old service..."
aws ecs update-service --cluster $clusterName --service $serviceName --desired-count 0 > $null
Start-Sleep -Seconds 30
aws ecs delete-service --cluster $clusterName --service $serviceName --force > $null
Write-Host "Old service deleted."

# 3. Create the new, correctly configured service
Write-Host "Creating new service with correct network configuration..."
aws ecs create-service --cluster $clusterName --service-name $serviceName --task-definition $taskDefArn --desired-count 1 --launch-type "FARGATE" --network-configuration "awsvpcConfiguration={subnets=[`"$($subnets -join '`,`"')`],securityGroups=[`"$securityGroup`],assignPublicIp=DISABLED}" --load-balancers "targetGroupArn=$targetGroupArn,containerName=discovery-interview-container,containerPort=80" --health-check-grace-period-seconds 60

Write-Host ""
Write-Host "SUCCESS: Definitive deployment complete."
Write-Host "Monitor the 'Health' tab in the ECS console. The service will become Healthy."
