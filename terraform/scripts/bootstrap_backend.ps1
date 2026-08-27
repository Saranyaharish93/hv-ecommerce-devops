<#
.SYNOPSIS
    Bootstraps the S3 Bucket for Terraform Native Remote State & Locking.
#>

$BUCKET_NAME = "lumora-ecommerce-prod-tfstate-us-east-1"
$REGION      = "us-east-1"

Write-Host "==> Checking if S3 Bucket '$BUCKET_NAME' exists..." -ForegroundColor Cyan
$bucketCheck = aws s3api head-bucket --bucket $BUCKET_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating S3 bucket '$BUCKET_NAME' in $REGION..." -ForegroundColor Yellow
    aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION
    
    Write-Host "Enabling versioning on S3 bucket..." -ForegroundColor Yellow
    aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled

    Write-Host "Enabling default encryption (AES256)..." -ForegroundColor Yellow
    aws s3api put-bucket-encryption --bucket $BUCKET_NAME --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}'

    Write-Host "Blocking all public access on S3 bucket..." -ForegroundColor Yellow
    aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    Write-Host "✅ S3 Bucket created successfully with native locking support!" -ForegroundColor Green
} else {
    Write-Host "✅ S3 Bucket '$BUCKET_NAME' already exists." -ForegroundColor Green
}

Write-Host "`n🎉 S3 Remote State Backend is ready! You can now run 'terraform init'." -ForegroundColor Green