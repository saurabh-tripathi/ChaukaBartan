output "zone_id" {
  value       = aws_route53_zone.root.zone_id
  description = "Route 53 hosted zone ID — pass to the alb module for ACM validation."
}

output "name_servers" {
  value       = aws_route53_zone.root.name_servers
  description = "Copy these 4 NS records into GoDaddy → gradnuclei.com → Nameservers → Custom DNS."
}
