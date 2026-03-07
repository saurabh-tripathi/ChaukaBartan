locals {
  name        = "${var.project_name}-${var.environment}"
  tags        = { Project = var.project_name, Environment = var.environment }
  https_enabled = var.domain_name != ""
  dns_validation_enabled = var.domain_name != "" && var.hosted_zone_id != ""
}

# ── Load Balancer ─────────────────────────────────────────────────────────────

resource "aws_lb" "this" {
  name               = local.name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = var.subnet_ids
  tags               = local.tags
}

resource "aws_lb_target_group" "app" {
  name        = local.name
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"  # required for Fargate (awsvpc networking)

  health_check {
    path                = var.health_check_path
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }

  tags = local.tags
}

# ── HTTP listener — forwards when HTTPS is off, redirects when HTTPS is on ────

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  dynamic "default_action" {
    for_each = local.https_enabled ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }

  dynamic "default_action" {
    for_each = local.https_enabled ? [] : [1]
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.app.arn
    }
  }
}

# ── ACM certificate + DNS validation (conditional on domain_name) ─────────────

resource "aws_acm_certificate" "app" {
  count             = local.https_enabled ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = ["www.${var.domain_name}"]

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# Route 53 DNS validation records (conditional on hosted_zone_id also being set)
resource "aws_route53_record" "cert_validation" {
  for_each = local.dns_validation_enabled ? {
    for dvo in aws_acm_certificate.app[0].domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  } : {}

  zone_id = var.hosted_zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "app" {
  count           = local.dns_validation_enabled ? 1 : 0
  certificate_arn = aws_acm_certificate.app[0].arn
  validation_record_fqdns = [
    for r in aws_route53_record.cert_validation : r.fqdn
  ]
}

# ── HTTPS listener (conditional) ──────────────────────────────────────────────

resource "aws_lb_listener" "https" {
  count             = local.https_enabled ? 1 : 0
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.app[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }

  depends_on = [aws_acm_certificate_validation.app]
}
