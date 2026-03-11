output "backend_target_group_arn"  { value = aws_lb_target_group.backend.arn }
output "frontend_target_group_arn" { value = aws_lb_target_group.frontend.arn }
output "alb_dns_name"              { value = aws_lb.this.dns_name }
output "alb_zone_id"               { value = aws_lb.this.zone_id }
output "alb_arn"                   { value = aws_lb.this.arn }
output "acm_certificate_arn"       { value = length(aws_acm_certificate.app) > 0 ? aws_acm_certificate.app[0].arn : "" }

# Kept for backwards-compat (old name was target_group_arn → backend)
output "target_group_arn" { value = aws_lb_target_group.backend.arn }
