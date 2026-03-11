locals {
  name                   = "${var.project_name}-${var.environment}"
  tags                   = { Project = var.project_name, Environment = var.environment }
  https_enabled          = var.domain_name != ""
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

# ── Target Groups ─────────────────────────────────────────────────────────────

# Backend: FastAPI on :8000
resource "aws_lb_target_group" "backend" {
  name        = "${local.name}-api"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = var.health_check_path
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }

  tags = local.tags
}

# Frontend: Next.js on :3000
resource "aws_lb_target_group" "frontend" {
  name        = "${local.name}-web"
  port        = var.frontend_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200-399"
  }

  tags = local.tags
}

# ── HTTP listener — redirect to HTTPS when domain is set, else forward ────────

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
      target_group_arn = aws_lb_target_group.frontend.arn
    }
  }
}

# ── ACM certificate + DNS validation ─────────────────────────────────────────

resource "aws_acm_certificate" "app" {
  count             = local.https_enabled ? 1 : 0
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

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

# ── Route 53 A record — subdomain → ALB ───────────────────────────────────────

resource "aws_route53_record" "app" {
  count   = local.dns_validation_enabled ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.this.dns_name
    zone_id                = aws_lb.this.zone_id
    evaluate_target_health = true
  }
}

# ── HTTPS listener with path-based routing ────────────────────────────────────

resource "aws_lb_listener" "https" {
  count             = local.https_enabled ? 1 : 0
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.app[0].arn

  # Default: all traffic → Next.js frontend
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  depends_on = [aws_acm_certificate_validation.app]
}

# Route /api/v1/* → FastAPI backend
resource "aws_lb_listener_rule" "backend_api" {
  count        = local.https_enabled ? 1 : 0
  listener_arn = aws_lb_listener.https[0].arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/*"]
    }
  }
}
