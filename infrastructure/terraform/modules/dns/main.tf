# Route 53 hosted zone for the root domain.
# After `terraform apply`, copy the name_servers output into GoDaddy's
# "Nameservers" settings for gradnuclei.com (Custom DNS, all 4 NS records).

resource "aws_route53_zone" "root" {
  name = var.root_domain
  tags = { Name = var.root_domain }
}
