# tf/s3_cloudfront.tf
# Amazon S3 static website hosting and AWS CloudFront global edge distributions fronted by ACM SSL.

# S3 website hosting bucket
resource "aws_s3_bucket" "frontend" {
  bucket        = "open-emfer-v2-production-frontend-harvy"
  force_destroy = true # Cleans bucket completely on terraform destroy
}

resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html" # Graceful SPA redirect
  }
}

# Public read policy for Static Website bucket
resource "aws_s3_bucket_public_access_block" "public" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "read" {
  depends_on = [aws_s3_bucket_public_access_block.public]
  bucket     = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# CloudFront edge cache distribution fronting S3 website origin (Path B)
resource "aws_cloudfront_distribution" "cdn" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.website.website_endpoint
    origin_id   = "S3WebsiteOrigin"

    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_protocol_policy   = "http-only" # S3 website endpoints do not support HTTPS directly
      origin_ssl_protocols     = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = [var.domain_name] # Custom CNAME alias bound in AWS (Path B)

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3WebsiteOrigin"

    forwarded_values {
      query_string = true
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 15 # Short 15s edge caching to absorb polling traffic (FR-015)
    max_ttl                = 60
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Bind your custom AWS ACM SSL Certificate directly to CloudFront (Path B)
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cert.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}
