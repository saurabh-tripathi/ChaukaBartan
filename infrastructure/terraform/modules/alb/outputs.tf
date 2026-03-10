output "target_group_arn"    { value = aws_lb_target_group.app.arn }
output "alb_dns_name"        { value = aws_lb.this.dns_name }
output "alb_arn"             { value = aws_lb.this.arn }
output "acm_certificate_arn" { value = length(aws_acm_certificate.app) > 0 ? aws_acm_certificate.app[0].arn : "" }
