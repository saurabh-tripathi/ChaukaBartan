output "cluster_name"          { value = aws_ecs_cluster.this.name }
output "cluster_arn"           { value = aws_ecs_cluster.this.arn }
output "service_name"          { value = aws_ecs_service.app.name }
output "task_execution_role_arn" { value = aws_iam_role.execution.arn }
output "log_group_name"        { value = aws_cloudwatch_log_group.app.name }
