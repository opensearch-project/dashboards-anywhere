#
# VPC Resources
#  * VPC
#  * Subnets
#  * Internet Gateway
#  * Route Table
#

# cidr_block was based on RFC 1918 and below two articles.
# https://docs.aws.amazon.com/vpc/latest/userguide/configure-your-vpc.html
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc
resource "aws_vpc" "playground-prod" {
  cidr_block = "10.0.0.0/16"

  tags = tomap({
    "Name"                                      = "playground-prod-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_subnet" "playground-prod" {
  count = 2

  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.playground-prod.id

  tags = tomap({
    "Name"                                      = "playground-prod-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_internet_gateway" "playground-prod" {
  vpc_id = aws_vpc.playground-prod.id

  tags = {
    Name = "playground-prod"
  }
}

resource "aws_route_table" "playground-prod" {
  vpc_id = aws_vpc.playground-prod.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.playground-prod.id
  }
}

resource "aws_route_table_association" "playground-prod" {
  count = 2

  subnet_id      = aws_subnet.playground-prod.*.id[count.index]
  route_table_id = aws_route_table.playground-prod.id
}
